from __future__ import annotations

from .constants import SCHEMA_VERSION

_SUPPORTED_SCHEMA_VERSIONS = {SCHEMA_VERSION}


def is_supported_schema_version(version: str) -> bool:
    return version in _SUPPORTED_SCHEMA_VERSIONS


def wrap_artifact(kind: str, schema_version: str, payload: dict) -> dict:
    return {
        "kind": kind,
        "schema_version": schema_version,
        "payload": dict(payload),
    }


def assert_supported_artifact(data: dict, expected_kind: str) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Artifact must be a JSON object.")
    if "kind" not in data:
        raise ValueError("Artifact envelope missing 'kind'.")
    if "schema_version" not in data:
        raise ValueError("Artifact envelope missing 'schema_version'.")
    if "payload" not in data:
        raise ValueError("Artifact envelope missing 'payload'.")

    kind = data["kind"]
    if kind != expected_kind:
        raise ValueError(f"Artifact kind mismatch: expected '{expected_kind}', got '{kind}'.")

    schema_version = data["schema_version"]
    if not is_supported_schema_version(schema_version):
        raise ValueError(f"Unsupported schema_version '{schema_version}'.")

    payload = data["payload"]
    if not isinstance(payload, dict):
        raise ValueError("Artifact payload must be an object.")
    return dict(payload)


def unwrap_artifact(data: dict, expected_kind: str) -> dict:
    envelope_keys = {"kind", "schema_version", "payload"}
    if envelope_keys.intersection(data.keys()):
        return assert_supported_artifact(dict(data), expected_kind)
    return dict(data)
