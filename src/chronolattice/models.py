from __future__ import annotations

from dataclasses import dataclass, field

from .constants import C_STAR, DEFAULT_SEED


@dataclass(frozen=True)
class ChronoConfig:
    seed: int = DEFAULT_SEED
    selected_model: str = "chronolattice.v0_1"
    stability_threshold: float = C_STAR
    fixed_timestamp: str | None = None


@dataclass(frozen=True)
class ChronoEvent:
    event_id: str
    timestamp: str
    sequence_index: int
    actor: str
    event_type: str
    spatial_ref: dict[str, float] | None
    energy_delta: float
    information_value: float
    memory_refs: list[str]
    coherence: float
    payload_hash: str
    provenance: dict[str, str]


@dataclass(frozen=True)
class CausalEdge:
    source_event_id: str
    target_event_id: str
    probability: float
    causal_weight: float
    delay: float
    allowed: bool
    reason: str


@dataclass(frozen=True)
class MemoryEdge:
    source_event_id: str
    target_event_id: str
    memory_weight: float
    shared_refs: list[str]
    drift: float
    lineage_match: bool


@dataclass(frozen=True)
class GeometryEdge:
    source_event_id: str
    target_event_id: str
    observed_distance: float | None
    inferred_distance: float
    signal_delay: float | None
    geometry_weight: float


@dataclass(frozen=True)
class ChronoContradiction:
    contradiction_type: str
    event_ids: list[str]
    severity: str
    message: str


@dataclass(frozen=True)
class ChronoReconstruction:
    run_id: str
    input_hash: str
    reconstruction_hash: str
    events: list[ChronoEvent]
    causal_edges: list[CausalEdge]
    memory_edges: list[MemoryEdge]
    geometry_edges: list[GeometryEdge]
    contradictions: list[ChronoContradiction]
    entropy_score: float
    information_score: float
    coherence: float
    stable: bool
    seed: int


@dataclass(frozen=True)
class ChronoReceipt:
    receipt_id: str
    run_id: str
    input_hash: str
    reconstruction_hash: str
    event_count: int
    causal_edges: int
    memory_edges: int
    geometry_edges: int
    coherence: float
    stable: bool
    entropy_score: float
    contradiction_count: int
    selected_model: str
    seed: int
    created_at: str
