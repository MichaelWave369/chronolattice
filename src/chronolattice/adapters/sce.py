from __future__ import annotations

from ..models import ChronoEvent


def from_sce_report(report: dict) -> list[ChronoEvent]:
    raise NotImplementedError("SCE adapter is not implemented in v0.1; use normalized event traces for now.")
