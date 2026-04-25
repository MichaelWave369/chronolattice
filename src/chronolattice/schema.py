from __future__ import annotations

from .compat import is_supported_schema_version


def require_fields(data: dict, fields: list[str], context: str) -> list[str]:
    if not isinstance(data, dict):
        return [f"{context} must be an object."]
    missing = [name for name in fields if name not in data]
    return [f"{context} missing required field: {name}" for name in missing]


def validate_artifact_envelope(data: dict, expected_kind: str) -> list[str]:
    errors = require_fields(data, ["kind", "schema_version", "payload"], "artifact")
    if errors:
        return errors
    if data.get("kind") != expected_kind:
        errors.append(f"artifact kind mismatch: expected {expected_kind}")
    if not is_supported_schema_version(data.get("schema_version")):
        errors.append(f"artifact unsupported schema_version: {data.get('schema_version')}")
    if not isinstance(data.get("payload"), dict):
        errors.append("artifact payload must be an object")
    return errors


def validate_event_dict(data: dict) -> list[str]:
    required = [
        "event_id",
        "timestamp",
        "sequence_index",
        "actor",
        "event_type",
        "spatial_ref",
        "energy_delta",
        "information_value",
        "memory_refs",
        "coherence",
        "payload_hash",
        "provenance",
    ]
    return require_fields(data, required, "event")


def validate_reconstruction_dict(data: dict) -> list[str]:
    required = [
        "run_id",
        "input_hash",
        "reconstruction_hash",
        "events",
        "causal_edges",
        "memory_edges",
        "geometry_edges",
        "contradictions",
        "entropy_score",
        "information_score",
        "coherence",
        "stable",
        "seed",
    ]
    errors = require_fields(data, required, "reconstruction")
    if errors:
        return errors

    events = data.get("events")
    if not isinstance(events, list):
        errors.append("reconstruction.events must be a list")
        return errors

    for idx, event in enumerate(events):
        for err in validate_event_dict(event):
            errors.append(f"reconstruction.events[{idx}]: {err}")
    return errors


def validate_receipt_dict(data: dict) -> list[str]:
    required = [
        "receipt_id",
        "run_id",
        "input_hash",
        "reconstruction_hash",
        "event_count",
        "causal_edges",
        "memory_edges",
        "geometry_edges",
        "coherence",
        "stable",
        "entropy_score",
        "contradiction_count",
        "selected_model",
        "seed",
        "created_at",
    ]
    return require_fields(data, required, "receipt")


def is_legacy_reconstruction_dict(data: dict) -> bool:
    return validate_reconstruction_dict(data) == []


def is_legacy_receipt_dict(data: dict) -> bool:
    return validate_receipt_dict(data) == []
