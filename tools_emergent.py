"""Emergent agent tools - general-purpose capabilities for creative problem-solving.

These tools allow Claude to figure out solutions rather than following pre-scripted paths.
"""
from typing import Dict, Any
import json
import asyncio
import discord
from datetime import datetime, timedelta
from collections import defaultdict


class EmergentTools:
    """General-purpose tools enabling emergent intelligent behavior."""

    def __init__(self, bot):
        self.bot = bot
        self.action_history = []  # Track what the bot has done
        self.rate_limits = defaultdict(list)  # Track rate limiting

    def _check_rate_limit(self, action_type: str, limit: int, window_minutes: int = 1) -> bool:
        """Check if action is within rate limit."""
        now = datetime.now()
        cutoff = now - timedelta(minutes=window_minutes)

        # Clean old entries
        self.rate_limits[action_type] = [
            t for t in self.rate_limits[action_type] if t > cutoff
        ]

        if len(self.rate_limits[action_type]) >= limit:
            return False

        self.rate_limits[action_type].append(now)
        return True

    async def send_discord_message(self, input_data: Dict[str, Any]) -> str:
        """Send a message to a Discord channel or user.

        Enables emergent behaviors like:
        - "tell @person hello 10 times"
        - "send a message to #general"
        - "notify everyone in the channel"
        """
        print(f"[EMERGENT] send_discord_message called")
        print(f"[EMERGENT]   Target: {input_data.get('target')}")
        print(f"[EMERGENT]   Message: {input_data.get('message', '')[:50]}...")
        print(f"[EMERGENT]   Repeat: {input_data.get('repeat', 1)}")

        # Rate limit: 20 messages per minute
        if not self._check_rate_limit('send_message', 20, 1):
            print(f"[EMERGENT] ERROR: Rate limit exceeded")
            return json.dumps({
                "error": "Rate limit exceeded",
                "message": "Too many messages sent recently. Please wait."
            })

        target = input_data.get('target')
        message = input_data.get('message')
        repeat = min(input_data.get('repeat', 1), 50)  # Cap at 50 for safety

        if not target or not message:
            print(f"[EMERGENT] ERROR: Missing target or message")
            return json.dumps({"error": "Missing target or message", "success": False})

        # Parse target
        target_id = None
        target_type = None
        recipient = None

        # <@123> or <@!123> = user mention
        if target.startswith('<@') and target.endswith('>'):
            target_id = int(target.replace('<@', '').replace('!', '').replace('>', ''))
            print(f"[EMERGENT] Detected user mention, ID: {target_id}")
            try:
                recipient = await self.bot.fetch_user(target_id)
                target_type = 'user'
                print(f"[EMERGENT] ✅ Found user: {recipient.name}")
            except Exception as e:
                print(f"[EMERGENT] ❌ User fetch failed: {str(e)}")
                return json.dumps({"error": f"User not found: {target_id} ({str(e)})", "success": False})

        # <#123> = channel mention
        elif target.startswith('<#') and target.endswith('>'):
            target_id = int(target.replace('<#', '').replace('>', ''))
            print(f"[EMERGENT] Detected channel mention, ID: {target_id}")
            recipient = self.bot.get_channel(target_id)
            if recipient:
                target_type = 'channel'
                print(f"[EMERGENT] ✅ Found channel: {recipient.name}")
            else:
                print(f"[EMERGENT] ❌ Channel not in cache")
                # Log available channels for debugging
                all_channels = [f"{c.name} ({c.id})" for g in self.bot.guilds for c in g.channels[:5]]
                print(f"[EMERGENT] Available channels (first 5 per guild): {all_channels}")
                return json.dumps({"error": f"Channel not found: {target_id}", "success": False})

        # Just digits = try channel first, then user
        elif target.isdigit():
            target_id = int(target)
            print(f"[EMERGENT] Detected bare ID: {target_id}")

            # Try as channel first (from cache)
            recipient = self.bot.get_channel(target_id)
            if recipient:
                target_type = 'channel'
                print(f"[EMERGENT] ✅ Found as channel (cached): {getattr(recipient, 'name', 'DM')}")
            else:
                print(f"[EMERGENT] Not in cache, trying to fetch channel (works for DMs too)...")
                # Try fetching channel (works for both guild channels and DMs)
                try:
                    recipient = await self.bot.fetch_channel(target_id)
                    target_type = 'channel'
                    print(f"[EMERGENT] ✅ Found as channel (fetched): {getattr(recipient, 'name', 'DM')}")
                except Exception as e:
                    print(f"[EMERGENT] Not found as channel: {str(e)}, trying user...")
                    # Try as user
                    try:
                        recipient = await self.bot.fetch_user(target_id)
                        target_type = 'user'
                        print(f"[EMERGENT] ✅ Found as user: {recipient.name}")
                    except Exception as e2:
                        print(f"[EMERGENT] ❌ Not found as user either: {str(e2)}")
                    # Debug info
                    guilds = [f"{g.name} ({g.id})" for g in self.bot.guilds]
                    print(f"[EMERGENT] Bot is in {len(self.bot.guilds)} guild(s): {guilds}")
                    all_channels = [f"{c.name} ({c.id})" for g in self.bot.guilds for c in g.text_channels[:3]]
                    print(f"[EMERGENT] Available text channels (first 3 per guild): {all_channels}")
                    return json.dumps({
                        "error": f"Target not found: {target_id} (tried both channel and user)",
                        "success": False,
                        "debug_info": {
                            "guilds": guilds,
                            "sample_channels": all_channels
                        }
                    })
        else:
            print(f"[EMERGENT] ERROR: Invalid target format: {target}")
            return json.dumps({"error": f"Invalid target format: {target}", "success": False})

        if not recipient:
            print(f"[EMERGENT] ERROR: Recipient is None after parsing")
            return json.dumps({
                "error": f"Failed to get recipient: {target}",
                "success": False
            })

        # Split message if it exceeds Discord's 2000 character limit
        def split_long_message(text: str, max_length: int = 2000) -> list:
            """Split message into chunks."""
            if len(text) <= max_length:
                return [text]
            chunks = []
            while text:
                if len(text) <= max_length:
                    chunks.append(text)
                    break
                split_pos = text.rfind('\n', 0, max_length)
                if split_pos == -1:
                    split_pos = max_length
                chunks.append(text[:split_pos])
                text = text[split_pos:].lstrip()
            return chunks

        # Send message(s)
        sent_count = 0
        errors = []
        message_chunks = split_long_message(message)

        for i in range(repeat):
            try:
                # Send all chunks for this repetition
                for chunk in message_chunks:
                    await recipient.send(chunk)
                    sent_count += 1

                # Rate limit between messages if repeating
                if repeat > 1 and i < repeat - 1:
                    await asyncio.sleep(0.5)

            except discord.Forbidden:
                errors.append("Missing permissions to send messages")
                break
            except discord.HTTPException as e:
                errors.append(f"HTTP error: {str(e)}")
                break
            except Exception as e:
                errors.append(f"Error on message {i+1}: {str(e)}")
                break

        # Log action
        self.action_history.append({
            'type': 'send_message',
            'target': str(target_id),
            'target_type': target_type,
            'message': message[:100],  # Truncate for logging
            'count': sent_count,
            'requested': repeat,
            'timestamp': datetime.now().isoformat()
        })

        result = {
            "success": sent_count > 0,
            "sent": sent_count,
            "requested": repeat,
            "target": str(target_id),
            "target_type": target_type
        }

        if errors:
            result["errors"] = errors
            result["partial_success"] = True

        return json.dumps(result)

    async def read_message_history(self, input_data: Dict[str, Any]) -> str:
        """Read recent message history from a channel.

        Enables self-reflection and context awareness:
        - "what did I say earlier?"
        - "did I already answer this?"
        - "what was the user asking about?"
        """
        print(f"[EMERGENT] read_message_history called")
        print(f"[EMERGENT]   Channel ID: {input_data.get('channel_id')}")
        print(f"[EMERGENT]   Limit: {input_data.get('limit', 50)}")

        channel_id = input_data.get('channel_id')
        limit = min(input_data.get('limit', 50), 100)  # Cap at 100

        if not channel_id:
            print(f"[EMERGENT] ERROR: Missing channel_id")
            return json.dumps({"error": "Missing channel_id", "success": False})

        try:
            # Try getting channel from cache first
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                print(f"[EMERGENT] Not in cache, trying to fetch channel (works for DMs)...")
                # Try fetching (works for DM channels too)
                try:
                    channel = await self.bot.fetch_channel(int(channel_id))
                    print(f"[EMERGENT] ✅ Found channel via fetch: {getattr(channel, 'name', 'DM')}")
                except Exception as e:
                    print(f"[EMERGENT] ❌ Channel not found: {channel_id} ({str(e)})")
                    # Debug info
                    guilds = [f"{g.name} ({g.id})" for g in self.bot.guilds]
                    print(f"[EMERGENT] Bot is in {len(self.bot.guilds)} guild(s): {guilds}")
                    all_channels = [f"{c.name} ({c.id})" for g in self.bot.guilds for c in g.text_channels[:5]]
                    print(f"[EMERGENT] Available text channels (first 5 per guild): {all_channels}")
                    return json.dumps({
                        "error": "Channel not found",
                        "success": False,
                        "debug_info": {
                            "requested_id": channel_id,
                            "available_channels": all_channels
                        }
                    })
            else:
                print(f"[EMERGENT] ✅ Found channel in cache: {getattr(channel, 'name', 'DM')}")

            messages = []
            async for msg in channel.history(limit=limit):
                messages.append({
                    'id': str(msg.id),
                    'author': msg.author.name,
                    'author_id': str(msg.author.id),
                    'content': msg.content[:500],  # Truncate long messages
                    'timestamp': msg.created_at.isoformat(),
                    'is_bot': msg.author.bot,
                    'mentions': [str(u.id) for u in msg.mentions]
                })

            # Log action
            self.action_history.append({
                'type': 'read_history',
                'channel_id': str(channel_id),
                'message_count': len(messages),
                'timestamp': datetime.now().isoformat()
            })

            return json.dumps({
                "success": True,
                "messages": messages,
                "count": len(messages),
                "channel_id": str(channel_id)
            })

        except Exception as e:
            return json.dumps({"error": str(e), "success": False})

    async def check_previous_actions(self, input_data: Dict[str, Any]) -> str:
        """Check what actions the bot has taken recently.

        Self-reflection capability:
        - "did I forget something?"
        - "what have I done so far?"
        - "have I already sent that message?"
        """
        action_type = input_data.get('action_type', 'all')
        limit = min(input_data.get('limit', 10), 50)

        if action_type != 'all':
            actions = [a for a in self.action_history if a['type'] == action_type]
        else:
            actions = self.action_history

        recent_actions = actions[-limit:]

        return json.dumps({
            "success": True,
            "actions": recent_actions,
            "count": len(recent_actions),
            "total_actions": len(self.action_history)
        })

    async def get_discord_context(self, input_data: Dict[str, Any]) -> str:
        """Get information about Discord server, channels, or members.

        Enables context-aware actions:
        - "who's online?"
        - "what channels exist?"
        - "tell everyone in the server..."
        """
        context_type = input_data.get('type', 'server')
        guild_id = input_data.get('guild_id')

        if not guild_id:
            return json.dumps({"error": "Missing guild_id", "success": False})

        try:
            guild = self.bot.get_guild(int(guild_id))
            if not guild:
                return json.dumps({"error": "Guild not found", "success": False})

            if context_type == 'server':
                return json.dumps({
                    "success": True,
                    "name": guild.name,
                    "id": str(guild.id),
                    "member_count": guild.member_count,
                    "channel_count": len(guild.channels),
                    "role_count": len(guild.roles)
                })

            elif context_type == 'channels':
                channels = []
                for c in guild.channels[:50]:  # Limit to 50
                    channels.append({
                        "name": c.name,
                        "id": str(c.id),
                        "type": str(c.type),
                        "category": c.category.name if c.category else None
                    })

                return json.dumps({
                    "success": True,
                    "channels": channels,
                    "count": len(channels)
                })

            elif context_type == 'members':
                # Get members (limited to prevent huge data)
                members = []
                for m in guild.members[:50]:
                    members.append({
                        "name": m.name,
                        "id": str(m.id),
                        "display_name": m.display_name,
                        "status": str(m.status),
                        "is_bot": m.bot,
                        "mention": m.mention
                    })

                return json.dumps({
                    "success": True,
                    "members": members,
                    "count": len(members),
                    "total": guild.member_count
                })

            else:
                return json.dumps({"error": f"Unknown context type: {context_type}", "success": False})

        except Exception as e:
            return json.dumps({"error": str(e), "success": False})

    async def execute(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute an emergent tool.

        Dispatcher for all emergent tool execution.
        """
        print(f"[EMERGENT] Executing: {tool_name}")
        print(f"[EMERGENT] Input: {tool_input}")

        try:
            if tool_name == "send_discord_message":
                result = await self.send_discord_message(tool_input)

            elif tool_name == "read_message_history":
                result = await self.read_message_history(tool_input)

            elif tool_name == "check_previous_actions":
                result = await self.check_previous_actions(tool_input)

            elif tool_name == "get_discord_context":
                result = await self.get_discord_context(tool_input)

            else:
                result = json.dumps({
                    "error": f"Unknown emergent tool: {tool_name}",
                    "success": False
                })

            print(f"[EMERGENT] Result: {result}")
            return result

        except Exception as e:
            error_result = json.dumps({
                "error": str(e),
                "tool": tool_name,
                "success": False
            })
            print(f"[EMERGENT] Error: {error_result}")
            return error_result
