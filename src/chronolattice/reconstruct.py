from __future__ import annotations

from dataclasses import asdict
from typing import Any

from .causality import build_causal_edges, detect_causal_contradictions
from .coherence import is_stable, score_coherence
from .constants import DEFAULT_SEED
from .entropy import score_entropy
from .geometry import build_geometry_edges
from .hashing import stable_hash
from .information import score_information
from .memory import build_memory_edges, detect_memory_contradictions
from .models import ChronoConfig, ChronoEvent, ChronoReconstruction


def normalize_events(raw_events: list[ChronoEvent] | list[dict[str, Any]]) -> list[ChronoEvent]:
    normalized: list[ChronoEvent] = []
    for item in raw_events:
        if isinstance(item, ChronoEvent):
            normalized.append(item)
        else:
            normalized.append(
                ChronoEvent(
                    event_id=item["event_id"],
                    timestamp=item["timestamp"],
                    sequence_index=int(item["sequence_index"]),
                    actor=item["actor"],
                    event_type=item["event_type"],
                    spatial_ref=item.get("spatial_ref"),
                    energy_delta=float(item.get("energy_delta", 0.0)),
                    information_value=float(item.get("information_value", 0.0)),
                    memory_refs=list(item.get("memory_refs", [])),
                    coherence=float(item.get("coherence", 0.0)),
                    payload_hash=item.get("payload_hash") or stable_hash(item.get("payload", {})),
                    provenance=dict(item.get("provenance", {})),
                )
            )
    return sorted(normalized, key=lambda e: e.sequence_index)


def reconstruct(events: list[ChronoEvent] | list[dict[str, Any]], config: ChronoConfig) -> ChronoReconstruction:
    normalized_events = normalize_events(events)
    input_hash = stable_hash({"events": normalized_events, "seed": config.seed})
    causal_edges = build_causal_edges(normalized_events, config)
    memory_edges = build_memory_edges(normalized_events, config)
    geometry_edges = build_geometry_edges(normalized_events, causal_edges, memory_edges, config)
    contradictions = detect_causal_contradictions(normalized_events, causal_edges)
    contradictions.extend(detect_memory_contradictions(normalized_events, memory_edges))
    entropy_score = score_entropy(normalized_events)
    information_score = score_information(normalized_events)
    coherence = score_coherence(
        causal_edges,
        memory_edges,
        geometry_edges,
        entropy_score,
        information_score,
        contradictions,
        config,
    )
    stable = is_stable(coherence, config)

    payload = {
        "events": normalized_events,
        "causal_edges": causal_edges,
        "memory_edges": memory_edges,
        "geometry_edges": geometry_edges,
        "contradictions": contradictions,
        "entropy_score": entropy_score,
        "information_score": information_score,
        "coherence": coherence,
        "stable": stable,
        "seed": config.seed,
    }
    reconstruction_hash = stable_hash(payload)
    run_id = stable_hash({"input_hash": input_hash, "seed": config.seed})[:16]

    return ChronoReconstruction(
        run_id=run_id,
        input_hash=input_hash,
        reconstruction_hash=reconstruction_hash,
        events=normalized_events,
        causal_edges=causal_edges,
        memory_edges=memory_edges,
        geometry_edges=geometry_edges,
        contradictions=contradictions,
        entropy_score=entropy_score,
        information_score=information_score,
        coherence=coherence,
        stable=stable,
        seed=config.seed,
    )
