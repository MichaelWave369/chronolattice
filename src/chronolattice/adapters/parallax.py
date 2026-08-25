from __future__ import annotations

from typing import Any


def timeline_to_parallax_events(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    run_id = str(timeline["run_id"])
    output: list[dict[str, Any]] = []
    previous_event_id: str | None = None
    for native in timeline.get("events", []):
        timestamp = str(native["timestamp"])
        output.append(
            {
                "schema": "parallax.event.v1",
                "kind": str(native["event_type"]),
                "schemaVersion": "1",
                "eventId": str(native["event_id"]),
                "occurredAt": timestamp,
                "recordedAt": timestamp,
                "producer": "ChronoLattice",
                "sessionOrRunId": run_id,
                "actorRefs": [str(native["actor"])],
                "subjectRefs": [str(item) for item in native.get("memory_refs", [])],
                "payload": {
                    "native": native,
                    "_adapter": {
                        "recordedAtSource": "native timestamp fallback",
                        "assumption": "Native example does not distinguish occurrence and recording time.",
                    },
                },
                "parentEventRefs": [previous_event_id] if previous_event_id else [],
                "receiptRefs": [],
            }
        )
        previous_event_id = str(native["event_id"])
    return output
