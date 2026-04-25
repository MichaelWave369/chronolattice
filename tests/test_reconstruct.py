import json
from pathlib import Path

from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import reconstruct


def test_reconstruction_is_deterministic():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    cfg = ChronoConfig(seed=369369)
    a = reconstruct(data["events"], cfg)
    b = reconstruct(data["events"], cfg)
    assert a.reconstruction_hash == b.reconstruction_hash
    assert a.input_hash == b.input_hash
    assert a.coherence == b.coherence
