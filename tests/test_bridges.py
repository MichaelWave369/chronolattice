import json
from pathlib import Path

from chronolattice.adapters.phios import to_phios_payload
from chronolattice.cli import main
from chronolattice.coherence import score_coherence
from chronolattice.models import ChronoBridgeGap, ChronoConfig
from chronolattice.reconstruct import reconstruct
from chronolattice.serialization import reconstruction_from_dict, reconstruction_to_dict


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_simple_timeline_has_no_high_severity_bridge_gaps():
    data = _load("data/examples/simple_timeline.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert not any(g.severity == "high" for g in result.bridge_gaps)


def test_missing_bridge_gap_produces_gaps():
    data = _load("data/examples/missing_bridge_gap.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert len(result.bridge_gaps) >= 1


def test_missing_bridge_gap_contains_event_type_jump():
    data = _load("data/examples/missing_bridge_gap.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert any(g.gap_type == "event_type_jump" for g in result.bridge_gaps)


def test_coherence_drop_gap_detected_when_drop_exceeds_threshold():
    data = _load("data/examples/missing_bridge_gap.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert any(g.gap_type == "coherence_drop" for g in result.bridge_gaps)


def test_actor_discontinuity_detected_with_shared_memory_no_handoff():
    data = _load("data/examples/missing_bridge_gap.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert any(g.gap_type == "actor_discontinuity" for g in result.bridge_gaps)


def test_bridge_gap_ids_are_deterministic_across_runs():
    data = _load("data/examples/missing_bridge_gap.json")
    config = ChronoConfig(seed=369369)
    a = reconstruct(data["events"], config)
    b = reconstruct(data["events"], config)
    assert [g.gap_id for g in a.bridge_gaps] == [g.gap_id for g in b.bridge_gaps]


def test_bridge_gaps_present_in_serialized_reconstruction():
    data = _load("data/examples/missing_bridge_gap.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    payload = reconstruction_to_dict(result)
    assert "bridge_gaps" in payload["payload"]


def test_reconstruction_from_legacy_defaults_missing_bridge_gaps():
    data = _load("data/examples/simple_timeline.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    wrapped = reconstruction_to_dict(result)
    legacy = dict(wrapped["payload"])
    legacy.pop("bridge_gaps", None)
    restored = reconstruction_from_dict(legacy)
    assert restored.bridge_gaps == []


def test_bridge_gap_penalty_reduces_coherence_score():
    data = _load("data/examples/simple_timeline.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    without = score_coherence(
        result.causal_edges,
        result.memory_edges,
        result.geometry_edges,
        result.entropy_score,
        result.information_score,
        result.contradictions,
        ChronoConfig(seed=369369),
        bridge_gaps=[],
    )
    synthetic_gap = ChronoBridgeGap(
        gap_id="g",
        source_event_id=result.events[0].event_id,
        target_event_id=result.events[1].event_id,
        gap_type="coherence_drop",
        severity="high",
        score=1.0,
        missing_bridge_hint="x",
        evidence={},
        suggested_event_type="stabilization",
    )
    with_gap = score_coherence(
        result.causal_edges,
        result.memory_edges,
        result.geometry_edges,
        result.entropy_score,
        result.information_score,
        result.contradictions,
        ChronoConfig(seed=369369),
        bridge_gaps=[synthetic_gap],
    )
    assert with_gap < without


def test_cli_bridge_gaps_command_outputs_list(tmp_path: Path, capsys):
    out = tmp_path / "bridge_reconstruction.json"
    main(["reconstruct", "data/examples/missing_bridge_gap.json", "--out", str(out)])

    code = main(["bridge-gaps", str(out)])
    printed = capsys.readouterr().out
    payload = json.loads(printed)
    assert code == 0
    assert isinstance(payload, list)
    assert len(payload) >= 1


def test_phios_payload_includes_bridge_gaps_and_profile_mode_thresholds():
    data = _load("data/examples/missing_bridge_gap.json")
    result = reconstruct(data["events"], ChronoConfig(seed=369369, bridge_profile="sensitive"))
    payload = to_phios_payload(result)
    assert "bridge_gaps" in payload
    assert payload["field"]["bridge_profile"] == "sensitive"
    assert payload["field"]["bridge_threshold_mode"] == "profile"
    assert isinstance(payload["field"]["bridge_thresholds"], dict)


def test_sensitive_profile_detects_at_least_as_many_gaps_as_conservative():
    data = _load("data/examples/missing_bridge_gap.json")
    conservative = reconstruct(data["events"], ChronoConfig(seed=369369, bridge_profile="conservative"))
    sensitive = reconstruct(data["events"], ChronoConfig(seed=369369, bridge_profile="sensitive"))
    assert len(sensitive.bridge_gaps) >= len(conservative.bridge_gaps)


def test_manual_mode_high_thresholds_detect_fewer_or_equal_gaps_than_sensitive():
    data = _load("data/examples/missing_bridge_gap.json")
    sensitive = reconstruct(data["events"], ChronoConfig(seed=369369, bridge_profile="sensitive"))
    manual = reconstruct(
        data["events"],
        ChronoConfig(
            seed=369369,
            bridge_threshold_mode="manual",
            bridge_gap_threshold=0.90,
            coherence_drop_threshold=0.90,
            energy_jump_threshold=0.90,
            information_jump_threshold=0.90,
        ),
    )
    assert len(manual.bridge_gaps) <= len(sensitive.bridge_gaps)


def test_reconstruct_records_profile_and_manual_modes_and_thresholds():
    data = _load("data/examples/missing_bridge_gap.json")
    profile_result = reconstruct(data["events"], ChronoConfig(seed=369369))
    manual_result = reconstruct(
        data["events"],
        ChronoConfig(
            seed=369369,
            bridge_threshold_mode="manual",
            bridge_gap_threshold=0.75,
            coherence_drop_threshold=0.30,
            energy_jump_threshold=0.80,
            information_jump_threshold=0.70,
        ),
    )
    assert profile_result.bridge_threshold_mode == "profile"
    assert manual_result.bridge_threshold_mode == "manual"
    assert manual_result.bridge_thresholds == {
        "bridge_gap_threshold": 0.75,
        "coherence_drop_threshold": 0.3,
        "energy_jump_threshold": 0.8,
        "information_jump_threshold": 0.7,
    }
