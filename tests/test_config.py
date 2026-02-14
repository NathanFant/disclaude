"""Tests for configuration module."""
import os
import pytest


def test_config_imports():
    """Test that config module can be imported."""
    # Set required env vars for import
    os.environ["DISCORD_TOKEN"] = "A" * 70
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-12345"

    import config
    assert config.DISCORD_TOKEN is not None
    assert config.ANTHROPIC_API_KEY is not None


def test_config_defaults():
    """Test that config defaults are set correctly."""
    os.environ["DISCORD_TOKEN"] = "A" * 70
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-12345"

    import config
    assert config.COMMAND_PREFIX == "!"
    assert config.MAX_CONVERSATION_HISTORY == 10
    assert config.RATE_LIMIT_MESSAGES == 5
    assert config.RATE_LIMIT_SECONDS == 60
