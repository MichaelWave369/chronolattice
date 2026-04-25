import json
from dataclasses import replace
from pathlib import Path

from chronolattice.adapters.phios import to_phios_payload
from chronolattice.cli import main
from chronolattice.constants import ARTIFACT_KIND_BRIDGE_REPORT, SCHEMA_VERSION
from chronolattice.models import ChronoBridgeGap, ChronoConfig
from chronolattice.reconstruct import reconstruct
from chronolattice.reports import bridge_report_artifact, bridge_gap_report_id, build_bridge_gap_report
from chronolattice.schema import validate_bridge_report_dict


def _load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_simple_timeline_bridge_report_no_gaps_has_stable_summary():
    data = _load("data/examples/simple_timeline.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    report = build_bridge_gap_report(reconstruction)
    assert report["total_bridge_gaps"] == 0
    assert report["severity_counts"] == {"low": 0, "medium": 0, "high": 0}
    assert "No bridge gaps detected" in report["operator_summary"]


def test_missing_bridge_gap_report_counts_and_gap_types():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    report = build_bridge_gap_report(reconstruction)
    assert report["total_bridge_gaps"] > 0
    assert sum(report["severity_counts"].values()) == report["total_bridge_gaps"]
    assert (
        "event_type_jump" in report["gap_type_counts"]
        or "coherence_drop" in report["gap_type_counts"]
    )


def test_top_bridge_gap_ordering_is_deterministic():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    report_a = build_bridge_gap_report(reconstruction)
    report_b = build_bridge_gap_report(reconstruction)
    assert report_a["top_bridge_gaps"] == report_b["top_bridge_gaps"]


def test_bridge_gap_report_id_is_deterministic():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    report_id_a = bridge_gap_report_id(reconstruction)
    report_id_b = bridge_gap_report_id(reconstruction)
    assert report_id_a == report_id_b


def test_bridge_report_artifact_wrapper_shape():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    artifact = bridge_report_artifact(reconstruction)
    assert artifact["kind"] == ARTIFACT_KIND_BRIDGE_REPORT
    assert artifact["schema_version"] == SCHEMA_VERSION
    assert artifact["payload"]["report_id"]


def test_cli_bridge_report_writes_output_file(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    report_path = tmp_path / "report.json"
    main(["reconstruct", "data/examples/missing_bridge_gap.json", "--out", str(reconstruction_path)])
    code = main(["bridge-report", str(reconstruction_path), "--out", str(report_path)])
    assert code == 0
    artifact = json.loads(report_path.read_text(encoding="utf-8"))
    assert artifact["kind"] == ARTIFACT_KIND_BRIDGE_REPORT


def test_cli_bridge_report_stdout_mode_prints_wrapped_artifact(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    main(["reconstruct", "data/examples/missing_bridge_gap.json", "--out", str(reconstruction_path)])
    code = main(["bridge-report", str(reconstruction_path)])
    out = capsys.readouterr().out
    assert code == 0
    artifact = json.loads(out)
    assert artifact["kind"] == ARTIFACT_KIND_BRIDGE_REPORT


def test_cli_validate_accepts_wrapped_bridge_report(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    report_path = tmp_path / "report.json"
    main(["reconstruct", "data/examples/missing_bridge_gap.json", "--out", str(reconstruction_path)])
    main(["bridge-report", str(reconstruction_path), "--out", str(report_path)])
    code = main(["validate", str(report_path)])
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "ok"


def test_validate_bridge_report_dict_accepts_valid_payload():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    payload = bridge_report_artifact(reconstruction)["payload"]
    assert validate_bridge_report_dict(payload) == []


def test_validate_bridge_report_dict_rejects_missing_report_id():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    payload = dict(bridge_report_artifact(reconstruction)["payload"])
    payload.pop("report_id")
    errors = validate_bridge_report_dict(payload)
    assert any("report_id" in error for error in errors)


def test_phios_payload_includes_bridge_gap_report_summary():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    payload = to_phios_payload(reconstruction)
    summary = payload["field"]["bridge_gap_report_summary"]
    assert summary["total_bridge_gaps"] == len(reconstruction.bridge_gaps)
    assert "severity_counts" in summary
    assert "gap_type_counts" in summary
    assert "operator_summary" in summary


def test_report_recommendations_include_provenance_guidance_for_provenance_gap():
    data = _load("data/examples/simple_timeline.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    provenance_gap = ChronoBridgeGap(
        gap_id="synthetic-provenance-gap",
        source_event_id=reconstruction.events[0].event_id,
        target_event_id=reconstruction.events[1].event_id,
        gap_type="provenance_gap",
        severity="medium",
        score=0.91,
        missing_bridge_hint="missing provenance handoff",
        evidence={"reason": "test"},
        suggested_event_type="provenance_receipt",
    )
    reconstruction_with_gap = replace(reconstruction, bridge_gaps=[provenance_gap])
    report = build_bridge_gap_report(reconstruction_with_gap)
    assert "Add provenance receipts for result, artifact, commit, or receipt events." in report["recommendations"]


def test_report_recommendations_include_build_transition_for_event_type_jump():
    data = _load("data/examples/missing_bridge_gap.json")
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369, bridge_profile="sensitive"))
    report = build_bridge_gap_report(reconstruction)
    assert "Add planning/build transition events between idea and result states." in report["recommendations"]
