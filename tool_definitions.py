"""Tool definitions for Claude agent capabilities.

These tools enable Claude to perform actions like fetching Skyblock stats,
creating reminders, linking accounts, etc.
"""

TOOLS = [
    {
        "name": "get_skyblock_stats",
        "description": (
            "Get Hypixel Skyblock statistics for a Discord user. "
            "Returns skill levels, skill average, profile name, and other stats. "
            "The user must have linked their Minecraft account first using link_minecraft_account."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "discord_id": {
                    "type": "string",
                    "description": "Discord user ID as a string"
                }
            },
            "required": ["discord_id"]
        }
    },
    {
        "name": "link_minecraft_account",
        "description": (
            "Link a Discord user to their Minecraft account. "
            "Fetches the UUID from Mojang API, stores the link in the database, "
            "and attempts to fetch their Skyblock profile information."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "discord_id": {
                    "type": "string",
                    "description": "Discord user ID as a string"
                },
                "minecraft_username": {
                    "type": "string",
                    "description": "Minecraft username (case-insensitive)"
                }
            },
            "required": ["discord_id", "minecraft_username"]
        }
    },
    {
        "name": "create_reminder",
        "description": (
            "Create a reminder that will notify the user at a specific time. "
            "The reminder will be sent as a message in the same channel."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Discord user ID"
                },
                "channel_id": {
                    "type": "string",
                    "description": "Discord channel ID where the reminder should be sent"
                },
                "message": {
                    "type": "string",
                    "description": "The reminder message content"
                },
                "time": {
                    "type": "string",
                    "description": (
                        "ISO 8601 timestamp when the reminder should fire "
                        "(e.g., '2024-03-15T14:30:00Z' or '2024-03-15T14:30:00+00:00')"
                    )
                }
            },
            "required": ["user_id", "channel_id", "message", "time"]
        }
    },
    {
        "name": "check_user_link_status",
        "description": (
            "Check if a Discord user has linked their Minecraft account. "
            "Returns the linked username and UUID if available."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "discord_id": {
                    "type": "string",
                    "description": "Discord user ID as a string"
                }
            },
            "required": ["discord_id"]
        }
    }
]
