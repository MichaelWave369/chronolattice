import json
from pathlib import Path

import pytest

from chronolattice.constants import ARTIFACT_KIND_RECONSTRUCTION
from chronolattice.migrations import (
    artifact_migration_status,
    latest_schema_version,
    list_supported_schema_versions,
    migrate_artifact,
    migration_path,
    needs_migration,
)
from chronolattice.models import ChronoConfig
from chronolattice.reconstruct import reconstruct
from chronolattice.serialization import reconstruction_to_dict


def _wrapped_reconstruction() -> dict:
    data = json.loads(Path("data/examples/simple_timeline.json").read_text(encoding="utf-8"))
    reconstruction = reconstruct(data["events"], ChronoConfig(seed=369369))
    return reconstruction_to_dict(reconstruction)


def test_list_supported_schema_versions_returns_expected():
    assert list_supported_schema_versions() == ("0.1",)


def test_latest_schema_version_returns_expected():
    assert latest_schema_version() == "0.1"


def test_needs_migration_for_current_schema_is_false():
    assert needs_migration("0.1") is False


def test_migration_path_same_version_is_empty():
    assert migration_path("0.1", "0.1") == []


def test_migration_path_unsupported_raises_value_error():
    with pytest.raises(ValueError):
        migration_path("0.0", "0.1")


def test_migrate_artifact_returns_equal_but_not_same_for_current_wrapped_artifact():
    wrapped = _wrapped_reconstruction()
    migrated = migrate_artifact(wrapped)
    assert migrated == wrapped
    assert migrated is not wrapped


def test_migrate_artifact_does_not_mutate_input():
    wrapped = _wrapped_reconstruction()
    original = json.loads(json.dumps(wrapped))
    _ = migrate_artifact(wrapped)
    assert wrapped == original


def test_artifact_migration_status_for_wrapped_current_reconstruction():
    wrapped = _wrapped_reconstruction()
    status = artifact_migration_status(wrapped)
    assert status["kind"] == ARTIFACT_KIND_RECONSTRUCTION
    assert status["schema_version"] == "0.1"
    assert status["supported"] is True
    assert status["needs_migration"] is False
    assert status["migration_path"] == []
    assert status["error"] is None


def test_artifact_migration_status_for_legacy_flat_reconstruction():
    wrapped = _wrapped_reconstruction()
    legacy = wrapped["payload"]
    status = artifact_migration_status(legacy)
    assert status["kind"] is None
    assert status["schema_version"] is None
    assert status["supported"] is False
    assert "legacy flat payload" in (status["error"] or "").lower()
