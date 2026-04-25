import json
from pathlib import Path

from chronolattice.cli import main


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
    assert "receipt_id" in receipt_data
    assert "reconstruction_hash" in receipt_data
