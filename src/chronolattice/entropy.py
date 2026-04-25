from __future__ import annotations

from .models import ChronoEvent


def score_entropy(events: list[ChronoEvent]) -> float:
    if not events:
        return 0.0
    unique_types = len({e.event_type for e in events}) / len(events)
    unique_actors = len({e.actor for e in events}) / len(events)
    refs = [r for e in events for r in e.memory_refs]
    unique_refs = len(set(refs)) / max(len(refs), 1)
    score = 0.4 * unique_types + 0.3 * unique_actors + 0.3 * unique_refs
    return max(0.0, min(score, 1.0))
