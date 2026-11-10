import pytest

from answer_or_abstain_rag.config.loader import load_settings
from answer_or_abstain_rag.kernel.errors import ConfigurationError


def test_defaults_load_without_files():
    settings = load_settings(env={})
    assert settings.pipeline.top_k >= 1
    assert settings.pipeline.stages


def test_toml_profile_overrides_defaults(tmp_path):
    profile = tmp_path / "p.toml"
    profile.write_text("[pipeline]\ntop_k = 3\n[cache]\nenabled = false\n")
    settings = load_settings(profile, env={})
    assert settings.pipeline.top_k == 3
    assert settings.cache.enabled is False


def test_environment_overrides_toml(tmp_path):
    profile = tmp_path / "p.toml"
    profile.write_text("[pipeline]\ntop_k = 3\n")
    settings = load_settings(profile, env={"ANSWER_OR_ABSTAIN_RAG_PIPELINE__TOP_K": "7", "ANSWER_OR_ABSTAIN_RAG_CACHE__ENABLED": "off"})
    assert settings.pipeline.top_k == 7
    assert settings.cache.enabled is False


def test_unknown_keys_are_rejected(tmp_path):
    profile = tmp_path / "p.toml"
    profile.write_text("[pipeline]\nnot_a_key = 1\n")
    with pytest.raises(ConfigurationError):
        load_settings(profile, env={})


def test_bad_env_value_is_rejected():
    with pytest.raises(ConfigurationError):
        load_settings(env={"ANSWER_OR_ABSTAIN_RAG_PIPELINE__TOP_K": "many"})


def test_missing_file_is_rejected(tmp_path):
    with pytest.raises(ConfigurationError):
        load_settings(tmp_path / "missing.toml", env={})
