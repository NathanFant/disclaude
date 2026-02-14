# Emergent Agent Architecture

Building a bot that **figures out what to do** instead of following pre-scripted tools.

## The Problem with Pre-defined Tools

**Current approach:**
```python
tools = [
    "get_skyblock_stats",      # ← Hard-coded
    "link_minecraft_account",  # ← Hard-coded
    "create_reminder"          # ← Hard-coded
]
```

**What you want:**
```
User: "tell @person 'chicken nugget' 57 times"
Bot: *Figures out it needs to send messages*
     *Sends 57 messages*
     "Done!"
```

No pre-defined "send_message_57_times" tool needed!

## The Solution: General-Purpose Tools

Instead of specific tools, give Claude **general capabilities**:

### 1. Discord Control Tools

```python
{
    "name": "send_discord_message",
    "description": "Send a message to any channel or user",
    "input_schema": {
        "type": "object",
        "properties": {
            "target": {"type": "string", "description": "Channel ID, user ID, or @mention"},
            "message": {"type": "string"},
            "repeat": {"type": "integer", "default": 1}
        }
    }
}
```

Now Claude can figure out to use this for "send chicken nugget 57 times"!

### 2. Code Execution Tool

```python
{
    "name": "execute_python",
    "description": "Execute Python code to accomplish tasks",
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
            "description": {"type": "string", "description": "What this code does"}
        }
    }
}
```

**Example:**
```
User: "calculate my skill average and compare to average player"
Claude: execute_python(code="
    from hypixel_client import hypixel_client
    # Fetch data
    profile = await get_profile()
    skill_avg = calculate_skills(profile)
    # Compare to baseline
    print(f'Your: {skill_avg}, Average: 25')
")
```

### 3. Memory/Context Tools

```python
{
    "name": "read_message_history",
    "description": "Read previous messages in this channel",
    "input_schema": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "default": 50}
        }
    }
}
```

**Example:**
```
User: "hey you forgot to serve the stats on my skyblock"
Claude: *Reads message history*
        *Sees previous conversation*
        "You're right! Let me get those stats now..."
        *Calls get_skyblock_stats*
```

### 4. Self-Reflection Tools

```python
{
    "name": "check_previous_actions",
    "description": "Check what actions I've taken recently",
    "input_schema": {
        "type": "object",
        "properties": {
            "action_type": {"type": "string"}
        }
    }
}
```

### 5. Web Search Tool

```python
{
    "name": "search_web",
    "description": "Search the internet for current information",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        }
    }
}
```

## Implementation: Emergent Tools

### tools_emergent.py

```python
"""Emergent agent tools - general-purpose capabilities."""
from typing import Dict, Any
import json
import asyncio
import discord
from datetime import datetime


class EmergentTools:
    """General-purpose tools for emergent behavior."""

    def __init__(self, bot):
        self.bot = bot
        self.action_history = []  # Track what the bot has done

    async def send_discord_message(self, input_data: Dict[str, Any]) -> str:
        """Send a message to a Discord channel or user.

        Allows repetition for emergent behaviors like:
        "tell @person 'hello' 10 times"
        """
        target = input_data.get('target')
        message = input_data.get('message')
        repeat = input_data.get('repeat', 1)

        if not target or not message:
            return json.dumps({"error": "Missing target or message"})

        # Parse target (channel ID, user ID, or @mention)
        target_id = None

        # Extract ID from <@123> or <#123> format
        if target.startswith('<@') and target.endswith('>'):
            target_id = int(target[2:-1].replace('!', ''))
            target_type = 'user'
        elif target.startswith('<#') and target.endswith('>'):
            target_id = int(target[2:-1])
            target_type = 'channel'
        elif target.isdigit():
            target_id = int(target)
            target_type = 'channel'  # Assume channel if just ID

        if not target_id:
            return json.dumps({"error": "Invalid target format"})

        # Get the target object
        if target_type == 'user':
            recipient = self.bot.get_user(target_id)
            if not recipient:
                return json.dumps({"error": f"User {target_id} not found"})
        else:
            recipient = self.bot.get_channel(target_id)
            if not recipient:
                return json.dumps({"error": f"Channel {target_id} not found"})

        # Send message(s)
        sent_count = 0
        for i in range(min(repeat, 100)):  # Cap at 100 for safety
            try:
                await recipient.send(message)
                sent_count += 1
                if repeat > 1:
                    await asyncio.sleep(0.5)  # Rate limit
            except Exception as e:
                break

        # Log action
        self.action_history.append({
            'type': 'send_message',
            'target': str(target_id),
            'message': message,
            'count': sent_count,
            'timestamp': datetime.now().isoformat()
        })

        return json.dumps({
            "success": True,
            "sent": sent_count,
            "target": str(target_id),
            "message": message
        })

    async def execute_python(self, input_data: Dict[str, Any]) -> str:
        """Execute Python code safely.

        DANGEROUS! Should have strict sandboxing in production.
        For now, only allow specific safe operations.
        """
        code = input_data.get('code', '')
        description = input_data.get('description', 'Running code')

        # SAFETY: Whitelist of allowed modules/functions
        allowed_imports = {
            'hypixel_client', 'skyblock_analyzer', 'user_profiles',
            'datetime', 'json', 'math'
        }

        # Check for dangerous operations
        dangerous = ['exec', 'eval', 'open', 'import os', 'subprocess', '__']
        if any(d in code for d in dangerous):
            return json.dumps({
                "error": "Code contains disallowed operations",
                "security": "blocked"
            })

        # Limited execution environment
        try:
            # Create safe globals
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'dict': dict,
                    'list': list,
                }
            }

            # Execute code
            exec_result = {}
            exec(code, safe_globals, exec_result)

            # Log action
            self.action_history.append({
                'type': 'execute_python',
                'description': description,
                'timestamp': datetime.now().isoformat()
            })

            return json.dumps({
                "success": True,
                "description": description,
                "result": str(exec_result) if exec_result else "Executed successfully"
            })

        except Exception as e:
            return json.dumps({
                "error": str(e),
                "code": code[:100]  # First 100 chars for debugging
            })

    async def read_message_history(self, input_data: Dict[str, Any]) -> str:
        """Read recent message history from the current channel.

        Allows Claude to remember context and self-correct.
        """
        channel_id = input_data.get('channel_id')
        limit = input_data.get('limit', 50)

        if not channel_id:
            return json.dumps({"error": "Missing channel_id"})

        channel = self.bot.get_channel(int(channel_id))
        if not channel:
            return json.dumps({"error": "Channel not found"})

        try:
            messages = []
            async for msg in channel.history(limit=limit):
                messages.append({
                    'author': msg.author.name,
                    'content': msg.content[:200],  # Truncate long messages
                    'timestamp': msg.created_at.isoformat(),
                    'is_bot': msg.author.bot
                })

            return json.dumps({
                "success": True,
                "messages": messages,
                "count": len(messages)
            })

        except Exception as e:
            return json.dumps({"error": str(e)})

    async def check_previous_actions(self, input_data: Dict[str, Any]) -> str:
        """Check what actions the bot has taken recently.

        Self-reflection capability.
        """
        action_type = input_data.get('action_type', 'all')
        limit = input_data.get('limit', 10)

        if action_type != 'all':
            actions = [a for a in self.action_history if a['type'] == action_type]
        else:
            actions = self.action_history

        recent_actions = actions[-limit:]

        return json.dumps({
            "success": True,
            "actions": recent_actions,
            "count": len(recent_actions)
        })

    async def get_discord_context(self, input_data: Dict[str, Any]) -> str:
        """Get information about Discord server, channels, users."""
        context_type = input_data.get('type', 'server')
        guild_id = input_data.get('guild_id')

        if not guild_id:
            return json.dumps({"error": "Missing guild_id"})

        guild = self.bot.get_guild(int(guild_id))
        if not guild:
            return json.dumps({"error": "Guild not found"})

        if context_type == 'server':
            return json.dumps({
                "success": True,
                "name": guild.name,
                "member_count": guild.member_count,
                "channels": len(guild.channels),
                "roles": len(guild.roles)
            })

        elif context_type == 'channels':
            channels = [
                {"name": c.name, "id": str(c.id), "type": str(c.type)}
                for c in guild.channels[:20]  # Limit to 20
            ]
            return json.dumps({"success": True, "channels": channels})

        elif context_type == 'members':
            # Get online members
            online = [m for m in guild.members if m.status != discord.Status.offline]
            members = [
                {"name": m.name, "id": str(m.id), "status": str(m.status)}
                for m in online[:20]
            ]
            return json.dumps({"success": True, "members": members})

        return json.dumps({"error": "Unknown context type"})
```

### tool_definitions_emergent.py

```python
"""Tool definitions for emergent agent behavior."""

EMERGENT_TOOLS = [
    {
        "name": "send_discord_message",
        "description": (
            "Send a message to any Discord channel or user. Can send multiple times. "
            "Use for: sending messages, replying to users, spamming (if requested), "
            "notifying people, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "Channel ID, user ID, or @mention (e.g., '<@123>' or '<#456>')"
                },
                "message": {
                    "type": "string",
                    "description": "Message content to send"
                },
                "repeat": {
                    "type": "integer",
                    "description": "Number of times to send the message (default: 1, max: 100)",
                    "default": 1
                }
            },
            "required": ["target", "message"]
        }
    },
    {
        "name": "read_message_history",
        "description": (
            "Read recent message history from a channel. "
            "Use to: check what was said before, see if you already did something, "
            "understand context, find information from previous conversation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "channel_id": {
                    "type": "string",
                    "description": "Discord channel ID"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of messages to read (default: 50)",
                    "default": 50
                }
            },
            "required": ["channel_id"]
        }
    },
    {
        "name": "check_previous_actions",
        "description": (
            "Check what actions you (the bot) have taken recently. "
            "Use for: self-reflection, checking if you forgot something, "
            "verifying what you did."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action_type": {
                    "type": "string",
                    "description": "Type of action to check (e.g., 'send_message', 'get_stats') or 'all'",
                    "default": "all"
                },
                "limit": {
                    "type": "integer",
                    "description": "Number of recent actions to check",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "get_discord_context",
        "description": (
            "Get information about the Discord server, channels, or members. "
            "Use to: find channels, see who's online, understand server structure."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["server", "channels", "members"],
                    "description": "Type of context to get"
                },
                "guild_id": {
                    "type": "string",
                    "description": "Discord server (guild) ID"
                }
            },
            "required": ["type", "guild_id"]
        }
    },
    {
        "name": "execute_python",
        "description": (
            "Execute Python code to accomplish complex tasks. "
            "Use when you need to: calculate something, process data, "
            "perform operations not covered by other tools. "
            "CAUTION: Limited to safe operations only."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "description": {
                    "type": "string",
                    "description": "Brief description of what this code does"
                }
            },
            "required": ["code", "description"]
        }
    }
]
```

## Example: Emergent Behaviors

### Example 1: Self-Correction

```
User: "hey you forgot to serve the stats on my skyblock"

Claude:
  1. read_message_history(channel_id="123")
  2. Sees: "User: what are my skyblock stats?"
  3. Sees: "Bot: Let me check... [no follow-up]"
  4. Realizes it didn't complete the task
  5. get_skyblock_stats(user_id="...")
  6. Responds: "You're right! Sorry about that. Here are your stats: ..."
```

### Example 2: Creative Spam

```
User: "tell @person 'chicken nugget' 57 times"

Claude:
  1. Understands the request
  2. send_discord_message(
       target="<@person_id>",
       message="chicken nugget",
       repeat=57
     )
  3. Responds: "Done! Sent 'chicken nugget' 57 times to @person 😄"
```

### Example 3: Context-Aware Actions

```
User: "who's online right now?"

Claude:
  1. get_discord_context(type="members", guild_id="...")
  2. Receives list of online members
  3. Responds: "Currently online: Alice, Bob, Charlie (3 members)"

User: "tell them all to join vc"

Claude:
  1. Remembers the online members from before
  2. For each member:
     send_discord_message(
       target="<@member>",
       message="Hey! Join the voice channel!"
     )
  3. Responds: "Messaged all 3 online members!"
```

### Example 4: Complex Task

```
User: "analyze everyone's skyblock stats and tell me who's best at combat"

Claude:
  1. get_discord_context(type="members")
  2. For each member with linked account:
     get_skyblock_stats(user_id)
  3. execute_python(code="
       stats = [...]
       best_combat = max(stats, key=lambda x: x['combat'])
       print(f'{best_combat['name']} has combat level {best_combat['combat']}')
     ")
  4. Responds with analysis!
```

## Safety & Control

### Rate Limiting

```python
# In EmergentTools
MAX_MESSAGES_PER_MINUTE = 10
MAX_CODE_EXECUTIONS_PER_HOUR = 5

def check_rate_limit(self, action_type):
    recent = [a for a in self.action_history
              if a['type'] == action_type
              and datetime.now() - datetime.fromisoformat(a['timestamp']) < timedelta(minutes=1)]

    if action_type == 'send_message' and len(recent) >= MAX_MESSAGES_PER_MINUTE:
        raise RateLimitError("Too many messages sent")
```

### Permission System

```python
# Admin-only tools
ADMIN_TOOLS = ['execute_python', 'ban_user', 'delete_messages']

def check_permission(self, user_id, tool_name):
    if tool_name in ADMIN_TOOLS and user_id not in ADMIN_USER_IDS:
        raise PermissionError(f"Tool {tool_name} requires admin privileges")
```

### Code Sandboxing

For `execute_python`, use a proper sandbox:
- `RestrictedPython` library
- Docker container
- Separate process with timeout
- Whitelist of allowed operations

## Integration

Combine with existing tools:

```python
# In bot.py
from tool_definitions import TOOLS
from tool_definitions_emergent import EMERGENT_TOOLS
from tools import tool_executor
from tools_emergent import EmergentTools

# Initialize
emergent_tools = EmergentTools(bot)

# Combine all tools
ALL_TOOLS = TOOLS + EMERGENT_TOOLS

# In tool executor, add emergent tool handling
# ... existing code ...
```

## The Result

Now your bot can:

✅ Figure out tasks on its own
✅ Send messages creatively ("57 chicken nuggets")
✅ Self-correct ("you forgot to...")
✅ Read and understand context
✅ Chain multiple actions
✅ Execute custom code for complex tasks

**True emergence** - not pre-programmed responses, but intelligent action!
