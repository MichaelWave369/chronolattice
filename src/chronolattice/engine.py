from __future__ import annotations

import json
from pathlib import Path

from .adapters.phios import to_phios_payload
from .constants import DEFAULT_SEED
from .models import ChronoConfig, ChronoEvent, ChronoReconstruction
from .reconstruct import reconstruct
from .profiles import resolve_bridge_config
from .receipts import emit_receipt


class ChronoLatticeEngine:
    def __init__(self, config: ChronoConfig | None = None):
        base = config or ChronoConfig(seed=DEFAULT_SEED)
        self.config = resolve_bridge_config(base)

    def reconstruct_from_file(self, path: str | Path, cli_manual_fields: set[str] | None = None) -> ChronoReconstruction:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        run_id = raw.get("run_id")
        seed = int(raw.get("seed", self.config.seed))
        events = raw.get("events", [])
        config = ChronoConfig(
            seed=seed,
            selected_model=self.config.selected_model,
            stability_threshold=self.config.stability_threshold,
            fixed_timestamp=self.config.fixed_timestamp,
            bridge_profile=self.config.bridge_profile,
            bridge_threshold_mode=self.config.bridge_threshold_mode,
            bridge_gap_threshold=self.config.bridge_gap_threshold,
            coherence_drop_threshold=self.config.coherence_drop_threshold,
            energy_jump_threshold=self.config.energy_jump_threshold,
            information_jump_threshold=self.config.information_jump_threshold,
        )
        recon = reconstruct(events, config, cli_manual_fields=cli_manual_fields)
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
                bridge_gaps=recon.bridge_gaps,
                entropy_score=recon.entropy_score,
                information_score=recon.information_score,
                coherence=recon.coherence,
                stable=recon.stable,
                seed=recon.seed,
                bridge_profile=recon.bridge_profile,
                bridge_threshold_mode=recon.bridge_threshold_mode,
                bridge_thresholds=recon.bridge_thresholds,
                bridge_threshold_provenance=recon.bridge_threshold_provenance,
            )
        return recon

    def reconstruct_events(
        self,
        events: list[ChronoEvent] | list[dict],
        cli_manual_fields: set[str] | None = None,
    ) -> ChronoReconstruction:
        return reconstruct(events, self.config, cli_manual_fields=cli_manual_fields)

    def emit_receipt(self, reconstruction: ChronoReconstruction):
        return emit_receipt(reconstruction, self.config)

    def phios_payload(self, reconstruction: ChronoReconstruction) -> dict:
        return to_phios_payload(reconstruction)
