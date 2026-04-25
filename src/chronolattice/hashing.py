from __future__ import annotations

from dataclasses import asdict, is_dataclass
import hashlib
import json
from typing import Any


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if isinstance(value, dict):
        return {k: to_jsonable(value[k]) for k in sorted(value.keys())}
    if isinstance(value, list):
        return [to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [to_jsonable(v) for v in value]
    return value


def stable_hash(value: Any) -> str:
    payload = json.dumps(to_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
