"""Persistent JSON storage for completed formula calculations.

This module deliberately has no terminal or diagram-generation behavior.  It
stores a calculation record after a caller has already obtained its inputs and
results from the formula service.
"""

from __future__ import annotations

import json
import math
import os
import tempfile
from pathlib import Path
from typing import TypeAlias


JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
CalculationRecord: TypeAlias = dict[str, JsonValue]

SCHEMA_VERSION = 1
_COLLECTION_KEYS = {"schema_version", "calculations"}
_RECORD_KEYS = {
    "formula_option",
    "formula_name",
    "inputs",
    "results",
    "diagram_path",
}


class StorageFormatError(ValueError):
    """Raised when an existing storage file is not a supported collection."""


def load_calculations(file_path: str | Path) -> list[CalculationRecord]:
    """Load saved calculation records from ``file_path``.

    Args:
        file_path: JSON collection location. A missing or empty file is read as
            an empty collection and is left untouched.

    Returns:
        A new list containing the validated saved records.

    Raises:
        StorageFormatError: If the file contains malformed JSON or a structure
            that does not match schema version 1.
        OSError: If the file cannot be read.
    """
    return _read_collection(Path(file_path))["calculations"]


def append_calculation(
    file_path: str | Path,
    formula_option: str,
    formula_name: str,
    inputs: dict[str, JsonValue],
    results: dict[str, JsonValue],
    diagram_path: str | Path | None = None,
) -> CalculationRecord:
    """Append one formula calculation to a JSON collection atomically.

    Args:
        file_path: JSON collection location to create or update.
        formula_option: Selected option from ``formula_service.FORMULAS``.
        formula_name: Display name paired with the selected option.
        inputs: Validated formula inputs to preserve with the calculation.
        results: Results returned by the existing formula service.
        diagram_path: Optional relative reference to an existing diagram.

    Returns:
        A copy of the record written to disk.

    Raises:
        StorageFormatError: If existing storage is malformed or incompatible.
        TypeError: If a supplied value is not JSON-compatible.
        ValueError: If a number is non-finite or the diagram path is absolute.
        OSError: If an atomic write cannot be completed.
    """
    record = _build_record(
        formula_option,
        formula_name,
        inputs,
        results,
        diagram_path,
    )
    collection = _read_collection(Path(file_path))
    collection["calculations"].append(record)
    _write_collection(Path(file_path), collection)
    return _copy_json_value(record)


def _empty_collection() -> dict[str, JsonValue]:
    return {"schema_version": SCHEMA_VERSION, "calculations": []}


def _read_collection(file_path: Path) -> dict[str, JsonValue]:
    """Read and validate a collection without creating a missing file."""
    try:
        text = file_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _empty_collection()

    # An empty file is intentionally treated like an empty collection. Reading
    # must not turn it into a JSON file until a caller explicitly appends data.
    if not text.strip():
        return _empty_collection()

    try:
        raw_collection = json.loads(text)
    except json.JSONDecodeError as error:
        raise StorageFormatError("Storage file contains invalid JSON.") from error

    return _validate_collection(raw_collection)


def _validate_collection(value: object) -> dict[str, JsonValue]:
    if not isinstance(value, dict) or set(value) != _COLLECTION_KEYS:
        raise StorageFormatError(
            "Storage file must contain schema_version and calculations."
        )
    if value["schema_version"] != SCHEMA_VERSION or isinstance(
        value["schema_version"], bool
    ):
        raise StorageFormatError("Storage file has an unsupported schema_version.")
    if not isinstance(value["calculations"], list):
        raise StorageFormatError("Storage file calculations must be a list.")

    records: list[JsonValue] = []
    for record in value["calculations"]:
        records.append(_validate_record(record))
    return {"schema_version": SCHEMA_VERSION, "calculations": records}


def _build_record(
    formula_option: str,
    formula_name: str,
    inputs: dict[str, JsonValue],
    results: dict[str, JsonValue],
    diagram_path: str | Path | None,
) -> CalculationRecord:
    record: dict[str, object] = {
        "formula_option": formula_option,
        "formula_name": formula_name,
        "inputs": inputs,
        "results": results,
        "diagram_path": _normalize_diagram_path(diagram_path),
    }
    return _validate_record(record)


def _validate_record(value: object) -> CalculationRecord:
    if not isinstance(value, dict) or set(value) != _RECORD_KEYS:
        raise StorageFormatError("Each calculation must contain the required fields.")
    if not isinstance(value["formula_option"], str) or not value["formula_option"]:
        raise StorageFormatError("formula_option must be a non-empty string.")
    if not isinstance(value["formula_name"], str) or not value["formula_name"]:
        raise StorageFormatError("formula_name must be a non-empty string.")
    if not isinstance(value["inputs"], dict) or not isinstance(value["results"], dict):
        raise StorageFormatError("inputs and results must be JSON objects.")

    stored_diagram_path = value["diagram_path"]
    if stored_diagram_path is not None:
        if not isinstance(stored_diagram_path, str) or not stored_diagram_path:
            raise StorageFormatError("diagram_path must be a relative string or null.")
        if Path(stored_diagram_path).is_absolute():
            raise StorageFormatError("diagram_path must be relative.")

    return {
        "formula_option": value["formula_option"],
        "formula_name": value["formula_name"],
        "inputs": _copy_json_value(value["inputs"]),
        "results": _copy_json_value(value["results"]),
        "diagram_path": stored_diagram_path,
    }


def _normalize_diagram_path(diagram_path: str | Path | None) -> str | None:
    if diagram_path is None:
        return None
    stored_path = str(diagram_path)
    relative_path = Path(stored_path)
    if not stored_path or relative_path.is_absolute():
        raise ValueError("diagram_path must be a non-empty relative path.")
    return stored_path


def _copy_json_value(value: object) -> JsonValue:
    """Validate JSON compatibility while creating an independent value copy."""
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("JSON numbers must be finite.")
        return value
    if isinstance(value, list):
        return [_copy_json_value(item) for item in value]
    if isinstance(value, dict):
        copied: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError("JSON object keys must be strings.")
            copied[key] = _copy_json_value(item)
        return copied
    raise TypeError(f"Value of type {type(value).__name__} is not JSON-compatible.")


def _write_collection(file_path: Path, collection: dict[str, JsonValue]) -> None:
    """Write a validated collection through a temporary sibling file."""
    temporary_path: Path | None = None
    try:
        # A sibling temporary file lets os.replace perform an atomic replacement
        # on one filesystem. Closing it before replacement is required on Windows.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(collection, temporary_file, ensure_ascii=False, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, file_path)
    except (OSError, TypeError, ValueError):
        # Replacement has not happened on failure, so the prior storage remains.
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
        raise
