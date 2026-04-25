from __future__ import annotations

from ..constants import C_STAR
from ..models import ChronoReconstruction


def to_phios_payload(reconstruction: ChronoReconstruction) -> dict:
    nodes = [
        {
            "id": e.event_id,
            "t": e.timestamp,
            "actor": e.actor,
            "event_type": e.event_type,
            "coherence": e.coherence,
        }
        for e in reconstruction.events
    ]
    edges = [
        {
            "kind": "causal",
            "source": e.source_event_id,
            "target": e.target_event_id,
            "weight": e.causal_weight,
            "allowed": e.allowed,
        }
        for e in reconstruction.causal_edges
    ]
    edges.extend(
        {
            "kind": "memory",
            "source": e.source_event_id,
            "target": e.target_event_id,
            "weight": e.memory_weight,
        }
        for e in reconstruction.memory_edges
    )
    edges.extend(
        {
            "kind": "geometry",
            "source": e.source_event_id,
            "target": e.target_event_id,
            "weight": e.geometry_weight,
        }
        for e in reconstruction.geometry_edges
    )
    edges.extend(
        {
            "kind": "bridge_gap",
            "source": g.source_event_id,
            "target": g.target_event_id,
            "weight": g.score,
            "gap_type": g.gap_type,
            "severity": g.severity,
        }
        for g in reconstruction.bridge_gaps
    )

    bridge_gaps = [
        {
            "id": g.gap_id,
            "source": g.source_event_id,
            "target": g.target_event_id,
            "type": g.gap_type,
            "severity": g.severity,
            "score": g.score,
            "hint": g.missing_bridge_hint,
            "suggested_event_type": g.suggested_event_type,
        }
        for g in reconstruction.bridge_gaps
    ]

    return {
        "kind": "chronolattice.phios.payload.v0_1",
        "nodes": nodes,
        "edges": edges,
        "bridge_gaps": bridge_gaps,
        "field": {
            "global_coherence": reconstruction.coherence,
            "stable": reconstruction.stable,
            "c_star": C_STAR,
            "bridge_profile": reconstruction.bridge_profile,
        },
    }
