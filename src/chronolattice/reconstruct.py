from __future__ import annotations

from typing import Any

from .bridges import detect_bridge_gaps
from .causality import build_causal_edges, detect_causal_contradictions
from .coherence import is_stable, score_coherence
from .entropy import score_entropy
from .geometry import build_geometry_edges
from .hashing import stable_hash
from .information import score_information
from .memory import build_memory_edges, detect_memory_contradictions
from .models import ChronoConfig, ChronoEvent, ChronoReconstruction
from .profiles import resolve_bridge_config


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
    effective_config = resolve_bridge_config(config)
    normalized_events = normalize_events(events)
    input_hash = stable_hash({"events": normalized_events, "seed": effective_config.seed})
    causal_edges = build_causal_edges(normalized_events, effective_config)
    memory_edges = build_memory_edges(normalized_events, effective_config)
    geometry_edges = build_geometry_edges(normalized_events, causal_edges, memory_edges, effective_config)
    contradictions = detect_causal_contradictions(normalized_events, causal_edges)
    contradictions.extend(detect_memory_contradictions(normalized_events, memory_edges))
    bridge_gaps = detect_bridge_gaps(normalized_events, causal_edges, memory_edges, geometry_edges, effective_config)
    entropy_score = score_entropy(normalized_events)
    information_score = score_information(normalized_events)
    coherence = score_coherence(
        causal_edges,
        memory_edges,
        geometry_edges,
        entropy_score,
        information_score,
        contradictions,
        effective_config,
        bridge_gaps=bridge_gaps,
    )
    stable = is_stable(coherence, effective_config)

    payload = {
        "events": normalized_events,
        "causal_edges": causal_edges,
        "memory_edges": memory_edges,
        "geometry_edges": geometry_edges,
        "contradictions": contradictions,
        "bridge_gaps": bridge_gaps,
        "entropy_score": entropy_score,
        "information_score": information_score,
        "coherence": coherence,
        "stable": stable,
        "seed": effective_config.seed,
        "bridge_profile": effective_config.bridge_profile,
        "bridge_threshold_mode": effective_config.bridge_threshold_mode,
        "bridge_thresholds": {
            "bridge_gap_threshold": effective_config.bridge_gap_threshold,
            "coherence_drop_threshold": effective_config.coherence_drop_threshold,
            "energy_jump_threshold": effective_config.energy_jump_threshold,
            "information_jump_threshold": effective_config.information_jump_threshold,
        },
    }
    reconstruction_hash = stable_hash(payload)
    run_id = stable_hash({"input_hash": input_hash, "seed": effective_config.seed})[:16]

    return ChronoReconstruction(
        run_id=run_id,
        input_hash=input_hash,
        reconstruction_hash=reconstruction_hash,
        events=normalized_events,
        causal_edges=causal_edges,
        memory_edges=memory_edges,
        geometry_edges=geometry_edges,
        contradictions=contradictions,
        bridge_gaps=bridge_gaps,
        entropy_score=entropy_score,
        information_score=information_score,
        coherence=coherence,
        stable=stable,
        seed=effective_config.seed,
        bridge_profile=effective_config.bridge_profile,
        bridge_threshold_mode=effective_config.bridge_threshold_mode,
        bridge_thresholds={
            "bridge_gap_threshold": effective_config.bridge_gap_threshold,
            "coherence_drop_threshold": effective_config.coherence_drop_threshold,
            "energy_jump_threshold": effective_config.energy_jump_threshold,
            "information_jump_threshold": effective_config.information_jump_threshold,
        },
    )
