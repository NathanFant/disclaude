# Building an Agentic Discord Bot

Transform your Discord bot from a chatbot into an **agent** that can actually do things.

## What is an Agent?

An **agent** is an AI that can:
- ✅ Use tools to perform actions
- ✅ Make decisions about which tools to use
- ✅ Chain multiple actions together
- ✅ Interact with external systems
- ✅ Execute commands and retrieve information

**Current bot**: Chats with users
**Agent bot**: Chats AND takes actions (searches Hypixel stats, sets reminders, runs commands, etc.)

## How It Works

### Tool Use Flow

```
User: "What's my Skyblock skill average?"
  ↓
Claude thinks: "I need to fetch Skyblock data"
  ↓
Claude calls: get_skyblock_stats(user_id)
  ↓
Bot executes: Fetches from Hypixel API
  ↓
Claude receives: {"skill_average": 32.5, "skills": {...}}
  ↓
Claude responds: "Your Skyblock skill average is 32.5!"
```

### Implementation with Anthropic API

```python
# Define tools the bot can use
tools = [
    {
        "name": "get_skyblock_stats",
        "description": "Get Hypixel Skyblock stats for a user",
        "input_schema": {
            "type": "object",
            "properties": {
                "discord_id": {
                    "type": "string",
                    "description": "Discord user ID"
                }
            },
            "required": ["discord_id"]
        }
    }
]

# Call Claude with tools
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    tools=tools,  # ← Give Claude access to tools
    messages=[{"role": "user", "content": "What are my Skyblock stats?"}]
)

# Claude decides to use a tool
if response.stop_reason == "tool_use":
    for block in response.content:
        if block.type == "tool_use":
            # Execute the tool
            result = execute_tool(block.name, block.input)

            # Send result back to Claude
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2048,
                tools=tools,
                messages=[
                    {"role": "user", "content": "What are my Skyblock stats?"},
                    {"role": "assistant", "content": response.content},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result
                            }
                        ]
                    }
                ]
            )
```

## Tools Your Bot Could Have

### 1. Hypixel/Skyblock Tools ✅ (Already have data!)

```python
{
    "name": "get_skyblock_stats",
    "description": "Get detailed Skyblock stats for a Discord user",
    "input_schema": {
        "type": "object",
        "properties": {
            "discord_id": {"type": "string"},
            "stat_type": {
                "type": "string",
                "enum": ["skills", "slayers", "dungeons", "profile"]
            }
        }
    }
}
```

**User**: "How's my combat skill doing?"
**Agent**: *Calls get_skyblock_stats* → "Your combat is level 45!"

### 2. Reminder Tools ✅ (Already have scheduler!)

```python
{
    "name": "create_reminder",
    "description": "Set a reminder for a user at a specific time",
    "input_schema": {
        "type": "object",
        "properties": {
            "user_id": {"type": "string"},
            "message": {"type": "string"},
            "time": {"type": "string", "description": "ISO 8601 format"}
        }
    }
}
```

**User**: "Remind me to check auctions in 1 hour"
**Agent**: *Calls create_reminder* → "I'll remind you at 3:45 PM!"

### 3. User Management Tools

```python
{
    "name": "link_minecraft_account",
    "description": "Link a Discord user to their Minecraft account",
    "input_schema": {
        "type": "object",
        "properties": {
            "discord_id": {"type": "string"},
            "minecraft_username": {"type": "string"}
        }
    }
}
```

**User**: "My Minecraft username is NathanFant"
**Agent**: *Calls link_minecraft_account* → "Linked! Found UUID and 5 Skyblock profiles!"

### 4. Server Info Tools

```python
{
    "name": "get_server_stats",
    "description": "Get Discord server statistics",
    "input_schema": {
        "type": "object",
        "properties": {
            "guild_id": {"type": "string"}
        }
    }
}
```

### 5. Web Search Tool

```python
{
    "name": "search_web",
    "description": "Search the web for current information",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
}
```

**User**: "What's the current price of enchanted diamond blocks?"
**Agent**: *Calls search_web* → Finds current market prices

## Implementation Example

### Step 1: Create Tool Executor

```python
# tools.py
"""Tool execution for agentic capabilities."""
from typing import Dict, Any, Optional
import json

from hypixel_client import hypixel_client
from skyblock_analyzer import skyblock_analyzer
from user_profiles import user_profiles
from scheduler import smart_scheduler
from datetime import datetime


class ToolExecutor:
    """Executes tools that Claude can call."""

    @staticmethod
    async def execute(tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result as a string."""

        if tool_name == "get_skyblock_stats":
            return await ToolExecutor.get_skyblock_stats(tool_input)

        elif tool_name == "create_reminder":
            return await ToolExecutor.create_reminder(tool_input)

        elif tool_name == "link_minecraft_account":
            return await ToolExecutor.link_minecraft_account(tool_input)

        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

    @staticmethod
    async def get_skyblock_stats(input_data: Dict[str, Any]) -> str:
        """Get Skyblock stats for a user."""
        discord_id = int(input_data['discord_id'])

        # Check if user is linked
        if not user_profiles.is_linked(discord_id):
            return json.dumps({
                "error": "User not linked",
                "message": "User needs to link their Minecraft account first"
            })

        # Get user's UUID
        uuid = user_profiles.get_uuid(discord_id)
        username = user_profiles.get_username(discord_id)

        # Fetch Skyblock profile
        profile = await hypixel_client.get_active_profile(uuid)
        if not profile:
            return json.dumps({"error": "No Skyblock profile found"})

        # Get player data
        player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)
        if not player_data:
            return json.dumps({"error": "Could not load player data"})

        # Analyze skills
        skill_analysis = skyblock_analyzer.analyze_skills(player_data)

        return json.dumps({
            "username": username,
            "profile_name": profile.get('cute_name'),
            "skill_average": skill_analysis.get('skill_average', 0),
            "skills": {
                name: data['level']
                for name, data in skill_analysis.get('skills', {}).items()
            }
        })

    @staticmethod
    async def create_reminder(input_data: Dict[str, Any]) -> str:
        """Create a reminder for a user."""
        user_id = int(input_data['user_id'])
        message = input_data['message']
        time_str = input_data['time']

        # Parse ISO 8601 time
        target_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))

        # Schedule reminder
        task_id = await smart_scheduler.schedule_reminder(
            when=target_time,
            channel_id=input_data.get('channel_id'),
            user_id=user_id,
            message=message,
            send_function=None  # Will need to be set
        )

        return json.dumps({
            "success": True,
            "task_id": task_id,
            "scheduled_for": target_time.isoformat()
        })

    @staticmethod
    async def link_minecraft_account(input_data: Dict[str, Any]) -> str:
        """Link a Discord user to their Minecraft account."""
        discord_id = int(input_data['discord_id'])
        username = input_data['minecraft_username']

        # Get UUID from Mojang
        uuid = await hypixel_client.get_uuid_from_username(username)
        if not uuid:
            return json.dumps({
                "error": "Minecraft user not found",
                "username": username
            })

        # Store the link
        user_profiles.link_user(discord_id, username, uuid)

        # Try to fetch Skyblock profile
        profile = await hypixel_client.get_active_profile(uuid)

        result = {
            "success": True,
            "username": username,
            "uuid": uuid,
            "linked": True
        }

        if profile:
            result["skyblock_profile"] = profile.get('cute_name')

            player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)
            if player_data:
                skill_analysis = skyblock_analyzer.analyze_skills(player_data)
                result["skill_average"] = skill_analysis.get('skill_average', 0)

        return json.dumps(result)


# Tool executor instance
tool_executor = ToolExecutor()
```

### Step 2: Define Available Tools

```python
# tool_definitions.py
"""Tool definitions for Claude."""

TOOLS = [
    {
        "name": "get_skyblock_stats",
        "description": "Get Hypixel Skyblock statistics for a Discord user. Returns skill levels, skill average, and profile information. User must be linked first.",
        "input_schema": {
            "type": "object",
            "properties": {
                "discord_id": {
                    "type": "string",
                    "description": "Discord user ID (as string)"
                },
                "stat_type": {
                    "type": "string",
                    "enum": ["skills", "all"],
                    "description": "Type of stats to retrieve",
                    "default": "all"
                }
            },
            "required": ["discord_id"]
        }
    },
    {
        "name": "link_minecraft_account",
        "description": "Link a Discord user to their Minecraft account. Fetches UUID from Mojang API and stores the link in the database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "discord_id": {
                    "type": "string",
                    "description": "Discord user ID (as string)"
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
        "description": "Create a reminder that will notify the user at a specific time.",
        "input_schema": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "Discord user ID"
                },
                "channel_id": {
                    "type": "string",
                    "description": "Discord channel ID where reminder should be sent"
                },
                "message": {
                    "type": "string",
                    "description": "Reminder message"
                },
                "time": {
                    "type": "string",
                    "description": "ISO 8601 timestamp when reminder should fire (e.g., 2024-03-15T14:30:00Z)"
                }
            },
            "required": ["user_id", "channel_id", "message", "time"]
        }
    }
]
```

### Step 3: Update bot.py to Use Tools

```python
# In bot.py, update get_claude_response()

async def get_claude_response(messages: list, model: str = None, context: dict = None) -> str:
    """Get response from Claude API with tool use support."""
    from tool_definitions import TOOLS
    from tools import tool_executor

    if model is None:
        last_message = messages[-1]['content'] if messages else ""
        model = determine_model_complexity(last_message, messages)

    system_prompt = personality.get_system_prompt()

    # Add context if provided
    if context:
        system_prompt += f"\n\nCurrent context:\n"
        system_prompt += f"- User ID: {context.get('user_id')}\n"
        system_prompt += f"- Channel ID: {context.get('channel_id')}\n"
        system_prompt += f"- Guild ID: {context.get('guild_id')}\n"

    # Call Claude with tools
    response = await asyncio.to_thread(
        client.messages.create,
        model=model,
        max_tokens=2048,
        system=system_prompt,
        tools=TOOLS,  # ← Enable tool use
        messages=messages
    )

    # Handle tool use
    if response.stop_reason == "tool_use":
        # Collect all tool uses
        tool_uses = [block for block in response.content if block.type == "tool_use"]

        # Execute tools
        tool_results = []
        for tool_use in tool_uses:
            print(f"[AGENT] Executing tool: {tool_use.name}")
            print(f"[AGENT] Input: {tool_use.input}")

            # Execute the tool
            result = await tool_executor.execute(tool_use.name, tool_use.input)

            print(f"[AGENT] Result: {result}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": result
            })

        # Send tool results back to Claude
        messages_with_results = messages + [
            {"role": "assistant", "content": response.content},
            {"role": "user", "content": tool_results}
        ]

        # Get final response
        final_response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=messages_with_results
        )

        # Extract text response
        text_blocks = [block.text for block in final_response.content if hasattr(block, 'text')]
        return '\n'.join(text_blocks)

    # No tool use, just return text
    return response.content[0].text


# Update on_message to pass context
async def on_message(message):
    # ... existing code ...

    # Pass context to Claude
    context = {
        'user_id': str(message.author.id),
        'channel_id': str(message.channel.id),
        'guild_id': str(message.guild.id) if message.guild else None
    }

    response_text = await get_claude_response(messages_list, context=context)

    # ... rest of existing code ...
```

## Example Conversations

### With Tools (Agent)

**User**: "What's my Skyblock skill average?"

**Agent thinks**: "I need to get Skyblock stats for this user"

**Agent calls**: `get_skyblock_stats(discord_id="123456")`

**Tool returns**: `{"skill_average": 32.5, "skills": {...}}`

**Agent**: "Your Skyblock skill average is 32.5! Your top skills are Combat (45), Mining (38), and Farming (35)."

---

**User**: "Link my Minecraft account, it's NathanFant"

**Agent calls**: `link_minecraft_account(discord_id="123456", minecraft_username="NathanFant")`

**Tool returns**: `{"success": true, "uuid": "47fb7b99...", "skill_average": 32.5}`

**Agent**: "Done! I've linked your account to NathanFant (UUID: 47fb7b99...). I found your Skyblock profile 'Papaya' with a skill average of 32.5!"

---

**User**: "Remind me in 30 minutes to check my auctions"

**Agent calls**: `create_reminder(user_id="123456", time="2024-03-15T15:30:00Z", message="check auctions")`

**Tool returns**: `{"success": true, "scheduled_for": "..."}`

**Agent**: "I'll remind you at 3:30 PM to check your auctions!"

## Safety Considerations

### Tool Permissions

Add permission checks:

```python
async def execute(tool_name: str, tool_input: Dict[str, Any], user_id: int) -> str:
    # Check if user has permission to use this tool
    if tool_name == "admin_command" and not is_admin(user_id):
        return json.dumps({"error": "Permission denied"})

    # Execute tool...
```

### Rate Limiting

Limit tool usage:

```python
tool_usage = defaultdict(lambda: deque(maxlen=5))

async def execute(tool_name: str, tool_input: Dict[str, Any], user_id: int) -> str:
    # Check rate limit
    if len(tool_usage[user_id]) >= 5:
        return json.dumps({"error": "Too many tool calls. Please wait."})

    tool_usage[user_id].append(datetime.now())
    # Execute tool...
```

### Input Validation

Validate tool inputs:

```python
async def get_skyblock_stats(input_data: Dict[str, Any]) -> str:
    try:
        discord_id = int(input_data['discord_id'])
    except (KeyError, ValueError):
        return json.dumps({"error": "Invalid discord_id"})

    # Continue...
```

## Benefits of Agent Architecture

✅ **Natural Interaction**: No need for slash commands
✅ **Smart Actions**: Claude decides when to use tools
✅ **Multi-step Tasks**: Chain multiple tools together
✅ **Error Handling**: Claude can retry with different approaches
✅ **Explanatory**: Claude explains what it's doing

## Next Steps

1. Create `tools.py` with tool executor
2. Create `tool_definitions.py` with tool schemas
3. Update `bot.py` to support tool use
4. Test with simple tools first
5. Add more complex tools gradually
6. Add safety checks and rate limiting

## Example: Complete Agent Flow

```
User: "Check my Skyblock stats and remind me to do slayers in an hour"

Claude:
  1. Calls get_skyblock_stats(discord_id="123456")
  2. Receives: {"skill_average": 32.5, ...}
  3. Calls create_reminder(time="+1 hour", message="do slayers")
  4. Receives: {"success": true}
  5. Responds: "Your skill average is 32.5! I've set a reminder
     for 3:45 PM to do slayers."
```

This is a **true agent** - it understands intent, uses tools, and takes action!

---

**Ready to implement?** Start with one tool (e.g., `get_skyblock_stats`) and expand from there!
