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
    circuit: dict[str, Any],
    results: dict[str, Any],
    source_image: str | Path,
) -> dict[str, Any]:
    """Save a circuit, its calculated results, and a private diagram copy.

    The image is copied before the JSON is atomically replaced.  If that JSON
    write fails, only the copy created by this call is removed; earlier records
    and images are never changed.
    """
    collection_path = Path(storage_path)
    snapshot = _json_copy(circuit)
    calculation = _json_copy(results)
    if not isinstance(snapshot, dict) or not isinstance(calculation, dict):
        raise CircuitStorageError("Circuit and results must be JSON objects.")
    collection = _read_collection(collection_path)
    image_source = _validate_source_image(Path(source_image))

    circuit_id = circuit_identity(snapshot)
    image_directory = collection_path.parent / "saved_circuit_images"
    image_directory.mkdir(parents=True, exist_ok=True)
    image_name = f"circuit-{circuit_id[:12]}-{uuid.uuid4().hex}.png"
    image_destination = image_directory / image_name
    relative_image_path = image_destination.relative_to(collection_path.parent).as_posix()
    record = {
        "circuit_id": circuit_id,
        "circuit": snapshot,
        "results": calculation,
        "diagram_path": relative_image_path,
    }

    copied_image = False
    try:
        _copy_image_exclusively(image_source, image_destination)
        copied_image = True
        collection["circuits"].append(record)
        _write_collection(collection_path, collection)
    except Exception:
        if copied_image:
            try:
                image_destination.unlink()
            except FileNotFoundError:
                pass
        raise
    return _json_copy(record)


def load_circuits(file_path: str | Path) -> list[dict[str, Any]]:
    """Load circuit records without resolving their relative image references."""
    return _read_collection(Path(file_path))["circuits"]


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
    records = [_validate_record(record) for record in value["circuits"]]
    return {"schema_version": SCHEMA_VERSION, "circuits": records}


def _validate_record(record: object) -> dict[str, Any]:
    if not isinstance(record, dict) or set(record) != {
        "circuit_id", "circuit", "results", "diagram_path"
    }:
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
    return {"circuit_id": record["circuit_id"], "circuit": circuit,
            "results": results, "diagram_path": record["diagram_path"]}


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
