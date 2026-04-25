import json
from pathlib import Path

from chronolattice.constants import ARTIFACT_KIND_RECONSTRUCTION, SCHEMA_VERSION
from chronolattice.hashing import stable_hash
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import reconstruct
from chronolattice.serialization import (
    load_json,
    reconstruction_from_dict,
    reconstruction_to_dict,
    write_json,
)


def test_reconstruction_round_trip_deterministic():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    config = ChronoConfig(seed=369369, fixed_timestamp="2026-04-24T00:00:00Z")
    original = reconstruct(data["events"], config)

    serialized = reconstruction_to_dict(original)
    restored = reconstruction_from_dict(serialized)

    assert serialized["kind"] == ARTIFACT_KIND_RECONSTRUCTION
    assert serialized["schema_version"] == SCHEMA_VERSION
    assert "payload" in serialized
    assert stable_hash(original) == stable_hash(restored)
    assert original.reconstruction_hash == restored.reconstruction_hash
    assert original.coherence == restored.coherence


def test_reconstruction_json_file_round_trip(tmp_path: Path):
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    original = reconstruct(data["events"], ChronoConfig(seed=369369))
    out_file = tmp_path / "reconstruction.json"

    write_json(out_file, reconstruction_to_dict(original))
    loaded = load_json(out_file)
    restored = reconstruction_from_dict(loaded)

    assert restored.reconstruction_hash == original.reconstruction_hash


def test_reconstruction_from_legacy_flat_dict():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    original = reconstruct(data["events"], ChronoConfig(seed=369369))
    legacy_payload = reconstruction_to_dict(original)["payload"]

    restored = reconstruction_from_dict(legacy_payload)
    assert stable_hash(original) == stable_hash(restored)
