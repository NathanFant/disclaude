# Agent Capabilities

Your bot is now a **true agent** - it can think, use tools, and take actions.

## What is an Agent?

**Regular chatbot**: Responds to messages
**Agent**: Responds AND performs actions using tools

Your bot can now:
- ✅ Fetch Skyblock stats when asked
- ✅ Link Minecraft accounts naturally
- ✅ Send messages to users/channels
- ✅ Read conversation history
- ✅ Self-reflect and correct mistakes
- ✅ Figure out creative solutions

## Example Conversations

### Skyblock Stats (Pre-defined Tool)
```
You: "What's my Skyblock skill average?"

Bot thinks: Need to get stats
Bot uses: get_skyblock_stats(discord_id="123")
Bot responds: "Your skill average is 32.5! Combat: 45, Mining: 38, Farming: 35"
```

### Creative Spam (Emergent Behavior)
```
You: "tell @NathanFant 'chicken nugget' 57 times"

Bot thinks: Need to send message repeatedly
Bot uses: send_discord_message(target="<@id>", message="chicken nugget", repeat=57)
Bot responds: "Done! Sent 'chicken nugget' 57 times! 🐔"
```

### Self-Correction (Emergent)
```
You: "hey you forgot to send me my stats"

Bot thinks: Let me check what I did
Bot uses: read_message_history()
Bot sees: User asked for stats, I said "checking..." but never responded
Bot realizes: I DID forget!
Bot uses: get_skyblock_stats()
Bot responds: "You're right! Sorry about that. Your skill average is 32.5..."
```

### Context-Aware Multi-Step (Emergent)
```
You: "who's online?"

Bot uses: get_discord_context(type="members")
Bot responds: "Alice, Bob, Charlie are online"

You: "tell them all to join vc"

Bot remembers: The 3 online members
Bot uses: send_discord_message() for each
Bot responds: "Messaged all 3 members!"
```

## Available Tools

### Pre-defined Tools (Skyblock/Bot Management)

**get_skyblock_stats** - Fetch Hypixel Skyblock statistics
**link_minecraft_account** - Link Discord to Minecraft
**create_reminder** - Schedule reminders
**check_user_link_status** - Check if user is linked

### Emergent Tools (General Actions)

**send_discord_message** - Send to any user/channel, with repetition
- Can spam if requested ("send 'hello' 10 times")
- Rate limited (20/minute)

**read_message_history** - Read previous messages
- Understand context
- Self-correct mistakes

**check_previous_actions** - Self-reflection
- See what the bot has done
- Verify completed tasks

**get_discord_context** - Get server info
- List channels
- See who's online
- Get server details

## How It Works

```
User message
    ↓
Claude receives message + available tools
    ↓
Claude decides: "I need to use a tool"
    ↓
Claude calls tool (e.g., get_skyblock_stats)
    ↓
Bot executes tool, returns result
    ↓
Claude receives result
    ↓
Claude responds naturally with the information
```

## Tool Chaining

Claude can use multiple tools in sequence:

```
You: "link me to NathanFant and show my stats"

Claude:
1. link_minecraft_account(username="NathanFant")
2. get_skyblock_stats(user_id)
3. Responds: "Linked! Your skill average is 32.5..."
```

## Safety Features

✅ **Rate limiting** - 20 messages/minute max
✅ **Caps** - Max 50 repetitions
✅ **Action history** - Tracks all actions
✅ **Error handling** - Graceful failures
✅ **Context isolation** - Each channel separate

## What Makes It Emergent?

**Pre-defined approach:**
```python
if user_says("spam"):
    send_spam()  # Need this function pre-written
```

**Emergent approach:**
```python
# Claude figures out to use general tool creatively
send_discord_message(message="...", repeat=57)
```

No need to pre-define every possible action!

## Examples of Emergence

### Self-Awareness
```
You: "did you already tell me that?"
Bot: *Checks previous actions* → "Yes, I mentioned it 5 minutes ago"
```

### Context Understanding
```
You: "what did we talk about yesterday?"
Bot: *Reads message history* → Summarizes conversation
```

### Creative Problem Solving
```
You: "notify everyone about the maintenance"
Bot: *Gets member list* → *Messages each person*
```

### Error Recovery
```
You: "you said you'd remind me but didn't"
Bot: *Checks actions* → "You're right, let me set that reminder now"
```

## Tool Definitions

Located in:
- `tool_definitions.py` - Pre-defined Skyblock/bot tools
- `tool_definitions_emergent.py` - General-purpose tools

## Tool Execution

Located in:
- `tools.py` - Executes pre-defined tools
- `tools_emergent.py` - Executes emergent tools

## Adding New Tools

To add a new tool:

1. **Define in tool_definitions.py:**
```python
{
    "name": "my_new_tool",
    "description": "What this tool does",
    "input_schema": {
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "..."}
        },
        "required": ["param"]
    }
}
```

2. **Implement in tools.py:**
```python
async def my_new_tool(input_data: Dict[str, Any]) -> str:
    result = do_something(input_data['param'])
    return json.dumps({"success": True, "result": result})
```

3. **Add to executor:**
```python
if tool_name == "my_new_tool":
    return await my_new_tool(tool_input)
```

## Limitations

- No file system access (by design)
- No arbitrary code execution (safety)
- Rate limits on messaging (prevent spam)
- Context limited to current conversation

## Best Practices

✅ **Let Claude decide** - Don't force tool use, let it figure out when needed
✅ **Clear descriptions** - Tool descriptions help Claude understand when to use them
✅ **Error handling** - Always return JSON with success/error status
✅ **Rate limiting** - Prevent abuse with limits
✅ **Logging** - Track tool usage with action history

## Troubleshooting

**Bot doesn't use tools:**
- Check tool definitions are loaded
- Verify `tools=ALL_TOOLS` in API call
- Check Claude API response for tool_use

**Tool execution fails:**
- Check Railway logs for `[AGENT]` messages
- Verify tool input matches schema
- Check return format is JSON string

**Rate limit errors:**
- Normal! Prevents spam
- Wait 1 minute and try again
- Adjust limits in `tools_emergent.py`

## Status

✅ **Implemented and Active**

Your bot NOW has full agent capabilities. Just talk to it naturally:

- "What's my Skyblock skill average?"
- "Tell @person hello 10 times"
- "Did you already answer this?"
- "Who's online right now?"

It will figure out what to do! 🤖✨
