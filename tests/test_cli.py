import json
from pathlib import Path

from chronolattice.cli import main
from chronolattice.constants import (
    ARTIFACT_KIND_PHIOS_PAYLOAD,
    ARTIFACT_KIND_RECEIPT,
    ARTIFACT_KIND_RECONSTRUCTION,
)


def test_cli_version_exits_zero(capsys):
    code = main(["version"])
    out = capsys.readouterr().out.strip()
    assert code == 0
    assert out == "0.1.0"


def test_cli_reconstruct_writes_output(tmp_path: Path):
    out = tmp_path / "reconstruction.json"
    code = main([
        "reconstruct",
        "data/examples/simple_timeline.json",
        "--seed",
        "369369",
        "--out",
        str(out),
    ])
    assert code == 0
    assert out.exists()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["kind"] == ARTIFACT_KIND_RECONSTRUCTION


def test_cli_receipt_flow(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    receipt_path = tmp_path / "receipt.json"

    reconstruct_code = main([
        "reconstruct",
        "data/examples/simple_timeline.json",
        "--seed",
        "369369",
        "--out",
        str(reconstruction_path),
    ])
    receipt_code = main([
        "receipt",
        str(reconstruction_path),
        "--out",
        str(receipt_path),
    ])

    assert reconstruct_code == 0
    assert receipt_code == 0
    assert reconstruction_path.exists()
    assert receipt_path.exists()

    receipt_data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt_data["kind"] == ARTIFACT_KIND_RECEIPT
    assert "receipt_id" in receipt_data["payload"]
    assert "reconstruction_hash" in receipt_data["payload"]


def test_cli_phios_payload_wrapped(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    phios_path = tmp_path / "phios.json"
    main([
        "reconstruct",
        "data/examples/simple_timeline.json",
        "--out",
        str(reconstruction_path),
    ])

    code = main([
        "phios-payload",
        str(reconstruction_path),
        "--out",
        str(phios_path),
    ])
    assert code == 0
    payload = json.loads(phios_path.read_text(encoding="utf-8"))
    assert payload["kind"] == ARTIFACT_KIND_PHIOS_PAYLOAD


def test_cli_inspect_and_contradictions_support_wrapped_reconstruction(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    main([
        "reconstruct",
        "data/examples/simple_timeline.json",
        "--out",
        str(reconstruction_path),
    ])

    inspect_code = main(["inspect", str(reconstruction_path)])
    inspect_out = capsys.readouterr().out
    contradictions_code = main(["contradictions", str(reconstruction_path)])
    contradictions_out = capsys.readouterr().out

    assert inspect_code == 0
    assert contradictions_code == 0
    assert "coherence" in inspect_out
    assert contradictions_out.strip().startswith("[")


def test_cli_migration_status_on_wrapped_reconstruction(tmp_path: Path, capsys):
    reconstruction_path = tmp_path / "reconstruction.json"
    main([
        "reconstruct",
        "data/examples/simple_timeline.json",
        "--out",
        str(reconstruction_path),
    ])

    code = main(["migration-status", str(reconstruction_path)])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["supported"] is True
    assert payload["needs_migration"] is False


def test_cli_migrate_copies_current_wrapped_artifact(tmp_path: Path):
    reconstruction_path = tmp_path / "reconstruction.json"
    migrated_path = tmp_path / "reconstruction_migrated.json"
    main([
        "reconstruct",
        "data/examples/simple_timeline.json",
        "--out",
        str(reconstruction_path),
    ])

    code = main(["migrate", str(reconstruction_path), "--out", str(migrated_path)])
    assert code == 0
    assert migrated_path.exists()

    original = json.loads(reconstruction_path.read_text(encoding="utf-8"))
    migrated = json.loads(migrated_path.read_text(encoding="utf-8"))
    assert migrated == original
