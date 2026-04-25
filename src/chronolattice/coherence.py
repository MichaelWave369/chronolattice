from __future__ import annotations

from .models import CausalEdge, ChronoBridgeGap, ChronoConfig, ChronoContradiction, GeometryEdge, MemoryEdge


def clamp01(value: float) -> float:
    return max(0.0, min(value, 1.0))


def score_coherence(
    causal_edges: list[CausalEdge],
    memory_edges: list[MemoryEdge],
    geometry_edges: list[GeometryEdge],
    entropy_score: float,
    information_score: float,
    contradictions: list[ChronoContradiction],
    config: ChronoConfig,
    bridge_gaps: list[ChronoBridgeGap] | None = None,
) -> float:
    allowed = [e.causal_weight for e in causal_edges if e.allowed]
    causal_fit = sum(allowed) / len(allowed) if allowed else 1.0
    memory_fit = sum(e.memory_weight for e in memory_edges) / len(memory_edges) if memory_edges else 1.0
    geometry_fit = sum(e.geometry_weight for e in geometry_edges) / len(geometry_edges) if geometry_edges else 1.0
    receipt_fit = 1.0

    contradiction_penalties = {"low": 0.03, "medium": 0.08, "high": 0.16}
    contradiction_penalty = sum(contradiction_penalties.get(c.severity, 0.08) for c in contradictions)

    bridge_penalties = {"low": 0.02, "medium": 0.05, "high": 0.10}
    bridge_penalty = sum(bridge_penalties.get(g.severity, 0.02) for g in (bridge_gaps or []))

    blended = (
        0.20 * causal_fit
        + 0.20 * memory_fit
        + 0.15 * clamp01(entropy_score)
        + 0.15 * clamp01(information_score)
        + 0.15 * receipt_fit
        + 0.15 * geometry_fit
        - contradiction_penalty
        - bridge_penalty
    )
    return clamp01(blended)


def is_stable(coherence: float, config: ChronoConfig) -> bool:
    return coherence >= config.stability_threshold
