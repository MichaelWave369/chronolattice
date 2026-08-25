from chronolattice.adapters.parallax import timeline_to_parallax_events


def test_timeline_projection_is_ordered_and_explicit_about_time_fallback():
    timeline = {
        "run_id": "r1",
        "events": [
            {"event_id":"e1","timestamp":"2026-01-01T00:00:00Z","actor":"a","event_type":"observe","memory_refs":[]},
            {"event_id":"e2","timestamp":"2026-01-01T00:00:01Z","actor":"a","event_type":"observe","memory_refs":["m1"]},
        ],
    }
    out = timeline_to_parallax_events(timeline)
    assert out[0]["parentEventRefs"] == []
    assert out[1]["parentEventRefs"] == ["e1"]
    assert out[0]["occurredAt"] == out[0]["recordedAt"]
    assert out[0]["payload"]["_adapter"]["recordedAtSource"] == "native timestamp fallback"
