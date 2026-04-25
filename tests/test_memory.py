import json
from pathlib import Path

from chronolattice.memory import build_memory_edges, detect_memory_contradictions
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import normalize_events


def test_memory_orphan_detected():
    data = json.loads(Path("data/examples/memory_orphan.json").read_text(encoding="utf-8"))
    events = normalize_events(data["events"])
    edges = build_memory_edges(events, ChronoConfig())
    contradictions = detect_memory_contradictions(events, edges)
    assert any(c.contradiction_type == "memory_orphan" for c in contradictions)
