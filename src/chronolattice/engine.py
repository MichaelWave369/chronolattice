from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .adapters.phios import to_phios_payload
from .constants import DEFAULT_SEED
from .models import ChronoConfig, ChronoEvent, ChronoReconstruction
from .reconstruct import normalize_events, reconstruct
from .receipts import emit_receipt


class ChronoLatticeEngine:
    def __init__(self, config: ChronoConfig | None = None):
        self.config = config or ChronoConfig(seed=DEFAULT_SEED)

    def reconstruct_from_file(self, path: str | Path) -> ChronoReconstruction:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        run_id = raw.get("run_id")
        seed = int(raw.get("seed", self.config.seed))
        events = raw.get("events", [])
        recon = reconstruct(events, ChronoConfig(seed=seed, selected_model=self.config.selected_model, stability_threshold=self.config.stability_threshold, fixed_timestamp=self.config.fixed_timestamp))
        if run_id:
            return ChronoReconstruction(
                run_id=run_id,
                input_hash=recon.input_hash,
                reconstruction_hash=recon.reconstruction_hash,
                events=recon.events,
                causal_edges=recon.causal_edges,
                memory_edges=recon.memory_edges,
                geometry_edges=recon.geometry_edges,
                contradictions=recon.contradictions,
                entropy_score=recon.entropy_score,
                information_score=recon.information_score,
                coherence=recon.coherence,
                stable=recon.stable,
                seed=recon.seed,
            )
        return recon

    def reconstruct_events(self, events: list[ChronoEvent] | list[dict]) -> ChronoReconstruction:
        return reconstruct(events, self.config)

    def emit_receipt(self, reconstruction: ChronoReconstruction):
        return emit_receipt(reconstruction, self.config)

    def phios_payload(self, reconstruction: ChronoReconstruction) -> dict:
        return to_phios_payload(reconstruction)
