import json
from pathlib import Path

import pytest

from chronolattice.cli import main
from chronolattice.constants import ARTIFACT_KIND_RECEIPT, ARTIFACT_KIND_RECONSTRUCTION, SCHEMA_VERSION
from chronolattice.models import ChronoConfig
from chronolattice.normalization import (
    detect_legacy_artifact_kind,
    normalize_artifact_envelope,
    normalize_artifact_file,
)
from chronolattice.receipts import emit_receipt
from chronolattice.reconstruct import reconstruct
from chronolattice.serialization import receipt_to_dict, reconstruction_to_dict


def _legacy_reconstruction() -> dict:
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    return reconstruction_to_dict(reconstruction)["payload"]


def _legacy_receipt() -> dict:
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    config = ChronoConfig(seed=369369, fixed_timestamp="2026-04-24T00:00:00Z")
    reconstruction = reconstruct(data["events"], config)
    receipt = emit_receipt(reconstruction, config)
    return receipt_to_dict(receipt)["payload"]


def test_detect_legacy_artifact_kind_for_reconstruction():
    assert detect_legacy_artifact_kind(_legacy_reconstruction()) == ARTIFACT_KIND_RECONSTRUCTION


def test_detect_legacy_artifact_kind_for_receipt():
    assert detect_legacy_artifact_kind(_legacy_receipt()) == ARTIFACT_KIND_RECEIPT


def test_detect_legacy_artifact_kind_for_wrapped_artifact():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    wrapped = reconstruction_to_dict(reconstruction)
    assert detect_legacy_artifact_kind(wrapped) == ARTIFACT_KIND_RECONSTRUCTION


def test_detect_legacy_artifact_kind_for_unknown_dict():
    assert detect_legacy_artifact_kind({"foo": "bar"}) is None


def test_normalize_artifact_envelope_wraps_legacy_reconstruction():
    legacy = _legacy_reconstruction()
    normalized = normalize_artifact_envelope(legacy)
    assert normalized["kind"] == ARTIFACT_KIND_RECONSTRUCTION
    assert normalized["schema_version"] == SCHEMA_VERSION
    assert normalized["payload"] == legacy


def test_normalize_artifact_envelope_wraps_legacy_receipt():
    legacy = _legacy_receipt()
    normalized = normalize_artifact_envelope(legacy)
    assert normalized["kind"] == ARTIFACT_KIND_RECEIPT
    assert normalized["schema_version"] == SCHEMA_VERSION
    assert normalized["payload"] == legacy


def test_normalize_artifact_envelope_returns_copy_for_wrapped_artifact():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    wrapped = reconstruction_to_dict(reconstruction)
    normalized = normalize_artifact_envelope(wrapped)
    assert normalized == wrapped
    assert normalized is not wrapped


def test_normalize_artifact_envelope_does_not_mutate_input():
    legacy = _legacy_reconstruction()
    original = json.loads(json.dumps(legacy))
    _ = normalize_artifact_envelope(legacy)
    assert legacy == original


def test_normalize_artifact_envelope_raises_on_unknown_shape():
    with pytest.raises(ValueError):
        normalize_artifact_envelope({"foo": "bar"})


def test_normalize_artifact_envelope_raises_on_kind_mismatch():
    with pytest.raises(ValueError):
        normalize_artifact_envelope(_legacy_reconstruction(), kind=ARTIFACT_KIND_RECEIPT)


def test_normalize_artifact_file_writes_output(tmp_path: Path):
    legacy_file = tmp_path / "legacy.json"
    out_file = tmp_path / "normalized.json"
    legacy = _legacy_reconstruction()
    legacy_file.write_text(json.dumps(legacy), encoding="utf-8")

    normalized = normalize_artifact_file(legacy_file, out=out_file)
    assert out_file.exists()
    loaded = json.loads(out_file.read_text(encoding="utf-8"))
    assert loaded == normalized
    assert loaded["kind"] == ARTIFACT_KIND_RECONSTRUCTION


def test_cli_normalize_envelope_on_legacy_flat_reconstruction(tmp_path: Path):
    legacy = _legacy_reconstruction()
    legacy_path = tmp_path / "legacy.json"
    wrapped_path = tmp_path / "wrapped.json"
    legacy_path.write_text(json.dumps(legacy), encoding="utf-8")

    code = main(["normalize-envelope", str(legacy_path), "--out", str(wrapped_path)])
    assert code == 0
    assert wrapped_path.exists()
    wrapped = json.loads(wrapped_path.read_text(encoding="utf-8"))
    assert wrapped["kind"] == ARTIFACT_KIND_RECONSTRUCTION
    assert wrapped["payload"]["reconstruction_hash"] == legacy["reconstruction_hash"]


def test_cli_normalize_envelope_on_wrapped_reconstruction(tmp_path: Path):
    wrapped_path = tmp_path / "wrapped.json"
    normalized_path = tmp_path / "normalized.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(wrapped_path)])

    code = main(["normalize-envelope", str(wrapped_path), "--out", str(normalized_path)])
    assert code == 0
    original = json.loads(wrapped_path.read_text(encoding="utf-8"))
    normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
    assert normalized == original


def test_cli_normalize_envelope_prints_stdout_when_out_omitted(tmp_path: Path, capsys):
    wrapped_path = tmp_path / "wrapped.json"
    main(["reconstruct", "data/examples/simple_timeline.json", "--out", str(wrapped_path)])

    code = main(["normalize-envelope", str(wrapped_path)])
    out = capsys.readouterr().out
    payload = json.loads(out)

    assert code == 0
    assert payload["kind"] == ARTIFACT_KIND_RECONSTRUCTION
