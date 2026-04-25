from __future__ import annotations

from ..models import ChronoEvent


def from_sml_cells(cells: list[dict]) -> list[ChronoEvent]:
    raise NotImplementedError("SML adapter is not implemented in v0.1; use normalized event traces for now.")
