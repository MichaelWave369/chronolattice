import pytest

from chronolattice.models import ChronoConfig
from chronolattice.profiles import apply_bridge_profile, get_bridge_profile, list_bridge_profiles


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
