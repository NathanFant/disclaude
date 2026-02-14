"""Configuration management for the Discord bot."""
import os

# All configuration comes from environment variables
# Set these in Railway for production or in your shell for local development

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

# Debug logging
print(f"[CONFIG] DISCORD_TOKEN length: {len(DISCORD_TOKEN)}")
print(f"[CONFIG] DISCORD_TOKEN first 10 chars: {DISCORD_TOKEN[:10]}...")
print(f"[CONFIG] DISCORD_TOKEN last 10 chars: ...{DISCORD_TOKEN[-10:]}")
print(f"[CONFIG] Raw env var (first 30): {os.getenv('DISCORD_TOKEN', '')[:30]}")

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
        f"Check for extra quotes or incomplete token.\n"
        f"Current value starts with: {DISCORD_TOKEN[:20]}...\n"
        f"This looks like a placeholder or reference variable."
    )
if not ANTHROPIC_API_KEY:
    raise ValueError(
        "ANTHROPIC_API_KEY not found in environment variables. "
        "Please set it in Railway's Variables section."
    )
