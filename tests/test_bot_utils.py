"""Tests for bot utility functions."""
import sys
import os

# Set test env vars before importing
os.environ["DISCORD_TOKEN"] = "A" * 70
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key-12345"

from bot import split_message, check_rate_limit
from collections import deque
from datetime import datetime


def test_split_message_short():
    """Test that short messages are not split."""
    text = "Short message"
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == text


def test_split_message_long():
    """Test that long messages are split correctly."""
    text = "A" * 3000  # Longer than Discord's 2000 char limit
    result = split_message(text)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk) <= 2000


def test_split_message_preserves_newlines():
    """Test that message splitting respects newlines."""
    text = "Line 1\n" * 100 + "A" * 1000
    result = split_message(text)
    assert len(result) > 1
