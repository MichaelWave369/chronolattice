from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from .compat import assert_supported_artifact, wrap_artifact
from .constants import ARTIFACT_KIND_RECEIPT, ARTIFACT_KIND_RECONSTRUCTION, SCHEMA_VERSION
from .schema import is_legacy_receipt_dict, is_legacy_reconstruction_dict
from .serialization import load_json, write_json


def detect_legacy_artifact_kind(data: dict) -> str | None:
    if not isinstance(data, dict):
        return None
    if {"kind", "schema_version", "payload"}.issubset(data.keys()):
        kind = data.get("kind")
        return kind if isinstance(kind, str) else None
    if is_legacy_reconstruction_dict(data):
        return ARTIFACT_KIND_RECONSTRUCTION
    if is_legacy_receipt_dict(data):
        return ARTIFACT_KIND_RECEIPT
    return None


def normalize_artifact_envelope(data: dict, kind: str | None = None) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Artifact must be a JSON object.")

    raw = deepcopy(data)
    envelope = {"kind", "schema_version", "payload"}
    if envelope.intersection(raw.keys()):
        if kind is None:
            current_kind = raw.get("kind")
            if not isinstance(current_kind, str):
                raise ValueError("Wrapped artifact has invalid 'kind'.")
            assert_supported_artifact(raw, current_kind)
            return deepcopy(raw)

        assert_supported_artifact(raw, kind)
        return deepcopy(raw)

    detected_kind = detect_legacy_artifact_kind(raw)
    if detected_kind is None:
        raise ValueError("Unable to detect legacy artifact kind for normalization.")

    if kind is not None and kind != detected_kind:
        raise ValueError(f"Provided kind '{kind}' does not match detected kind '{detected_kind}'.")

    target_kind = kind or detected_kind
    return wrap_artifact(target_kind, SCHEMA_VERSION, deepcopy(raw))


def normalize_artifact_file(path: str | Path, out: str | Path | None = None) -> dict:
    data = load_json(path)
    normalized = normalize_artifact_envelope(data)
    if out is not None:
        write_json(out, normalized)
    return normalized
