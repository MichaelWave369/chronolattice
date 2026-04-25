from chronolattice.models import ChronoEvent


def test_chronoevent_constructible():
    event = ChronoEvent(
        event_id="e1",
        timestamp="2026-01-01T00:00:00Z",
        sequence_index=1,
        actor="actor",
        event_type="observe",
        spatial_ref=None,
        energy_delta=0.1,
        information_value=0.2,
        memory_refs=["m1"],
        coherence=0.9,
        payload_hash="hash",
        provenance={"lineage": "l1"},
    )
    assert event.event_id == "e1"
