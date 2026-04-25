from __future__ import annotations

from .models import CausalEdge, ChronoConfig, ChronoEvent, GeometryEdge, MemoryEdge


def build_geometry_edges(
    events: list[ChronoEvent],
    causal_edges: list[CausalEdge],
    memory_edges: list[MemoryEdge],
    config: ChronoConfig,
) -> list[GeometryEdge]:
    causal_map = {(e.source_event_id, e.target_event_id): e for e in causal_edges}
    memory_map = {(e.source_event_id, e.target_event_id): e for e in memory_edges}
    memory_map.update({(e.target_event_id, e.source_event_id): e for e in memory_edges})

    geometry: list[GeometryEdge] = []
    for i, source in enumerate(events):
        for target in events[i + 1 :]:
            seq_distance = abs(target.sequence_index - source.sequence_index)
            causal = causal_map.get((source.event_id, target.event_id))
            mem = memory_map.get((source.event_id, target.event_id))
            causal_factor = 1.0 - (causal.causal_weight if causal and causal.allowed else 0.0)
            memory_factor = 1.0 - (mem.memory_weight if mem else 0.0)
            actor_factor = 0.0 if source.actor == target.actor else 1.0
            info_delta = min(abs(source.information_value - target.information_value), 1.0)
            inferred = (
                0.30 * min(seq_distance / max(len(events), 1), 1.0)
                + 0.20 * causal_factor
                + 0.20 * memory_factor
                + 0.15 * actor_factor
                + 0.15 * info_delta
            )
            inferred = max(0.0, min(inferred, 1.0))
            weight = 1.0 / (1.0 + inferred)
            geometry.append(
                GeometryEdge(
                    source_event_id=source.event_id,
                    target_event_id=target.event_id,
                    observed_distance=None,
                    inferred_distance=inferred,
                    signal_delay=None,
                    geometry_weight=weight,
                )
            )
    return geometry
