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
