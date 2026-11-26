"""Durable storage for a circuit snapshot and its rendered diagram.

Saved ``diagram_path`` values are always relative to the directory containing
the JSON collection.  This makes a saved collection portable as long as its
image directory moves with it.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
_SUPPORTED_IMAGE_SIGNATURES = {".png": b"\x89PNG\r\n\x1a\n"}


class CircuitStorageError(ValueError):
    """Raised when circuit storage input or an existing collection is invalid."""


def circuit_identity(circuit: dict[str, Any]) -> str:
    """Return a stable content identity for a JSON-compatible circuit snapshot."""
    copied = _json_copy(circuit)
    if not isinstance(copied, dict):
        raise CircuitStorageError("Circuit data must be a JSON object.")
    encoded = json.dumps(copied, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def save_circuit(
    storage_path: str | Path,
    circuit_name: str,
    circuit: dict[str, Any],
    results: dict[str, Any],
    source_image: str | Path,
    editor_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Save a named circuit as a new document and copy its current diagram.

    The image is copied before the JSON is atomically replaced.  If that JSON
    write fails, only the copy created by this call is removed; earlier records
    and images are never changed.
    """
    name = _normalise_name(circuit_name)
    snapshot, calculation, state = _prepare_snapshot(circuit, results, editor_state)
    record = _new_record(name, snapshot, calculation, state)
    collection_path = Path(storage_path)
    collection = _read_collection(collection_path)
    return _persist_record(
        collection_path, collection, record, Path(source_image), append=True
    )


def update_circuit(
    storage_path: str | Path,
    record_id: str,
    circuit: dict[str, Any],
    results: dict[str, Any],
    source_image: str | Path,
    editor_state: dict[str, Any] | None = None,
    circuit_name: str | None = None,
) -> dict[str, Any]:
    """Replace one saved document while retaining its stable ``record_id``.

    A fresh image copy and a complete JSON document are written before the old
    record is replaced.  Previous image files are intentionally retained, so a
    failed update cannot destroy the image referenced by the old record.
    """
    collection_path = Path(storage_path)
    collection = _read_collection(collection_path)
    index = _find_record_index(collection["circuits"], record_id)
    if index is None:
        raise CircuitStorageError("Saved circuit was not found.")
    existing = collection["circuits"][index]
    name = existing["circuit_name"] if circuit_name is None else _normalise_name(circuit_name)
    snapshot, calculation, state = _prepare_snapshot(circuit, results, editor_state)
    record = _new_record(name, snapshot, calculation, state, record_id=record_id)
    return _persist_record(
        collection_path, collection, record, Path(source_image), append=False, index=index
    )


def load_circuits(file_path: str | Path) -> list[dict[str, Any]]:
    """Load circuit records without resolving their relative image references."""
    return _read_collection(Path(file_path))["circuits"]


def list_circuits(file_path: str | Path) -> list[dict[str, Any]]:
    """Return safe metadata for selector UIs without exposing circuit payloads."""
    collection_path = Path(file_path)
    records = _read_collection(collection_path)["circuits"]
    return [
        {
            "record_id": record["record_id"],
            "circuit_name": record["circuit_name"],
            "circuit_id": record["circuit_id"],
            "diagram_path": record["diagram_path"],
            "image_available": resolve_diagram_path(collection_path, record).is_file(),
        }
        for record in records
    ]


def get_circuit(file_path: str | Path, record_id: str) -> dict[str, Any] | None:
    """Return one validated document by its stable ID, or ``None`` if absent."""
    records = _read_collection(Path(file_path))["circuits"]
    index = _find_record_index(records, record_id)
    return None if index is None else _json_copy(records[index])


def resolve_diagram_path(storage_path: str | Path, record: dict[str, Any]) -> Path:
    """Resolve a record's image path relative to its collection JSON file."""
    path = record.get("diagram_path")
    if not isinstance(path, str) or not path:
        raise CircuitStorageError("Circuit record has no diagram path.")
    relative_path = Path(path)
    if relative_path.is_absolute():
        raise CircuitStorageError("diagram_path must be relative.")
    return Path(storage_path).parent / relative_path


def _empty_collection() -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "circuits": []}


def _read_collection(file_path: Path) -> dict[str, Any]:
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _empty_collection()
    if not text.strip():
        return _empty_collection()
    try:
        value = json.loads(text)
    except json.JSONDecodeError as error:
        raise CircuitStorageError("Circuit storage contains invalid JSON.") from error
    if not isinstance(value, dict) or set(value) != {"schema_version", "circuits"}:
        raise CircuitStorageError("Circuit storage must contain schema_version and circuits.")
    if value["schema_version"] != SCHEMA_VERSION or not isinstance(value["circuits"], list):
        raise CircuitStorageError("Circuit storage has an unsupported schema.")
    records = [_validate_record(record, index) for index, record in enumerate(value["circuits"])]
    return {"schema_version": SCHEMA_VERSION, "circuits": records}


def _validate_record(record: object, legacy_index: int) -> dict[str, Any]:
    legacy_fields = {"circuit_id", "circuit", "results", "diagram_path"}
    modern_fields = legacy_fields | {"record_id", "circuit_name", "editor_state"}
    if not isinstance(record, dict) or set(record) not in (legacy_fields, modern_fields):
        raise CircuitStorageError("Each circuit record has required fields missing.")
    if not isinstance(record["circuit_id"], str) or not record["circuit_id"]:
        raise CircuitStorageError("circuit_id must be a non-empty string.")
    if not isinstance(record["diagram_path"], str) or not record["diagram_path"]:
        raise CircuitStorageError("diagram_path must be a non-empty relative string.")
    if Path(record["diagram_path"]).is_absolute():
        raise CircuitStorageError("diagram_path must be relative.")
    circuit = _json_copy(record["circuit"])
    results = _json_copy(record["results"])
    if not isinstance(circuit, dict) or not isinstance(results, dict):
        raise CircuitStorageError("circuit and results must be JSON objects.")
    if record["circuit_id"] != circuit_identity(circuit):
        raise CircuitStorageError("circuit_id does not match the circuit snapshot.")
    if set(record) == legacy_fields:
        # Legacy records are accepted without touching disk. Their deterministic
        # IDs let callers load them; the next update rewrites them in new form.
        record_id = str(uuid.uuid5(
            uuid.NAMESPACE_URL, f"circuit-generator:legacy:{legacy_index}:{record['circuit_id']}"
        ))
        name = f"Untitled circuit {legacy_index + 1}"
        editor_state = _derive_editor_state(circuit)
    else:
        record_id = record["record_id"]
        if not isinstance(record_id, str) or not record_id:
            raise CircuitStorageError("record_id must be a non-empty string.")
        name = _normalise_name(record["circuit_name"])
        editor_state = _validate_editor_state(record["editor_state"], circuit)
    return {"record_id": record_id, "circuit_name": name,
            "circuit_id": record["circuit_id"], "circuit": circuit,
            "results": results, "editor_state": editor_state,
            "diagram_path": record["diagram_path"]}


def _normalise_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CircuitStorageError("circuit_name must be a non-empty string.")
    return value.strip()


def _prepare_snapshot(
    circuit: dict[str, Any],
    results: dict[str, Any],
    editor_state: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    snapshot = _json_copy(circuit)
    calculation = _json_copy(results)
    if not isinstance(snapshot, dict) or not isinstance(calculation, dict):
        raise CircuitStorageError("Circuit and results must be JSON objects.")
    state = _derive_editor_state(snapshot) if editor_state is None else _validate_editor_state(editor_state, snapshot)
    return snapshot, calculation, state


def _new_record(
    circuit_name: str,
    circuit: dict[str, Any],
    results: dict[str, Any],
    editor_state: dict[str, Any],
    record_id: str | None = None,
) -> dict[str, Any]:
    return {
        "record_id": str(uuid.uuid4()) if record_id is None else record_id,
        "circuit_name": circuit_name,
        "circuit_id": circuit_identity(circuit),
        "circuit": circuit,
        "results": results,
        "editor_state": editor_state,
        "diagram_path": "",
    }


def _persist_record(
    collection_path: Path,
    collection: dict[str, Any],
    record: dict[str, Any],
    source_image: Path,
    *,
    append: bool,
    index: int | None = None,
) -> dict[str, Any]:
    image_source = _validate_source_image(source_image)
    image_directory = collection_path.parent / "saved_circuit_images"
    image_directory.mkdir(parents=True, exist_ok=True)
    image_name = f"circuit-{record['circuit_id'][:12]}-{uuid.uuid4().hex}.png"
    image_destination = image_directory / image_name
    record["diagram_path"] = image_destination.relative_to(collection_path.parent).as_posix()

    copied_image = False
    try:
        _copy_image_exclusively(image_source, image_destination)
        copied_image = True
        if append:
            collection["circuits"].append(record)
        else:
            if index is None:
                raise RuntimeError("Update requires a record index.")
            collection["circuits"][index] = record
        _write_collection(collection_path, collection)
    except Exception:
        if copied_image:
            try:
                image_destination.unlink()
            except FileNotFoundError:
                pass
        raise
    return _json_copy(record)


def _find_record_index(records: list[dict[str, Any]], record_id: object) -> int | None:
    if not isinstance(record_id, str) or not record_id:
        return None
    for index, record in enumerate(records):
        if record["record_id"] == record_id:
            return index
    return None


def _derive_editor_state(circuit: dict[str, Any]) -> dict[str, Any]:
    nodes = _circuit_nodes(circuit)
    numbered = [int(match.group(1)) for node in nodes if (match := re.fullmatch(r"N(\d+)", node))]
    components = circuit.get("components")
    last_component = components[-1] if isinstance(components, list) and components else None
    last_node = last_component.get("to_node") if isinstance(last_component, dict) else None
    if not isinstance(last_node, str):
        source = circuit.get("source")
        last_node = source.get("to_node") if isinstance(source, dict) else None
    return {"next_node": max(numbered, default=-1) + 1, "last_node": last_node}


def _validate_editor_state(value: object, circuit: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"next_node", "last_node"}:
        raise CircuitStorageError("editor_state must contain next_node and last_node.")
    next_node = value["next_node"]
    last_node = value["last_node"]
    if isinstance(next_node, bool) or not isinstance(next_node, int) or next_node < 0:
        raise CircuitStorageError("editor_state.next_node must be a non-negative integer.")
    if last_node is not None and not isinstance(last_node, str):
        raise CircuitStorageError("editor_state.last_node must be a string or null.")
    nodes = _circuit_nodes(circuit)
    numbered = [int(match.group(1)) for node in nodes if (match := re.fullmatch(r"N(\d+)", node))]
    if next_node <= max(numbered, default=-1):
        raise CircuitStorageError("editor_state.next_node would reuse an existing node.")
    if last_node is not None and last_node not in nodes:
        raise CircuitStorageError("editor_state.last_node is not in the circuit.")
    return {"next_node": next_node, "last_node": last_node}


def _circuit_nodes(circuit: dict[str, Any]) -> set[str]:
    nodes: set[str] = set()
    components = circuit.get("components", [])
    if isinstance(components, list):
        for component in components:
            if isinstance(component, dict):
                for key in ("from_node", "to_node"):
                    if isinstance(component.get(key), str):
                        nodes.add(component[key])
    source = circuit.get("source")
    if isinstance(source, dict):
        for key in ("from_node", "to_node"):
            if isinstance(source.get(key), str):
                nodes.add(source[key])
    return nodes


def _validate_source_image(source: Path) -> Path:
    signature = _SUPPORTED_IMAGE_SIGNATURES.get(source.suffix.lower())
    if signature is None:
        raise CircuitStorageError("The current diagram is not a supported PNG image.")
    try:
        with source.open("rb") as image_file:
            if image_file.read(len(signature)) != signature:
                raise CircuitStorageError("The current diagram is not a valid PNG image.")
    except FileNotFoundError as error:
        raise CircuitStorageError(
            "No current diagram is available. Add or change a circuit part to generate it first."
        ) from error
    return source


def _copy_image_exclusively(source: Path, destination: Path) -> None:
    """Copy without ever replacing an existing saved image."""
    created_destination = False
    try:
        with source.open("rb") as source_file, destination.open("xb") as target_file:
            created_destination = True
            shutil.copyfileobj(source_file, target_file)
            target_file.flush()
            os.fsync(target_file.fileno())
    except Exception:
        if created_destination:
            try:
                destination.unlink()
            except FileNotFoundError:
                pass
        raise


def _json_copy(value: object) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CircuitStorageError("JSON numbers must be finite.")
        return value
    if isinstance(value, list):
        return [_json_copy(item) for item in value]
    if isinstance(value, dict):
        copied: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise CircuitStorageError("JSON object keys must be strings.")
            copied[key] = _json_copy(item)
        return copied
    raise CircuitStorageError(f"{type(value).__name__} is not JSON-compatible.")


def _write_collection(file_path: Path, collection: dict[str, Any]) -> None:
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=file_path.parent,
            prefix=f".{file_path.name}.", suffix=".tmp", delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(collection, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, file_path)
    except Exception:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
        raise
