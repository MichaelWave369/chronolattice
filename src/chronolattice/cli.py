from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path

from .adapters.phios import to_phios_payload
from .compat import wrap_artifact
from .constants import (
    ARTIFACT_KIND_PHIOS_PAYLOAD,
    ARTIFACT_KIND_RECEIPT,
    ARTIFACT_KIND_RECONSTRUCTION,
    SCHEMA_VERSION,
    VERSION,
)
from .engine import ChronoLatticeEngine
from .migrations import artifact_migration_status, migrate_artifact
from .normalization import normalize_artifact_envelope
from .profiles import list_bridge_profiles
from .models import ChronoConfig
from .schema import (
    validate_artifact_envelope,
    validate_event_dict,
    validate_receipt_dict,
    validate_reconstruction_dict,
)
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

    # raw event input shape
    if "events" in data and "run_id" in data and "kind" not in data:
        events = data.get("events")
        if isinstance(events, list):
            for idx, event in enumerate(events):
                for err in validate_event_dict(event):
                    errors.append(f"events[{idx}]: {err}")
        else:
            errors.append("input.events must be a list")
        return (len(errors) == 0), errors

    # wrapped reconstruction
    if data.get("kind") == ARTIFACT_KIND_RECONSTRUCTION:
        errors.extend(validate_artifact_envelope(data, ARTIFACT_KIND_RECONSTRUCTION))
        if not errors:
            errors.extend(validate_reconstruction_dict(data["payload"]))
        return (len(errors) == 0), errors

    # wrapped receipt
    if data.get("kind") == ARTIFACT_KIND_RECEIPT:
        errors.extend(validate_artifact_envelope(data, ARTIFACT_KIND_RECEIPT))
        if not errors:
            errors.extend(validate_receipt_dict(data["payload"]))
        return (len(errors) == 0), errors

    # legacy flat reconstruction
    reconstruction_errors = validate_reconstruction_dict(data)
    if not reconstruction_errors:
        return True, []

    # legacy flat receipt
    receipt_errors = validate_receipt_dict(data)
    if not receipt_errors:
        return True, []

    errors.extend(["Unknown artifact shape."])
    errors.extend([f"reconstruction: {err}" for err in reconstruction_errors])
    errors.extend([f"receipt: {err}" for err in receipt_errors])
    return False, errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="chronolattice")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("version")
    sub.add_parser("bridge-profiles")
    v = sub.add_parser("validate")
    v.add_argument("path")

    r = sub.add_parser("reconstruct")
    r.add_argument("path")
    r.add_argument("--seed", type=int, default=369369)
    r.add_argument("--bridge-profile", choices=["conservative", "balanced", "sensitive", "phi_guardian"], default="balanced")
    r.add_argument("--bridge-threshold-mode", choices=["profile", "manual"], default="profile")
    r.add_argument("--bridge-gap-threshold", type=float)
    r.add_argument("--coherence-drop-threshold", type=float)
    r.add_argument("--energy-jump-threshold", type=float)
    r.add_argument("--information-jump-threshold", type=float)
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

    bridge_gaps = sub.add_parser("bridge-gaps")
    bridge_gaps.add_argument("reconstruction_path")
    bridge_gaps.add_argument("--severity", choices=["low", "medium", "high"])
    bridge_gaps.add_argument("--type", dest="gap_type")

    migration_status = sub.add_parser("migration-status")
    migration_status.add_argument("path")

    migrate = sub.add_parser("migrate")
    migrate.add_argument("path")
    migrate.add_argument("--out", required=True)

    normalize = sub.add_parser("normalize-envelope")
    normalize.add_argument("path")
    normalize.add_argument("--out")
    normalize.add_argument("--kind")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "version":
        print(VERSION)
        return 0

    if args.command == "bridge-profiles":
        profiles = [asdict(p) for p in list_bridge_profiles()]
        print(json.dumps(profiles, indent=2, sort_keys=True))
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
        manual_values = [
            args.bridge_gap_threshold,
            args.coherence_drop_threshold,
            args.energy_jump_threshold,
            args.information_jump_threshold,
        ]
        manual_flags_used = any(v is not None for v in manual_values)
        if args.bridge_threshold_mode == "profile" and manual_flags_used:
            print("Manual threshold flags require --bridge-threshold-mode manual")
            return 1

        config = ChronoConfig(
            seed=args.seed,
            bridge_profile=args.bridge_profile,
            bridge_threshold_mode=args.bridge_threshold_mode,
            bridge_gap_threshold=args.bridge_gap_threshold if args.bridge_gap_threshold is not None else 0.55,
            coherence_drop_threshold=args.coherence_drop_threshold if args.coherence_drop_threshold is not None else 0.20,
            energy_jump_threshold=args.energy_jump_threshold if args.energy_jump_threshold is not None else 0.60,
            information_jump_threshold=args.information_jump_threshold if args.information_jump_threshold is not None else 0.50,
        )
        engine = ChronoLatticeEngine(config)
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
        phios_payload = to_phios_payload(reconstruction)
        wrapped = wrap_artifact(ARTIFACT_KIND_PHIOS_PAYLOAD, SCHEMA_VERSION, phios_payload)
        write_json(args.out, wrapped)
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
                    "bridge_profile": reconstruction.bridge_profile,
                    "bridge_threshold_mode": reconstruction.bridge_threshold_mode,
                    "bridge_thresholds": reconstruction.bridge_thresholds,
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

    if args.command == "bridge-gaps":
        reconstruction = reconstruction_from_dict(load_json(args.reconstruction_path))
        gaps = [g.__dict__ for g in reconstruction.bridge_gaps]
        if args.severity:
            gaps = [g for g in gaps if g["severity"] == args.severity]
        if args.gap_type:
            gaps = [g for g in gaps if g["gap_type"] == args.gap_type]
        print(json.dumps(gaps, indent=2, sort_keys=True))
        return 0

    if args.command == "migration-status":
        try:
            data = load_json(args.path)
        except Exception as exc:
            print(f"Invalid JSON: {exc}")
            return 1
        status = artifact_migration_status(data)
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0

    if args.command == "migrate":
        try:
            data = load_json(args.path)
            migrated = migrate_artifact(data)
        except Exception as exc:
            print(f"Migration failed: {exc}")
            return 1
        write_json(args.out, migrated)
        return 0

    if args.command == "normalize-envelope":
        try:
            data = load_json(args.path)
            normalized = normalize_artifact_envelope(data, kind=args.kind)
        except Exception as exc:
            print(f"Normalization failed: {exc}")
            return 1

        if args.out:
            write_json(args.out, normalized)
        else:
            print(json.dumps(normalized, indent=2, sort_keys=True))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
