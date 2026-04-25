import pytest

from chronolattice.compat import unwrap_artifact, wrap_artifact


def test_wrap_artifact_shape():
    wrapped = wrap_artifact("chronolattice.reconstruction", "0.1", {"x": 1})
    assert wrapped["kind"] == "chronolattice.reconstruction"
    assert wrapped["schema_version"] == "0.1"
    assert wrapped["payload"] == {"x": 1}


def test_unwrap_wrapped_payload():
    payload = unwrap_artifact(
        {
            "kind": "chronolattice.reconstruction",
            "schema_version": "0.1",
            "payload": {"run_id": "r"},
        },
        "chronolattice.reconstruction",
    )
    assert payload == {"run_id": "r"}


def test_unwrap_legacy_payload():
    legacy = {"run_id": "r", "input_hash": "i"}
    payload = unwrap_artifact(legacy, "chronolattice.reconstruction")
    assert payload == legacy


def test_unwrap_raises_on_wrong_kind():
    with pytest.raises(ValueError):
        unwrap_artifact(
            {
                "kind": "chronolattice.receipt",
                "schema_version": "0.1",
                "payload": {"x": 1},
            },
            "chronolattice.reconstruction",
        )


def test_unwrap_raises_on_unsupported_schema_version():
    with pytest.raises(ValueError):
        unwrap_artifact(
            {
                "kind": "chronolattice.reconstruction",
                "schema_version": "9.9",
                "payload": {"x": 1},
            },
            "chronolattice.reconstruction",
        )
