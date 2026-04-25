from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from .compat import unwrap_artifact, wrap_artifact
from .constants import ARTIFACT_KIND_RECEIPT, ARTIFACT_KIND_RECONSTRUCTION, SCHEMA_VERSION
from .models import (
    CausalEdge,
    ChronoBridgeGap,
    ChronoContradiction,
    ChronoEvent,
    ChronoReceipt,
    ChronoReconstruction,
    GeometryEdge,
    MemoryEdge,
)
from .schema import validate_receipt_dict, validate_reconstruction_dict


def _require_or_raise(errors: list[str], context: str) -> None:
    if errors:
        raise ValueError(f"Invalid {context}: " + "; ".join(errors))


def reconstruction_to_dict(reconstruction: ChronoReconstruction) -> dict:
    payload = asdict(reconstruction)
    payload.setdefault("bridge_gaps", [])
    payload.setdefault("bridge_profile", "balanced")
    return wrap_artifact(ARTIFACT_KIND_RECONSTRUCTION, SCHEMA_VERSION, payload)


def reconstruction_from_dict(data: dict) -> ChronoReconstruction:
    payload = unwrap_artifact(dict(data), ARTIFACT_KIND_RECONSTRUCTION)
    payload = dict(payload)
    payload.setdefault("bridge_gaps", [])
    payload.setdefault("bridge_profile", "balanced")

    errors = validate_reconstruction_dict(payload)
    _require_or_raise(errors, "reconstruction")

    events = [ChronoEvent(**dict(item)) for item in payload["events"]]
    causal_edges = [CausalEdge(**dict(item)) for item in payload["causal_edges"]]
    memory_edges = [MemoryEdge(**dict(item)) for item in payload["memory_edges"]]
    geometry_edges = [GeometryEdge(**dict(item)) for item in payload["geometry_edges"]]
    contradictions = [ChronoContradiction(**dict(item)) for item in payload["contradictions"]]
    bridge_gaps = [ChronoBridgeGap(**dict(item)) for item in payload.get("bridge_gaps", [])]

    return ChronoReconstruction(
        run_id=payload["run_id"],
        input_hash=payload["input_hash"],
        reconstruction_hash=payload["reconstruction_hash"],
        events=events,
        causal_edges=causal_edges,
        memory_edges=memory_edges,
        geometry_edges=geometry_edges,
        contradictions=contradictions,
        bridge_gaps=bridge_gaps,
        entropy_score=payload["entropy_score"],
        information_score=payload["information_score"],
        coherence=payload["coherence"],
        stable=payload["stable"],
        seed=payload["seed"],
        bridge_profile=payload.get("bridge_profile", "balanced"),
    )


def receipt_to_dict(receipt: ChronoReceipt) -> dict:
    payload = asdict(receipt)
    return wrap_artifact(ARTIFACT_KIND_RECEIPT, SCHEMA_VERSION, payload)


def receipt_from_dict(data: dict) -> ChronoReceipt:
    payload = unwrap_artifact(dict(data), ARTIFACT_KIND_RECEIPT)
    errors = validate_receipt_dict(payload)
    _require_or_raise(errors, "receipt")
    return ChronoReceipt(**payload)


def load_json(path: str | Path) -> dict:
    content = Path(path).read_text(encoding="utf-8")
    loaded = json.loads(content)
    if not isinstance(loaded, dict):
        raise ValueError("JSON root must be an object.")
    return loaded


def write_json(path: str | Path, data: dict) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(data), indent=2, sort_keys=True), encoding="utf-8")
