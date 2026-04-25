from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters.phios import to_phios_payload
from .constants import VERSION
from .engine import ChronoLatticeEngine
from .models import ChronoConfig
from .schema import validate_event_dict
from .serialization import (
    load_json,
    receipt_to_dict,
    reconstruction_from_dict,
    reconstruction_to_dict,
    write_json,
)


def _validate_input(path: str | Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        data = load_json(path)
    except Exception as exc:
        return False, [f"Invalid JSON: {exc}"]

    for field in ["run_id", "events"]:
        if field not in data:
            errors.append(f"input missing required field: {field}")

    events = data.get("events")
    if isinstance(events, list):
        for idx, event in enumerate(events):
            for err in validate_event_dict(event):
                errors.append(f"events[{idx}]: {err}")
    else:
        errors.append("input.events must be a list")

    return (len(errors) == 0), errors


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
        ok, errors = _validate_input(args.path)
        if ok:
            print("ok")
            return 0
        for err in errors:
            print(err)
        return 1

    if args.command == "reconstruct":
        engine = ChronoLatticeEngine(ChronoConfig(seed=args.seed))
        recon = engine.reconstruct_from_file(args.path)
        write_json(args.out, reconstruction_to_dict(recon))
        return 0

    if args.command == "receipt":
        reconstruction = reconstruction_from_dict(load_json(args.reconstruction_path))
        engine = ChronoLatticeEngine(ChronoConfig(seed=reconstruction.seed))
        receipt = engine.emit_receipt(reconstruction)
        write_json(args.out, receipt_to_dict(receipt))
        return 0

    if args.command == "phios-payload":
        reconstruction = reconstruction_from_dict(load_json(args.reconstruction_path))
        write_json(args.out, to_phios_payload(reconstruction))
        return 0

    if args.command == "inspect":
        reconstruction = reconstruction_from_dict(load_json(args.reconstruction_path))
        print(
            json.dumps(
                {
                    "run_id": reconstruction.run_id,
                    "event_count": len(reconstruction.events),
                    "coherence": reconstruction.coherence,
                    "stable": reconstruction.stable,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0

    if args.command == "contradictions":
        reconstruction = reconstruction_from_dict(load_json(args.reconstruction_path))
        print(json.dumps([c.__dict__ for c in reconstruction.contradictions], indent=2, sort_keys=True))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
