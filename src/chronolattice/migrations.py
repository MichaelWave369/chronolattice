from __future__ import annotations

from copy import deepcopy

from .constants import SCHEMA_VERSION, SUPPORTED_SCHEMA_VERSIONS


def list_supported_schema_versions() -> tuple[str, ...]:
    return SUPPORTED_SCHEMA_VERSIONS


def latest_schema_version() -> str:
    return SCHEMA_VERSION


def needs_migration(schema_version: str) -> bool:
    return schema_version != latest_schema_version()


def migration_path(from_version: str, to_version: str | None = None) -> list[str]:
    target = to_version or latest_schema_version()
    if from_version == target:
        return []
    if from_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(f"Unsupported source schema_version '{from_version}'.")
    if target not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(f"Unsupported target schema_version '{target}'.")
    raise ValueError(f"No migration path available from {from_version} to {target}.")


def migrate_artifact(data: dict, target_version: str | None = None) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Artifact must be a JSON object.")

    for field in ("kind", "schema_version", "payload"):
        if field not in data:
            raise ValueError(f"Wrapped artifact is required; missing '{field}'.")

    kind = data.get("kind")
    schema_version = data.get("schema_version")
    payload = data.get("payload")

    if not isinstance(kind, str):
        raise ValueError("Artifact 'kind' must be a string.")
    if not isinstance(schema_version, str):
        raise ValueError("Artifact 'schema_version' must be a string.")
    if not isinstance(payload, dict):
        raise ValueError("Artifact 'payload' must be an object.")

    target = target_version or latest_schema_version()
    if target not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(f"Unsupported target schema_version '{target}'.")
    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        raise ValueError(f"Unsupported source schema_version '{schema_version}'.")

    if schema_version == target:
        return deepcopy(data)

    # Conservative stub: no migrations currently defined.
    migration_path(schema_version, target)
    raise ValueError(f"No migration available from {schema_version} to {target}.")


def artifact_migration_status(data: dict) -> dict:
    status = {
        "kind": None,
        "schema_version": None,
        "latest_schema_version": latest_schema_version(),
        "supported": False,
        "needs_migration": False,
        "migration_path": [],
        "error": None,
    }

    if not isinstance(data, dict):
        status["error"] = "Artifact must be a JSON object."
        return status

    envelope_keys = {"kind", "schema_version", "payload"}
    if not envelope_keys.issubset(data.keys()):
        status["error"] = (
            "Legacy flat payload detected: load-compatible, but not migration-addressable without an envelope."
        )
        return status

    status["kind"] = data.get("kind") if isinstance(data.get("kind"), str) else None
    status["schema_version"] = data.get("schema_version") if isinstance(data.get("schema_version"), str) else None

    if not isinstance(data.get("payload"), dict):
        status["error"] = "Artifact payload must be an object."
        return status

    schema_version = data.get("schema_version")
    if not isinstance(schema_version, str):
        status["error"] = "Artifact schema_version must be a string."
        return status

    if schema_version not in SUPPORTED_SCHEMA_VERSIONS:
        status["error"] = f"Unsupported schema_version '{schema_version}'."
        return status

    status["supported"] = True
    status["needs_migration"] = needs_migration(schema_version)
    try:
        status["migration_path"] = migration_path(schema_version, latest_schema_version())
    except ValueError as exc:
        status["supported"] = False
        status["error"] = str(exc)

    if status["supported"]:
        status["error"] = None

    return status
