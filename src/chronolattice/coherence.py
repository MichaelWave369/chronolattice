from __future__ import annotations

from .constants import C_STAR
from .models import CausalEdge, ChronoConfig, ChronoContradiction, GeometryEdge, MemoryEdge


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
) -> float:
    allowed = [e.causal_weight for e in causal_edges if e.allowed]
    causal_fit = sum(allowed) / len(allowed) if allowed else 1.0
    memory_fit = sum(e.memory_weight for e in memory_edges) / len(memory_edges) if memory_edges else 1.0
    geometry_fit = sum(e.geometry_weight for e in geometry_edges) / len(geometry_edges) if geometry_edges else 1.0
    receipt_fit = 1.0
    penalties = {"low": 0.03, "medium": 0.08, "high": 0.16}
    penalty = sum(penalties.get(c.severity, 0.08) for c in contradictions)

    blended = (
        0.20 * causal_fit
        + 0.20 * memory_fit
        + 0.15 * clamp01(entropy_score)
        + 0.15 * clamp01(information_score)
        + 0.15 * receipt_fit
        + 0.15 * geometry_fit
        - penalty
    )
    return clamp01(blended)


def is_stable(coherence: float, config: ChronoConfig) -> bool:
    return coherence >= config.stability_threshold
