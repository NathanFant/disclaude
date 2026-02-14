"""Configuration management for the Discord bot."""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")

# Anthropic Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"

# Bot Behavior
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", "10"))
MAX_MESSAGE_LENGTH = 2000  # Discord's message limit

# Rate Limiting
RATE_LIMIT_MESSAGES = int(os.getenv("RATE_LIMIT_MESSAGES", "5"))
RATE_LIMIT_SECONDS = int(os.getenv("RATE_LIMIT_SECONDS", "60"))

# Validation
if not DISCORD_TOKEN:
    raise ValueError(
        "DISCORD_TOKEN not found in environment variables. "
        "Please set it in Railway's Variables section."
    )
if len(DISCORD_TOKEN) < 50:
    raise ValueError(
        f"DISCORD_TOKEN appears invalid (length: {len(DISCORD_TOKEN)}). "
        "Discord bot tokens should be longer. "
        "Check for extra quotes or incomplete token."
    )
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment variables. "
        "Please set it in Railway's Variables section."
    )
