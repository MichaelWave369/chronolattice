import json
from pathlib import Path

from chronolattice.cli import main
from chronolattice.constants import ARTIFACT_KIND_PHIOS_PAYLOAD, ARTIFACT_KIND_RECEIPT, ARTIFACT_KIND_RECONSTRUCTION


def test_cli_version_exits_zero(capsys):
    code = main(["version"])
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "0.1.0"


def test_cli_reconstruct_writes_output(tmp_path: Path):
    out = tmp_path / "reconstruction.json"
    code = main(["reconstruct", "data/examples/simple_timeline.json", "--seed", "369369", "--out", str(out)])
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["kind"] == ARTIFACT_KIND_RECONSTRUCTION


def test_cli_receipt_flow(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    receipt_path = tmp_path / "receipt.json"
    reconstruct_code = main(["reconstruct", "data/examples/simple_timeline.json", "--seed", "369369", "--out", str(reconstruction_path)])
    receipt_code = main(["receipt", str(reconstruction_path), "--out", str(receipt_path)])
    assert reconstruct_code == 0
    assert receipt_code == 0
    receipt_data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt_data["kind"] == ARTIFACT_KIND_RECEIPT


def test_cli_phios_payload_wrapped(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    phios_path = tmp_path / "phios.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(reconstruction_path)])
    code = main(["phios-payload", str(reconstruction_path), "--out", str(phios_path)])
    assert code == 0
    payload = json.loads(phios_path.read_text(encoding="utf-8"))
    assert payload["kind"] == ARTIFACT_KIND_PHIOS_PAYLOAD


def test_cli_inspect_and_contradictions_support_wrapped_reconstruction(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(reconstruction_path)])
    inspect_code = main(["inspect", str(reconstruction_path)])
    inspect_out = capsys.readouterr().out
    contradictions_code = main(["contradictions", str(reconstruction_path)])
    contradictions_out = capsys.readouterr().out
    assert inspect_code == 0
    assert contradictions_code == 0
    assert "bridge_threshold_mode" in inspect_out
    assert contradictions_out.strip().startswith("[")


def test_cli_migration_status_on_wrapped_reconstruction(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(reconstruction_path)])
    code = main(["migration-status", str(reconstruction_path)])
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert code == 0
    assert payload["supported"] is True


def test_cli_migrate_copies_current_wrapped_artifact(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    migrated_path = tmp_path / "reconstruction_migrated.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(reconstruction_path)])
    code = main(["migrate", str(reconstruction_path), "--out", str(migrated_path)])
    assert code == 0
    original = json.loads(reconstruction_path.read_text(encoding="utf-8"))
    migrated = json.loads(migrated_path.read_text(encoding="utf-8"))
    assert migrated == original


def test_cli_reconstruct_writes_conservative_profile_metadata(tmp_path: Path):
    out = tmp_path / "conservative.json"
    code = main(["reconstruct", "data/examples/missing_bridge_gap.json", "--bridge-profile", "conservative", "--out", str(out)])
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert code == 0
    assert payload["payload"]["bridge_profile"] == "conservative"
    assert payload["payload"]["bridge_threshold_mode"] == "profile"


def test_cli_reconstruct_writes_sensitive_profile_metadata(tmp_path: Path):
    out = tmp_path / "sensitive.json"
    code = main(["reconstruct", "data/examples/missing_bridge_gap.json", "--bridge-profile", "sensitive", "--out", str(out)])
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert code == 0
    assert payload["payload"]["bridge_profile"] == "sensitive"
    assert payload["payload"]["bridge_threshold_mode"] == "profile"
    assert payload["payload"]["bridge_threshold_provenance"] == {
        "bridge_gap_threshold": "profile:sensitive",
        "coherence_drop_threshold": "profile:sensitive",
        "energy_jump_threshold": "profile:sensitive",
        "information_jump_threshold": "profile:sensitive",
    }


def test_cli_bridge_profiles_lists_all_profiles(capsys):
    code = main(["bridge-profiles"])
    out = capsys.readouterr().out
    payload = json.loads(out)
    names = [item["name"] for item in payload]
    assert code == 0
    assert names == ["conservative", "balanced", "sensitive", "phi_guardian"]


def test_cli_reconstruct_manual_mode_writes_threshold_metadata(tmp_path: Path):
    out = tmp_path / "manual.json"
    code = main([
        "reconstruct",
        "data/examples/missing_bridge_gap.json",
        "--bridge-threshold-mode",
        "manual",
        "--bridge-gap-threshold",
        "0.75",
        "--coherence-drop-threshold",
        "0.30",
        "--energy-jump-threshold",
        "0.80",
        "--information-jump-threshold",
        "0.70",
        "--out",
        str(out),
    ])
    payload = json.loads(out.read_text(encoding="utf-8"))["payload"]
    assert code == 0
    assert payload["bridge_threshold_mode"] == "manual"
    assert payload["bridge_thresholds"] == {
        "bridge_gap_threshold": 0.75,
        "coherence_drop_threshold": 0.3,
        "energy_jump_threshold": 0.8,
        "information_jump_threshold": 0.7,
    }
    assert payload["bridge_threshold_provenance"] == {
        "bridge_gap_threshold": "manual_cli",
        "coherence_drop_threshold": "manual_cli",
        "energy_jump_threshold": "manual_cli",
        "information_jump_threshold": "manual_cli",
    }


def test_cli_reconstruct_manual_mode_partial_flags_set_default_provenance(tmp_path: Path):
    out = tmp_path / "manual_partial.json"
    code = main([
        "reconstruct",
        "data/examples/missing_bridge_gap.json",
        "--bridge-threshold-mode",
        "manual",
        "--bridge-gap-threshold",
        "0.75",
        "--energy-jump-threshold",
        "0.80",
        "--out",
        str(out),
    ])
    payload = json.loads(out.read_text(encoding="utf-8"))["payload"]
    assert code == 0
    assert payload["bridge_threshold_provenance"] == {
        "bridge_gap_threshold": "manual_cli",
        "coherence_drop_threshold": "manual_default",
        "energy_jump_threshold": "manual_cli",
        "information_jump_threshold": "manual_default",
    }


def test_cli_reconstruct_profile_mode_rejects_manual_threshold_flags(capsys):
    code = main([
        "reconstruct",
        "data/examples/missing_bridge_gap.json",
        "--bridge-threshold-mode",
        "profile",
        "--bridge-gap-threshold",
        "0.99",
        "--out",
        "out/should_not_exist.json",
    ])
    out = capsys.readouterr().out
    assert code == 1
    assert "Manual threshold flags require --bridge-threshold-mode manual" in out


def test_cli_inspect_includes_bridge_threshold_provenance(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(reconstruction_path)])
    code = main(["inspect", str(reconstruction_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "bridge_threshold_provenance" in out
