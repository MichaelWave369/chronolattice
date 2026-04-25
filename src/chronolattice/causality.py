from __future__ import annotations

from datetime import datetime

from .models import CausalEdge, ChronoConfig, ChronoContradiction, ChronoEvent


def _parse_iso(ts: str) -> datetime:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts)


def build_causal_edges(events: list[ChronoEvent], config: ChronoConfig) -> list[CausalEdge]:
    edges: list[CausalEdge] = []
    for source in events:
        for target in events:
            if source.event_id == target.event_id:
                continue
            forward = source.sequence_index < target.sequence_index
            shared = len(set(source.memory_refs).intersection(target.memory_refs))
            prob = 0.20
            if source.actor == target.actor:
                prob += 0.25
            if source.event_type == target.event_type:
                prob += 0.20
            prob += min(shared * 0.15, 0.30)
            prob = min(prob, 0.99)
            delay = max(target.sequence_index - source.sequence_index, 0)
            allowed = forward
            reason = "forward_sequence" if allowed else "backward_sequence_blocked"
            causal_weight = prob if allowed else 0.0
            edges.append(
                CausalEdge(
                    source_event_id=source.event_id,
                    target_event_id=target.event_id,
                    probability=prob,
                    causal_weight=causal_weight,
                    delay=float(delay),
                    allowed=allowed,
                    reason=reason,
                )
            )
    return edges


def detect_causal_contradictions(events: list[ChronoEvent], edges: list[CausalEdge]) -> list[ChronoContradiction]:
    contradictions: list[ChronoContradiction] = []
    index_map = {e.event_id: e.sequence_index for e in events}
    for edge in edges:
        if edge.allowed and index_map[edge.source_event_id] >= index_map[edge.target_event_id]:
            contradictions.append(
                ChronoContradiction(
                    contradiction_type="causal_loop",
                    event_ids=[edge.source_event_id, edge.target_event_id],
                    severity="high",
                    message="Allowed causal edge points backward in sequence.",
                )
            )

    sorted_by_seq = sorted(events, key=lambda e: e.sequence_index)
    parsed = [_parse_iso(e.timestamp) for e in sorted_by_seq]
    for i in range(1, len(parsed)):
        if parsed[i] < parsed[i - 1]:
            contradictions.append(
                ChronoContradiction(
                    contradiction_type="timestamp_inversion",
                    event_ids=[sorted_by_seq[i - 1].event_id, sorted_by_seq[i].event_id],
                    severity="medium",
                    message="Sequence ordering conflicts with ISO timestamp ordering.",
                )
            )
    return contradictions
