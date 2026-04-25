from __future__ import annotations

from .hashing import stable_hash
from .models import CausalEdge, ChronoBridgeGap, ChronoConfig, ChronoEvent, GeometryEdge, MemoryEdge


def clamp01(value: float) -> float:
    return max(0.0, min(value, 1.0))


def classify_gap_severity(score: float) -> str:
    score = clamp01(score)
    if score >= 0.80:
        return "high"
    if score >= 0.60:
        return "medium"
    return "low"


def bridge_gap_id(source_event_id: str, target_event_id: str, gap_type: str) -> str:
    return stable_hash({"source": source_event_id, "target": target_event_id, "gap_type": gap_type})[:16]


def detect_bridge_gaps(
    events: list[ChronoEvent],
    causal_edges: list[CausalEdge],
    memory_edges: list[MemoryEdge],
    geometry_edges: list[GeometryEdge],
    config: ChronoConfig,
) -> list[ChronoBridgeGap]:
    by_seq = sorted(events, key=lambda e: e.sequence_index)
    causal_map = {(e.source_event_id, e.target_event_id): e for e in causal_edges}
    seen: set[tuple[str, str, str]] = set()
    gaps: list[ChronoBridgeGap] = []

    def add_gap(
        source: ChronoEvent,
        target: ChronoEvent,
        gap_type: str,
        score: float,
        hint: str,
        evidence: dict[str, float | str | int | bool],
        suggested_event_type: str | None,
    ) -> None:
        bounded = clamp01(score)
        if bounded < config.bridge_gap_threshold:
            return
        key = (source.event_id, target.event_id, gap_type)
        if key in seen:
            return
        seen.add(key)
        gaps.append(
            ChronoBridgeGap(
                gap_id=bridge_gap_id(source.event_id, target.event_id, gap_type),
                source_event_id=source.event_id,
                target_event_id=target.event_id,
                gap_type=gap_type,
                severity=classify_gap_severity(bounded),
                score=bounded,
                missing_bridge_hint=hint,
                evidence=evidence,
                suggested_event_type=suggested_event_type,
            )
        )

    reset_types = {"reset", "start", "new_session"}
    source_types = {"idea", "intent", "question"}
    target_types = {"result", "artifact", "commit", "receipt"}

    for i in range(len(by_seq) - 1):
        source = by_seq[i]
        target = by_seq[i + 1]
        shared_memory = len(set(source.memory_refs).intersection(target.memory_refs))
        prov_text = " ".join(f"{k}:{v}" for k, v in target.provenance.items()).lower()

        if source.actor != target.actor and shared_memory > 0 and ("handoff" not in prov_text and "bridge" not in prov_text):
            score = clamp01(0.55 + 0.20 * min(shared_memory, 1) + 0.25 * abs(source.coherence - target.coherence))
            add_gap(
                source,
                target,
                "actor_discontinuity",
                score,
                "Expected a handoff or bridge event between actors sharing memory.",
                {"shared_memory_refs": shared_memory, "actor_changed": True},
                "handoff",
            )

        if source.actor == target.actor:
            if source.memory_refs and shared_memory == 0 and target.event_type not in reset_types:
                score = clamp01(0.60 + 0.20 * min(len(source.memory_refs), 3) / 3)
                add_gap(
                    source,
                    target,
                    "memory_discontinuity",
                    score,
                    "Expected a memory continuity event or reset marker.",
                    {"source_memory_count": len(source.memory_refs), "shared_memory_refs": shared_memory},
                    "memory_bridge",
                )

            if source.event_type in source_types and target.event_type in target_types:
                score = 0.80
                add_gap(
                    source,
                    target,
                    "event_type_jump",
                    score,
                    "Expected planning/build transition between idea and result.",
                    {"source_event_type": source.event_type, "target_event_type": target.event_type},
                    "build_step",
                )

            if target.event_type in target_types and not any(k in target.provenance for k in ("source", "receipt", "provenance_ref")):
                score = 0.75
                add_gap(
                    source,
                    target,
                    "provenance_gap",
                    score,
                    "Expected provenance receipt or source reference.",
                    {"target_event_type": target.event_type, "provenance_count": len(target.provenance)},
                    "provenance_receipt",
                )

        coherence_drop = source.coherence - target.coherence
        if coherence_drop >= config.coherence_drop_threshold:
            score = clamp01(coherence_drop / max(config.coherence_drop_threshold, 1e-9))
            add_gap(
                source,
                target,
                "coherence_drop",
                score,
                "Expected an intermediate stabilization event before coherence drop.",
                {"coherence_drop": round(coherence_drop, 6)},
                "stabilization",
            )

        energy_jump = abs(target.energy_delta - source.energy_delta)
        if energy_jump >= config.energy_jump_threshold:
            score = clamp01(energy_jump / max(config.energy_jump_threshold, 1e-9))
            add_gap(
                source,
                target,
                "energy_jump",
                score,
                "Expected a load transition event before energy jump.",
                {"energy_jump": round(energy_jump, 6)},
                "load_transition",
            )

        info_jump = abs(target.information_value - source.information_value)
        if info_jump >= config.information_jump_threshold:
            score = clamp01(info_jump / max(config.information_jump_threshold, 1e-9))
            add_gap(
                source,
                target,
                "information_jump",
                score,
                "Expected an explanation or discovery event before information jump.",
                {"information_jump": round(info_jump, 6)},
                "discovery",
            )

    for geo in geometry_edges:
        causal = causal_map.get((geo.source_event_id, geo.target_event_id))
        if not causal or not causal.allowed:
            continue
        if causal.causal_weight >= 0.65 and geo.geometry_weight <= 0.35:
            score = clamp01((causal.causal_weight + (1.0 - geo.geometry_weight)) / 2.0)
            source = next(e for e in by_seq if e.event_id == geo.source_event_id)
            target = next(e for e in by_seq if e.event_id == geo.target_event_id)
            add_gap(
                source,
                target,
                "geometry_causal_tension",
                score,
                "Expected a geometry bridge explaining strong causality over weak adjacency.",
                {
                    "causal_weight": round(causal.causal_weight, 6),
                    "geometry_weight": round(geo.geometry_weight, 6),
                },
                "geometry_bridge",
            )

    gaps.sort(key=lambda g: (g.source_event_id, g.target_event_id, g.gap_type, g.gap_id))
    return gaps
