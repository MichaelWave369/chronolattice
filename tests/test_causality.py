import json
from pathlib import Path

from chronolattice.causality import build_causal_edges, detect_causal_contradictions
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import normalize_events


def test_timestamp_inversion_detected():
    data = json.loads(Path("data/examples/causal_loop.json").read_text(encoding="utf-8"))
    events = normalize_events(data["events"])
    edges = build_causal_edges(events, ChronoConfig())
    contradictions = detect_causal_contradictions(events, edges)
    types = {c.contradiction_type for c in contradictions}
    assert "timestamp_inversion" in types
