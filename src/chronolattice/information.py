from __future__ import annotations

from .models import ChronoEvent


def score_information(events: list[ChronoEvent]) -> float:
    if not events:
        return 0.0
    avg = sum(max(0.0, min(e.information_value, 1.0)) for e in events) / len(events)
    return max(0.0, min(avg, 1.0))
