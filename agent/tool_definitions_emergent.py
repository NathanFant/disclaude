"""Tool definitions for emergent agent behavior.

These are general-purpose tools that enable Claude to figure out solutions
rather than following pre-scripted paths.
"""

EMERGENT_TOOLS = [
    {
        "name": "send_discord_message",
        "description": (
            "Send a message to any Discord channel or user. Can send the same message multiple times if requested. "
            "Use this for: replying to users, sending notifications, forwarding messages, "
            "creative tasks like 'send hello 10 times', messaging specific people, etc. "
            "Target can be a channel ID, user ID, or @mention format."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": (
                        "Where to send the message. Can be:\n"
                        "- User mention: '<@123456>'\n"
                        "- Channel mention: '<#789012>'\n"
                        "- Channel ID: '789012'"
                    )
                },
                "message": {
                    "type": "string",
                    "description": "The message content to send"
                },
                "repeat": {
                    "type": "integer",
                    "description": "Number of times to send the message (default: 1, max: 50)",
                    "default": 1,
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": ["target", "message"]
        }
    },
    {
        "name": "read_message_history",
        "description": (
            "Read recent message history from a Discord channel to understand context. "
            "Use this to: check what was said previously, see if you already responded to something, "
            "understand the conversation context, verify information, find what a user asked about earlier. "
            "Enables self-awareness and context understanding."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "Discord channel ID to read history from"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recent messages to read (default: 50, max: 100)",
                    "default": 50,
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": ["channel_id"]
        }
    },
    {
        "name": "check_previous_actions",
        "description": (
            "Check what actions you (the bot) have taken recently. "
            "Use this for self-reflection: verify if you already did something, check if you forgot a task, "
            "see what messages you sent, understand what actions you've performed. "
            "Enables self-awareness and correction of mistakes."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "description": (
                        "Type of action to check:\n"
                        "- 'send_message': Check messages sent\n"
                        "- 'read_history': Check history reads\n"
                        "- 'all': Check all action types"
                    ),
                    "default": "all"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recent actions to check (default: 10, max: 50)",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            }
        }
    },
    {
        "name": "get_discord_context",
        "description": (
            "Get information about the Discord server, channels, or members. "
            "Use to: find out who's in the server, list available channels, "
            "get server information, understand the Discord environment. "
            "Enables context-aware decision making."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["server", "channels", "members"],
                    "description": (
                        "Type of context to get:\n"
                        "- 'server': Server info (name, member count, etc.)\n"
                        "- 'channels': List of channels\n"
                        "- 'members': List of server members"
                    )
                },
                "guild_id": {
                    "type": "string",
                    "description": "Discord server (guild) ID"
                }
            },
            "required": ["type", "guild_id"]
        }
    }
]
