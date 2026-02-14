# Agent Integration Steps

How to turn your bot into an agent in 3 simple steps.

## Step 1: Update get_claude_response()

Replace your current `get_claude_response()` function in `bot.py` with this:

```python
async def get_claude_response(messages: list, model: str = None, context: dict = None) -> str:
    """Get response from Claude API with tool use support."""
    from tool_definitions import TOOLS
    from tools import tool_executor

    if model is None:
        last_message = messages[-1]['content'] if messages else ""
        model = determine_model_complexity(last_message, messages)

    # Build system prompt
    system_prompt = personality.get_system_prompt()

    # Add context about the current user/channel
    if context:
        system_prompt += f"\n\nCurrent context:"
        system_prompt += f"\n- User ID: {context.get('user_id')}"
        system_prompt += f"\n- Channel ID: {context.get('channel_id')}"
        if context.get('username'):
            system_prompt += f"\n- Username: {context.get('username')}"

    try:
        # Initial request to Claude with tools
        response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,  # ← Enable tool use
            messages=messages
        )

        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Collect all tool uses
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            # Execute all tools
            tool_results = []
            for tool_use in tool_uses:
                print(f"[AGENT] 🔧 Using tool: {tool_use.name}")

                # Execute the tool
                result = await tool_executor.execute(tool_use.name, tool_use.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                })

            # Send tool results back to Claude for final response
            messages_with_results = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": tool_results}
            ]

            # Get final response after tool execution
            final_response = await asyncio.to_thread(
                client.messages.create,
                model=model,
                max_tokens=2048,
                system=system_prompt,
                tools=TOOLS,
                messages=messages_with_results
            )

            # Extract text from final response
            text_blocks = [block.text for block in final_response.content if hasattr(block, 'text')]
            return '\n'.join(text_blocks)

        # No tool use, just return the text
        return response.content[0].text

    except Exception as e:
        return f"Error: {str(e)}"
```

## Step 2: Update on_message() to Pass Context

Find the part in `on_message()` where you call `get_claude_response()` and update it:

```python
# OLD:
response_text = await get_claude_response(messages_list)

# NEW:
context = {
    'user_id': str(message.author.id),
    'channel_id': str(message.channel.id),
    'guild_id': str(message.guild.id) if message.guild else None,
    'username': message.author.name
}
response_text = await get_claude_response(messages_list, context=context)
```

## Step 3: Test It!

Deploy and try these commands:

```
"What's my Skyblock skill average?"
```

Claude will:
1. Realize it needs to get Skyblock stats
2. Call `get_skyblock_stats(discord_id="your_id")`
3. Receive the data
4. Respond with a natural answer

```
"My Minecraft username is NathanFant"
```

Claude will:
1. Recognize you want to link an account
2. Call `link_minecraft_account(discord_id="...", minecraft_username="NathanFant")`
3. Receive confirmation
4. Tell you it's linked with your stats

---

## Complete Modified bot.py Sections

### Import additions (top of file)

```python
from tool_definitions import TOOLS
from tools import tool_executor
```

### Full get_claude_response() function

```python
async def get_claude_response(messages: list, model: str = None, context: dict = None) -> str:
    """Get response from Claude API with tool use support."""
    if model is None:
        last_message = messages[-1]['content'] if messages else ""
        model = determine_model_complexity(last_message, messages)

    system_prompt = personality.get_system_prompt()

    if context:
        system_prompt += f"\n\nCurrent context:"
        system_prompt += f"\n- User ID: {context.get('user_id')}"
        system_prompt += f"\n- Channel ID: {context.get('channel_id')}"
        if context.get('username'):
            system_prompt += f"\n- Username: {context.get('username')}"

    try:
        response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            max_tokens=2048,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_uses = [block for block in response.content if block.type == "tool_use"]

            tool_results = []
            for tool_use in tool_uses:
                print(f"[AGENT] 🔧 Using tool: {tool_use.name}")
                result = await tool_executor.execute(tool_use.name, tool_use.input)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": result
                })

            messages_with_results = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": tool_results}
            ]

            final_response = await asyncio.to_thread(
                client.messages.create,
                model=model,
                max_tokens=2048,
                system=system_prompt,
                tools=TOOLS,
                messages=messages_with_results
            )

            text_blocks = [block.text for block in final_response.content if hasattr(block, 'text')]
            return '\n'.join(text_blocks)

        return response.content[0].text

    except Exception as e:
        return f"Error: {str(e)}"
```

### Updated on_message() section

Find this section in your `on_message()`:

```python
# OLD CODE:
async with message.channel.typing():
    messages_list = list(conversation)
    response_text = await get_claude_response(messages_list)
    conversation.append({"role": "assistant", "content": response_text})

# NEW CODE:
async with message.channel.typing():
    messages_list = list(conversation)

    # Build context
    context = {
        'user_id': str(message.author.id),
        'channel_id': str(message.channel.id),
        'guild_id': str(message.guild.id) if message.guild else None,
        'username': message.author.name
    }

    # Get response with tool support
    response_text = await get_claude_response(messages_list, context=context)
    conversation.append({"role": "assistant", "content": response_text})
```

---

## Testing the Agent

### Test 1: Link Account

**Say**: "My Minecraft name is NathanFant"

**Expected**:
- Bot realizes you want to link
- Calls `link_minecraft_account`
- Responds: "I've linked your account! Found 5 Skyblock profiles, your active one is Papaya with skill average 32.5!"

### Test 2: Get Stats

**Say**: "What's my Skyblock skill average?"

**Expected**:
- Bot checks if you're linked
- Calls `get_skyblock_stats`
- Responds: "Your skill average is 32.5! Your top skills are Combat (45), Mining (38), Farming (35)."

### Test 3: Check Link Status

**Say**: "Am I linked?"

**Expected**:
- Bot calls `check_user_link_status`
- Responds: "Yes, you're linked to NathanFant (UUID: 47fb7b99...)"

### Test 4: Multi-Step

**Say**: "Link me to NathanFant and show my stats"

**Expected**:
- Bot calls `link_minecraft_account`
- Bot calls `get_skyblock_stats`
- Responds with both results in a natural way!

---

## Troubleshooting

### "Error: Unknown tool"

Make sure `tools.py` and `tool_definitions.py` are imported in `bot.py`:

```python
from tool_definitions import TOOLS
from tools import tool_executor
```

### "Tool execution failed"

Check Railway logs for `[TOOL]` messages to see what happened:

```
[TOOL] Executing: get_skyblock_stats
[TOOL] Input: {'discord_id': '123456'}
[TOOL] Result: {"success": true, ...}
```

### Agent doesn't use tools

Make sure:
1. `tools=TOOLS` is passed to `client.messages.create()`
2. Tool definitions are in `tool_definitions.py`
3. System prompt doesn't tell Claude to avoid tools

---

## What's Next?

Once this works, you can:

1. **Add more tools** (search web, manage server, etc.)
2. **Chain tools** (Claude can use multiple tools in sequence)
3. **Add safety checks** (rate limiting, permissions)
4. **Create complex workflows** (multi-step tasks)

Your bot is now a **true agent**! 🤖✨
