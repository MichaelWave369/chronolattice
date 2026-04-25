from __future__ import annotations

from typing import Any

from .compat import wrap_artifact
from .constants import ARTIFACT_KIND_BRIDGE_REPORT, SCHEMA_VERSION
from .hashing import stable_hash
from .models import ChronoReconstruction

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def count_by(items: list[dict] | list[Any], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        if isinstance(item, dict):
            value = item.get(key)
        else:
            value = getattr(item, key, None)
        if value is None:
            continue
        normalized = str(value)
        counts[normalized] = counts.get(normalized, 0) + 1
    return {name: counts[name] for name in sorted(counts)}


def bridge_gap_report_id(reconstruction: ChronoReconstruction) -> str:
    severity_counts = {"low": 0, "medium": 0, "high": 0}
    for gap in reconstruction.bridge_gaps:
        if gap.severity in severity_counts:
            severity_counts[gap.severity] += 1
    gap_type_counts = count_by(reconstruction.bridge_gaps, "gap_type")
    payload = {
        "run_id": reconstruction.run_id,
        "reconstruction_hash": reconstruction.reconstruction_hash,
        "total_bridge_gaps": len(reconstruction.bridge_gaps),
        "severity_counts": severity_counts,
        "gap_type_counts": gap_type_counts,
    }
    return stable_hash(payload)[:16]


def _operator_summary(severity_counts: dict[str, int], total_bridge_gaps: int) -> str:
    if total_bridge_gaps == 0:
        return "No bridge gaps detected. Timeline continuity appears stable under the selected bridge thresholds."
    if severity_counts["high"] > 0:
        return "High-priority bridge gaps detected. Review missing transition evidence before trusting this reconstruction."
    if severity_counts["medium"] > 0:
        return "Bridge gaps detected. Timeline may require transition, handoff, memory, or provenance events."
    return "Low-severity bridge gaps detected. Timeline is mostly continuous with minor transition questions."


def _recommendations(severity_counts: dict[str, int], gap_type_counts: dict[str, int], total_bridge_gaps: int) -> list[str]:
    if total_bridge_gaps == 0:
        return ["No action required."]

    recommendations: list[str] = []
    if severity_counts["high"] > 0:
        recommendations.append("Review high-severity bridge gaps first.")
    if "provenance_gap" in gap_type_counts:
        recommendations.append("Add provenance receipts for result, artifact, commit, or receipt events.")
    if "event_type_jump" in gap_type_counts:
        recommendations.append("Add planning/build transition events between idea and result states.")
    if "actor_discontinuity" in gap_type_counts:
        recommendations.append("Add handoff events when actor changes share memory context.")
    if "memory_discontinuity" in gap_type_counts:
        recommendations.append("Add memory bridge or reset markers.")
    if "coherence_drop" in gap_type_counts:
        recommendations.append("Add stabilization events before coherence collapse points.")
    if "geometry_causal_tension" in gap_type_counts:
        recommendations.append("Add geometry bridge evidence explaining strong causality over weak adjacency.")
    return recommendations


def build_bridge_gap_report(reconstruction: ChronoReconstruction) -> dict:
    severity_counts = {"low": 0, "medium": 0, "high": 0}
    for gap in reconstruction.bridge_gaps:
        if gap.severity in severity_counts:
            severity_counts[gap.severity] += 1

    gap_type_counts = count_by(reconstruction.bridge_gaps, "gap_type")
    suggested_event_type_counts = count_by(reconstruction.bridge_gaps, "suggested_event_type")

    events_by_id = {event.event_id: event for event in reconstruction.events}
    actor_counts: dict[str, int] = {}
    for gap in reconstruction.bridge_gaps:
        source = events_by_id.get(gap.source_event_id)
        target = events_by_id.get(gap.target_event_id)
        for event in (source, target):
            if event is None:
                continue
            actor = event.actor
            actor_counts[actor] = actor_counts.get(actor, 0) + 1
    actor_gap_counts = {name: actor_counts[name] for name in sorted(actor_counts)}

    ordered = sorted(
        reconstruction.bridge_gaps,
        key=lambda gap: (
            _SEVERITY_ORDER.get(gap.severity, 99),
            -gap.score,
            gap.gap_id,
        ),
    )
    top_bridge_gaps = [
        {
            "gap_id": gap.gap_id,
            "source_event_id": gap.source_event_id,
            "target_event_id": gap.target_event_id,
            "gap_type": gap.gap_type,
            "severity": gap.severity,
            "score": gap.score,
            "missing_bridge_hint": gap.missing_bridge_hint,
            "suggested_event_type": gap.suggested_event_type,
        }
        for gap in ordered[:10]
    ]

    total_bridge_gaps = len(reconstruction.bridge_gaps)
    operator_summary = _operator_summary(severity_counts, total_bridge_gaps)
    recommendations = _recommendations(severity_counts, gap_type_counts, total_bridge_gaps)

    return {
        "report_id": bridge_gap_report_id(reconstruction),
        "run_id": reconstruction.run_id,
        "reconstruction_hash": reconstruction.reconstruction_hash,
        "bridge_profile": reconstruction.bridge_profile,
        "bridge_threshold_mode": reconstruction.bridge_threshold_mode,
        "bridge_thresholds": reconstruction.bridge_thresholds,
        "bridge_threshold_provenance": reconstruction.bridge_threshold_provenance,
        "coherence": reconstruction.coherence,
        "stable": reconstruction.stable,
        "total_bridge_gaps": total_bridge_gaps,
        "severity_counts": severity_counts,
        "gap_type_counts": gap_type_counts,
        "suggested_event_type_counts": suggested_event_type_counts,
        "actor_gap_counts": actor_gap_counts,
        "top_bridge_gaps": top_bridge_gaps,
        "operator_summary": operator_summary,
        "recommendations": recommendations,
    }


def bridge_report_artifact(reconstruction: ChronoReconstruction) -> dict:
    payload = build_bridge_gap_report(reconstruction)
    return wrap_artifact(ARTIFACT_KIND_BRIDGE_REPORT, SCHEMA_VERSION, payload)
