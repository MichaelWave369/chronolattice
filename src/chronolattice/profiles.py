from __future__ import annotations

from dataclasses import dataclass, replace

from .models import ChronoConfig


@dataclass(frozen=True)
class BridgeProfile:
    name: str
    description: str
    bridge_gap_threshold: float
    coherence_drop_threshold: float
    energy_jump_threshold: float
    information_jump_threshold: float


BRIDGE_PROFILE_CONSERVATIVE = BridgeProfile(
    name="conservative",
    description="Fewer bridge gaps with higher confidence thresholds.",
    bridge_gap_threshold=0.70,
    coherence_drop_threshold=0.30,
    energy_jump_threshold=0.75,
    information_jump_threshold=0.65,
)

BRIDGE_PROFILE_BALANCED = BridgeProfile(
    name="balanced",
    description="Default v0.2 behavior balancing sensitivity and confidence.",
    bridge_gap_threshold=0.55,
    coherence_drop_threshold=0.20,
    energy_jump_threshold=0.60,
    information_jump_threshold=0.50,
)

BRIDGE_PROFILE_SENSITIVE = BridgeProfile(
    name="sensitive",
    description="Higher sensitivity for smaller discontinuities.",
    bridge_gap_threshold=0.40,
    coherence_drop_threshold=0.12,
    energy_jump_threshold=0.40,
    information_jump_threshold=0.35,
)

BRIDGE_PROFILE_PHI_GUARDIAN = BridgeProfile(
    name="phi_guardian",
    description="PHI/LAMBDA-inspired thresholds for PHI369-aligned guardrails.",
    bridge_gap_threshold=0.50,
    coherence_drop_threshold=0.190983,
    energy_jump_threshold=0.618034,
    information_jump_threshold=0.381966,
)


ALLOWED_THRESHOLD_MODES = {"profile", "manual"}
BRIDGE_THRESHOLD_KEYS = (
    "bridge_gap_threshold",
    "coherence_drop_threshold",
    "energy_jump_threshold",
    "information_jump_threshold",
)


def list_bridge_profiles() -> list[BridgeProfile]:
    return [
        BRIDGE_PROFILE_CONSERVATIVE,
        BRIDGE_PROFILE_BALANCED,
        BRIDGE_PROFILE_SENSITIVE,
        BRIDGE_PROFILE_PHI_GUARDIAN,
    ]


def get_bridge_profile(name: str) -> BridgeProfile:
    normalized = name.lower()
    mapping = {profile.name: profile for profile in list_bridge_profiles()}
    if normalized not in mapping:
        supported = ", ".join(mapping.keys())
        raise ValueError(f"Unknown bridge profile '{name}'. Supported profiles: {supported}")
    return mapping[normalized]


def apply_bridge_profile(config: ChronoConfig, profile_name: str) -> ChronoConfig:
    profile = get_bridge_profile(profile_name)
    return replace(
        config,
        bridge_profile=profile.name,
        bridge_gap_threshold=profile.bridge_gap_threshold,
        coherence_drop_threshold=profile.coherence_drop_threshold,
        energy_jump_threshold=profile.energy_jump_threshold,
        information_jump_threshold=profile.information_jump_threshold,
    )


def resolve_bridge_config(config: ChronoConfig) -> ChronoConfig:
    mode = config.bridge_threshold_mode.lower()
    if mode == "profile":
        return apply_bridge_profile(config, config.bridge_profile)
    if mode == "manual":
        return replace(config, bridge_threshold_mode="manual")
    allowed = ", ".join(sorted(ALLOWED_THRESHOLD_MODES))
    raise ValueError(f"Invalid bridge_threshold_mode '{config.bridge_threshold_mode}'. Allowed values: {allowed}")


def resolve_bridge_threshold_provenance(
    config: ChronoConfig,
    cli_manual_fields: set[str] | None = None,
) -> dict[str, str]:
    mode = config.bridge_threshold_mode.lower()
    if mode == "profile":
        source = f"profile:{config.bridge_profile}"
        return {key: source for key in BRIDGE_THRESHOLD_KEYS}
    if mode == "manual":
        if cli_manual_fields is None:
            return {key: "programmatic_config" for key in BRIDGE_THRESHOLD_KEYS}
        return {
            key: ("manual_cli" if key in cli_manual_fields else "manual_default")
            for key in BRIDGE_THRESHOLD_KEYS
        }
    allowed = ", ".join(sorted(ALLOWED_THRESHOLD_MODES))
    raise ValueError(f"Invalid bridge_threshold_mode '{config.bridge_threshold_mode}'. Allowed values: {allowed}")
