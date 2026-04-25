from __future__ import annotations


def require_fields(data: dict, fields: list[str], context: str) -> list[str]:
    if not isinstance(data, dict):
        return [f"{context} must be an object."]
    missing = [name for name in fields if name not in data]
    return [f"{context} missing required field: {name}" for name in missing]


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
