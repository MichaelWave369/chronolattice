import json
from pathlib import Path

from chronolattice.hashing import stable_hash
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import reconstruct
from chronolattice.receipts import emit_receipt
from chronolattice.serialization import receipt_from_dict, receipt_to_dict


def test_receipt_round_trip_deterministic():
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    config = ChronoConfig(seed=369369, fixed_timestamp="2026-04-24T00:00:00Z")
    reconstruction = reconstruct(data["events"], config)
    original_receipt = emit_receipt(reconstruction, config)

    serialized = receipt_to_dict(original_receipt)
    restored = receipt_from_dict(serialized)

    assert stable_hash(original_receipt) == stable_hash(restored)
    assert original_receipt.receipt_id == restored.receipt_id
