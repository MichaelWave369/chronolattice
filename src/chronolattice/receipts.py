from __future__ import annotations

from datetime import datetime, timezone

from .hashing import stable_hash
from .models import ChronoConfig, ChronoReceipt, ChronoReconstruction


def emit_receipt(reconstruction: ChronoReconstruction, config: ChronoConfig) -> ChronoReceipt:
    created_at = config.fixed_timestamp or datetime.now(timezone.utc).isoformat()
    receipt_material = {
        "run_id": reconstruction.run_id,
        "input_hash": reconstruction.input_hash,
        "reconstruction_hash": reconstruction.reconstruction_hash,
        "seed": reconstruction.seed,
        "selected_model": config.selected_model,
    }
    receipt_id = stable_hash(receipt_material)
    return ChronoReceipt(
        receipt_id=receipt_id,
        run_id=reconstruction.run_id,
        input_hash=reconstruction.input_hash,
        reconstruction_hash=reconstruction.reconstruction_hash,
        event_count=len(reconstruction.events),
        causal_edges=len(reconstruction.causal_edges),
        memory_edges=len(reconstruction.memory_edges),
        geometry_edges=len(reconstruction.geometry_edges),
        coherence=reconstruction.coherence,
        stable=reconstruction.stable,
        entropy_score=reconstruction.entropy_score,
        contradiction_count=len(reconstruction.contradictions),
        selected_model=config.selected_model,
        seed=reconstruction.seed,
        created_at=created_at,
    )
