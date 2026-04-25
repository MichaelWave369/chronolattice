import json
from pathlib import Path

from chronolattice.constants import C_STAR
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import reconstruct


def test_simple_timeline_coherence_is_stable():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert result.coherence >= C_STAR


def test_coherence_collapse_is_not_stable():
    data = json.loads(Path("data/examples/coherence_collapse.json").read_text(encoding="utf-8"))
    result = reconstruct(data["events"], ChronoConfig(seed=369369))
    assert result.stable is False
