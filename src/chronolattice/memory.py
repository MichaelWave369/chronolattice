from __future__ import annotations

from collections import Counter

from .models import ChronoConfig, ChronoContradiction, ChronoEvent, MemoryEdge


def build_memory_edges(events: list[ChronoEvent], config: ChronoConfig) -> list[MemoryEdge]:
    edges: list[MemoryEdge] = []
    total_unique_refs = len({ref for e in events for ref in e.memory_refs})
    for i, source in enumerate(events):
        for target in events[i + 1 :]:
            shared = sorted(set(source.memory_refs).intersection(target.memory_refs))
            if not shared:
                continue
            weight = len(shared) / max(total_unique_refs, 1)
            drift = abs(source.coherence - target.coherence)
            lineage_match = source.provenance.get("lineage", "") == target.provenance.get("lineage", "")
            edges.append(
                MemoryEdge(
                    source_event_id=source.event_id,
                    target_event_id=target.event_id,
                    memory_weight=weight,
                    shared_refs=shared,
                    drift=drift,
                    lineage_match=lineage_match,
                )
            )
    return edges


def detect_memory_contradictions(events: list[ChronoEvent], edges: list[MemoryEdge]) -> list[ChronoContradiction]:
    contradictions: list[ChronoContradiction] = []
    ref_counts = Counter(ref for e in events for ref in e.memory_refs)
    for event in events:
        if "memory_source" in event.provenance:
            continue
        orphan_refs = [ref for ref in event.memory_refs if ref_counts[ref] == 1]
        if orphan_refs:
            contradictions.append(
                ChronoContradiction(
                    contradiction_type="memory_orphan",
                    event_ids=[event.event_id],
                    severity="medium",
                    message=f"Event references orphan memory ids: {', '.join(sorted(orphan_refs))}",
                )
            )
    return contradictions
