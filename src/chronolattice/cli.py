from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any

from .adapters.phios import to_phios_payload
from .constants import VERSION
from .engine import ChronoLatticeEngine
from .models import ChronoConfig, ChronoReconstruction


def _write_json(path: str | Path, payload: Any) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _load_reconstruction(path: str | Path) -> ChronoReconstruction:
    data = _load_json(path)
    return ChronoReconstruction(**data)


def _validate_input(path: str | Path) -> tuple[bool, str]:
    required = {"run_id", "events"}
    event_required = {
        "event_id",
        "timestamp",
        "sequence_index",
        "actor",
        "event_type",
        "energy_delta",
        "information_value",
        "memory_refs",
        "coherence",
        "payload_hash",
        "provenance",
    }
    try:
        data = _load_json(path)
    except Exception as exc:
        return False, f"Invalid JSON: {exc}"
    missing = required - set(data.keys())
    if missing:
        return False, f"Missing top-level fields: {sorted(missing)}"
    for idx, ev in enumerate(data.get("events", [])):
        m = event_required - set(ev.keys())
        if m:
            return False, f"Event index {idx} missing fields: {sorted(m)}"
    return True, "ok"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chronolattice")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("version")
    v = sub.add_parser("validate")
    v.add_argument("path")

    r = sub.add_parser("reconstruct")
    r.add_argument("path")
    r.add_argument("--seed", type=int, default=369369)
    r.add_argument("--out", required=True)

    receipt = sub.add_parser("receipt")
    receipt.add_argument("reconstruction_path")
    receipt.add_argument("--out", required=True)

    payload = sub.add_parser("phios-payload")
    payload.add_argument("reconstruction_path")
    payload.add_argument("--out", required=True)

    inspect = sub.add_parser("inspect")
    inspect.add_argument("reconstruction_path")

    contradictions = sub.add_parser("contradictions")
    contradictions.add_argument("reconstruction_path")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "version":
        print(VERSION)
        return 0

    if args.command == "validate":
        ok, msg = _validate_input(args.path)
        print(msg)
        return 0 if ok else 1

    if args.command == "reconstruct":
        engine = ChronoLatticeEngine(ChronoConfig(seed=args.seed))
        recon = engine.reconstruct_from_file(args.path)
        _write_json(args.out, asdict(recon))
        return 0

    if args.command == "receipt":
        data = _load_json(args.reconstruction_path)
        engine = ChronoLatticeEngine(ChronoConfig(seed=int(data.get("seed", 369369))))
        recon = ChronoReconstruction(**data)
        receipt = engine.emit_receipt(recon)
        _write_json(args.out, asdict(receipt))
        return 0

    if args.command == "phios-payload":
        recon = ChronoReconstruction(**_load_json(args.reconstruction_path))
        _write_json(args.out, to_phios_payload(recon))
        return 0

    if args.command == "inspect":
        data = _load_json(args.reconstruction_path)
        print(json.dumps({
            "run_id": data.get("run_id"),
            "event_count": len(data.get("events", [])),
            "coherence": data.get("coherence"),
            "stable": data.get("stable"),
        }, indent=2, sort_keys=True))
        return 0

    if args.command == "contradictions":
        data = _load_json(args.reconstruction_path)
        print(json.dumps(data.get("contradictions", []), indent=2, sort_keys=True))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
