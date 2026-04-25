import pytest

from chronolattice.models import ChronoConfig
from chronolattice.profiles import (
    apply_bridge_profile,
    get_bridge_profile,
    list_bridge_profiles,
    resolve_bridge_config,
    resolve_bridge_threshold_provenance,
)


def test_list_bridge_profiles_order_is_deterministic():
    names = [p.name for p in list_bridge_profiles()]
    assert names == ["conservative", "balanced", "sensitive", "phi_guardian"]


def test_get_bridge_profile_case_insensitive():
    profile = get_bridge_profile("SENSITIVE")
    assert profile.name == "sensitive"


def test_get_bridge_profile_unknown_raises_with_supported_names():
    with pytest.raises(ValueError) as exc:
        get_bridge_profile("unknown")
    msg = str(exc.value)
    assert "conservative" in msg
    assert "phi_guardian" in msg


def test_apply_bridge_profile_returns_new_config():
    original = ChronoConfig(seed=369369)
    updated = apply_bridge_profile(original, "conservative")
    assert updated is not original
    assert updated.bridge_profile == "conservative"
    assert updated.bridge_gap_threshold == 0.70
    assert updated.coherence_drop_threshold == 0.30
    assert updated.energy_jump_threshold == 0.75
    assert updated.information_jump_threshold == 0.65


def test_balanced_profile_matches_default_thresholds():
    config = apply_bridge_profile(ChronoConfig(seed=369369), "balanced")
    assert config.bridge_gap_threshold == 0.55
    assert config.coherence_drop_threshold == 0.20
    assert config.energy_jump_threshold == 0.60
    assert config.information_jump_threshold == 0.50


def test_resolve_bridge_config_profile_mode_applies_balanced_defaults():
    resolved = resolve_bridge_config(ChronoConfig(seed=369369, bridge_threshold_mode="profile", bridge_profile="balanced"))
    assert resolved.bridge_gap_threshold == 0.55
    assert resolved.coherence_drop_threshold == 0.20
    assert resolved.energy_jump_threshold == 0.60
    assert resolved.information_jump_threshold == 0.50


def test_resolve_bridge_config_manual_mode_preserves_custom_values():
    config = ChronoConfig(
        seed=369369,
        bridge_threshold_mode="manual",
        bridge_gap_threshold=0.91,
        coherence_drop_threshold=0.41,
        energy_jump_threshold=0.88,
        information_jump_threshold=0.77,
    )
    resolved = resolve_bridge_config(config)
    assert resolved.bridge_threshold_mode == "manual"
    assert resolved.bridge_gap_threshold == 0.91
    assert resolved.coherence_drop_threshold == 0.41
    assert resolved.energy_jump_threshold == 0.88
    assert resolved.information_jump_threshold == 0.77


def test_resolve_bridge_config_invalid_mode_raises_value_error():
    with pytest.raises(ValueError):
        resolve_bridge_config(ChronoConfig(seed=369369, bridge_threshold_mode="bad"))


def test_resolve_bridge_threshold_provenance_profile_mode():
    resolved = resolve_bridge_threshold_provenance(
        ChronoConfig(seed=369369, bridge_threshold_mode="profile", bridge_profile="sensitive")
    )
    assert resolved == {
        "bridge_gap_threshold": "profile:sensitive",
        "coherence_drop_threshold": "profile:sensitive",
        "energy_jump_threshold": "profile:sensitive",
        "information_jump_threshold": "profile:sensitive",
    }


def test_resolve_bridge_threshold_provenance_manual_programmatic_mode():
    resolved = resolve_bridge_threshold_provenance(ChronoConfig(seed=369369, bridge_threshold_mode="manual"))
    assert resolved == {
        "bridge_gap_threshold": "programmatic_config",
        "coherence_drop_threshold": "programmatic_config",
        "energy_jump_threshold": "programmatic_config",
        "information_jump_threshold": "programmatic_config",
    }


def test_resolve_bridge_threshold_provenance_manual_cli_partial_mode():
    resolved = resolve_bridge_threshold_provenance(
        ChronoConfig(seed=369369, bridge_threshold_mode="manual"),
        cli_manual_fields={"bridge_gap_threshold", "energy_jump_threshold"},
    )
    assert resolved == {
        "bridge_gap_threshold": "manual_cli",
        "coherence_drop_threshold": "manual_default",
        "energy_jump_threshold": "manual_cli",
        "information_jump_threshold": "manual_default",
    }
