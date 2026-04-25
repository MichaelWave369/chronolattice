import json
from pathlib import Path

from chronolattice.constants import ARTIFACT_KIND_RECEIPT, ARTIFACT_KIND_RECONSTRUCTION
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import reconstruct
from chronolattice.schema import (
    validate_artifact_envelope,
    validate_event_dict,
    validate_receipt_dict,
    validate_reconstruction_dict,
)
from chronolattice.serialization import reconstruction_to_dict


def test_valid_event_has_no_errors():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    event = data["events"][0]
    assert validate_event_dict(event) == []


def test_missing_event_id_returns_error():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    event = dict(data["events"][0])
    event.pop("event_id")
    errors = validate_event_dict(event)
    assert any("event_id" in err for err in errors)


def test_missing_reconstruction_hash_returns_error():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    payload = reconstruction_to_dict(reconstruction)["payload"]
    payload.pop("reconstruction_hash")
    errors = validate_reconstruction_dict(payload)
    assert any("reconstruction_hash" in err for err in errors)


def test_missing_receipt_id_returns_error():
    receipt = {
        "run_id": "r",
        "input_hash": "i",
        "reconstruction_hash": "h",
        "event_count": 1,
        "causal_edges": 1,
        "memory_edges": 1,
        "geometry_edges": 1,
        "coherence": 0.9,
        "stable": True,
        "entropy_score": 0.8,
        "contradiction_count": 0,
        "selected_model": "chronolattice.v0_1",
        "seed": 369369,
        "created_at": "2026-04-24T00:00:00Z",
    }
    errors = validate_receipt_dict(receipt)
    assert any("receipt_id" in err for err in errors)


def test_validate_artifact_envelope_accepts_valid_reconstruction_wrapper():
    data = {
        "kind": ARTIFACT_KIND_RECONSTRUCTION,
        "schema_version": "0.1",
        "payload": {"run_id": "x"},
    }
    assert validate_artifact_envelope(data, ARTIFACT_KIND_RECONSTRUCTION) == []


def test_validate_artifact_envelope_rejects_bad_kind():
    data = {
        "kind": ARTIFACT_KIND_RECEIPT,
        "schema_version": "0.1",
        "payload": {"run_id": "x"},
    }
    errors = validate_artifact_envelope(data, ARTIFACT_KIND_RECONSTRUCTION)
    assert any("kind mismatch" in err for err in errors)
