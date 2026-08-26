from __future__ import annotations

from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path

import pytest

from chronolattice.hashing import stable_hash
from chronolattice.migrations import migrate_artifact
from chronolattice.models import ChronoConfig
from chronolattice.receipts import emit_receipt
from chronolattice.reconstruct import reconstruct
from chronolattice.reports import build_bridge_gap_report


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures"
CORE_FIXTURE = FIXTURES / "parallax-core-candidate-v0.json"
MAPPING_FIXTURE = FIXTURES / "pass13-chronolattice-core-mapping.json"
TIMELINE = ROOT / "data" / "examples" / "missing_bridge_gap.json"
CORE_SHA256 = "7df6b6ed596862c5d0aad794039424d4487cdb1d3cb43d2a50ede548dda6f96e"
PRIMITIVES = {
    "P1_NATIVE_AUTHORITY",
    "P2_EXACT_SUBJECT_IDENTITY",
    "P3_EVIDENCE_TRUTH_SEPARATION",
    "P4_EXPLICIT_HUMAN_BOUNDARY",
    "P5_AUTHORITY_PHASE_SEPARATION",
    "P6_FAIL_CLOSED_TRANSITION",
    "P7_IMMUTABLE_RECEIPT_LINEAGE",
}


def _timeline() -> dict:
    return json.loads(TIMELINE.read_text(encoding="utf-8"))


def _config() -> ChronoConfig:
    return ChronoConfig(fixed_timestamp="2026-08-26T00:20:00Z")


def test_frozen_candidate_is_exactly_the_pass12_candidate_before_mapping():
    raw = CORE_FIXTURE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == CORE_SHA256

    candidate = json.loads(raw)
    assert candidate["workingIdentifier"] == "parallax.core.candidate.v0"
    assert candidate["status"] == "NONCANONICAL_PASS12_CANDIDATE"
    assert {item["id"] for item in candidate["primitives"]} == PRIMITIVES

    mapping = json.loads(MAPPING_FIXTURE.read_text(encoding="utf-8"))
    assert mapping["candidate"]["sha256"] == CORE_SHA256
    assert mapping["candidate"]["frozenBeforeDomainSelection"] is True
    assert set(mapping["mappings"]) == PRIMITIVES


def test_p1_native_authority_probe_does_not_rewrite_native_input():
    raw = _timeline()
    original = deepcopy(raw["events"])

    reconstruction = reconstruct(raw["events"], _config())

    assert raw["events"] == original
    assert [event.event_id for event in reconstruction.events] == [
        item["event_id"] for item in original
    ]


def test_p2_exact_subject_identity_changes_when_subject_state_changes():
    raw = _timeline()
    baseline = reconstruct(raw["events"], _config())
    replay = reconstruct(deepcopy(raw["events"]), _config())

    assert replay.input_hash == baseline.input_hash
    assert replay.reconstruction_hash == baseline.reconstruction_hash
    assert emit_receipt(replay, _config()).receipt_id == emit_receipt(
        baseline, _config()
    ).receipt_id

    changed = deepcopy(raw["events"])
    changed[0]["information_value"] = float(changed[0]["information_value"]) + 0.01
    mutated = reconstruct(changed, _config())

    assert mutated.input_hash != baseline.input_hash
    assert mutated.reconstruction_hash != baseline.reconstruction_hash
    assert emit_receipt(mutated, _config()).receipt_id != emit_receipt(
        baseline, _config()
    ).receipt_id


def test_p3_reconstruction_identity_does_not_claim_physical_truth():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "does **not** claim full physical simulation in this version" in readme

    reconstruction = reconstruct(_timeline()["events"], _config())
    receipt = emit_receipt(reconstruction, _config())
    assert receipt.reconstruction_hash == reconstruction.reconstruction_hash
    # The receipt binds what the engine reconstructed; it contains no truth/rights authority flag.
    assert not hasattr(receipt, "truth")
    assert not hasattr(receipt, "authority")


def test_p4_missing_transition_inference_remains_recommendation_not_history_mutation():
    raw = _timeline()
    reconstruction = reconstruct(raw["events"], _config())
    report = build_bridge_gap_report(reconstruction)

    assert reconstruction.bridge_gaps, "fixture must expose at least one inferred bridge gap"
    assert len(reconstruction.events) == len(raw["events"])
    assert [event.event_id for event in reconstruction.events] == [
        item["event_id"] for item in raw["events"]
    ]
    assert report["recommendations"]
    assert all(gap.suggested_event_type is None or isinstance(gap.suggested_event_type, str)
               for gap in reconstruction.bridge_gaps)


def test_p5_receipt_and_recommendation_do_not_become_execution():
    reconstruction = reconstruct(_timeline()["events"], _config())
    before = stable_hash(reconstruction)

    receipt = emit_receipt(reconstruction, _config())
    report = build_bridge_gap_report(reconstruction)

    assert stable_hash(reconstruction) == before
    assert receipt.reconstruction_hash == reconstruction.reconstruction_hash
    assert report["reconstruction_hash"] == reconstruction.reconstruction_hash
    assert not hasattr(receipt, "execute")
    assert "recommendations" in report


def test_p6_unsupported_schema_transition_fails_closed():
    with pytest.raises(ValueError, match="Unsupported source schema_version"):
        migrate_artifact(
            {"kind": "reconstruction", "schema_version": "999", "payload": {}}
        )

    with pytest.raises(ValueError, match="Unsupported target schema_version"):
        migrate_artifact(
            {"kind": "reconstruction", "schema_version": "0.1", "payload": {}},
            target_version="999",
        )


def test_p7_prior_receipt_identity_is_immutable_across_later_rerun():
    raw = _timeline()
    baseline = reconstruct(raw["events"], _config())
    prior_receipt = emit_receipt(baseline, _config())
    prior_snapshot = (
        prior_receipt.receipt_id,
        prior_receipt.input_hash,
        prior_receipt.reconstruction_hash,
    )

    with pytest.raises(FrozenInstanceError):
        prior_receipt.reconstruction_hash = "rewritten"  # type: ignore[misc]

    changed = deepcopy(raw["events"])
    changed[-1]["coherence"] = float(changed[-1]["coherence"]) + 0.01
    later = reconstruct(changed, _config())
    later_receipt = emit_receipt(later, _config())

    assert (
        prior_receipt.receipt_id,
        prior_receipt.input_hash,
        prior_receipt.reconstruction_hash,
    ) == prior_snapshot
    assert later_receipt.input_hash != prior_receipt.input_hash
    assert later_receipt.reconstruction_hash != prior_receipt.reconstruction_hash
    assert later_receipt.receipt_id != prior_receipt.receipt_id
