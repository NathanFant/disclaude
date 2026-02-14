"""Discord bot with Claude AI integration."""
import discord
from discord import app_commands
from discord.ext import commands
import anthropic
from collections import defaultdict, deque
from datetime import datetime, timedelta
import re
import config
import asyncio
from personality import PersonalityTracker

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

# Conversation memory: {channel_id: deque of messages}
conversations = defaultdict(lambda: deque(maxlen=config.MAX_CONVERSATION_HISTORY))

# Rate limiting: {user_id: deque of timestamps}
rate_limits = defaultdict(lambda: deque(maxlen=config.RATE_LIMIT_MESSAGES))

# Personality tracker
personality = PersonalityTracker()


def check_rate_limit(user_id: int) -> bool:
    """Check if user is rate limited."""
    now = datetime.now()
    user_timestamps = rate_limits[user_id]

    # Remove old timestamps
    while user_timestamps and now - user_timestamps[0] > timedelta(seconds=config.RATE_LIMIT_SECONDS):
        user_timestamps.popleft()

    # Check if limit exceeded
    if len(user_timestamps) >= config.RATE_LIMIT_MESSAGES:
        return False

    # Add current timestamp
    user_timestamps.append(now)
    return True


def is_admin(user_id: int) -> bool:
    """Check if user is an admin."""
    return user_id in config.ADMIN_LIST


def determine_model_complexity(content: str, conversation_history: list) -> str:
    """Determine which Claude model to use based on question complexity."""
    content_lower = content.lower()

    # Simple questions - use Haiku (fast & cheap)
    simple_patterns = [
        'what is', 'who is', 'when is', 'where is',
        'how are you', 'hello', 'hi ', 'hey',
        'ping', 'status', 'help'
    ]
    if any(pattern in content_lower for pattern in simple_patterns) and len(content) < 50:
        return config.CLAUDE_MODEL_SIMPLE

    # Complex questions - use Opus (most capable)
    complex_indicators = [
        'explain in detail', 'analyze', 'compare and contrast',
        'write a program', 'create a', 'design a system',
        'debug', 'refactor', 'optimize',
        'architecture', 'implementation'
    ]
    code_blocks = '```' in content
    long_question = len(content) > 200
    long_conversation = len(conversation_history) > 6

    if (any(indicator in content_lower for indicator in complex_indicators) or
        code_blocks or
        (long_question and long_conversation)):
        return config.CLAUDE_MODEL_COMPLEX

    # Default to Sonnet for balanced performance
    return config.CLAUDE_MODEL_MEDIUM


async def get_claude_response(messages: list, model: str = None) -> str:
    """Get response from Claude API with optional model override."""
    if model is None:
        # Determine model based on the last user message
        last_message = messages[-1]['content'] if messages else ""
        model = determine_model_complexity(last_message, messages)

    # Get evolving personality system prompt
    system_prompt = personality.get_system_prompt()

    try:
        response = await asyncio.to_thread(
            client.messages.create,
            model=model,
            max_tokens=2048,  # Increased for better responses
            system=system_prompt,  # Evolving personality
            messages=messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


def split_message(text: str, max_length: int = config.MAX_MESSAGE_LENGTH) -> list:
    """Split long messages into chunks."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Find last newline within limit
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1:
            split_pos = max_length

        chunks.append(text[:split_pos])
        text = text[split_pos:].lstrip()

    return chunks


@bot.event
async def on_ready():
    """Bot startup event."""
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is in {len(bot.guilds)} guilds')

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')


def is_bot_mentioned(message) -> bool:
    """Check if the bot is mentioned by @mention or by name."""
    # Check for @mention
    if bot.user.mentioned_in(message):
        return True

    # Check for DM
    if isinstance(message.channel, discord.DMChannel):
        return True

    # Check if bot's name is mentioned in the message (case-insensitive)
    bot_name = bot.user.display_name.lower()
    message_lower = message.content.lower()

    # Check for bot name at start, in middle, or with punctuation
    return bot_name in message_lower


def clean_bot_mention(content: str) -> str:
    """Remove bot mentions and name from message content."""
    # Remove @mention format
    content = content.replace(f'<@{bot.user.id}>', '').replace(f'<@!{bot.user.id}>', '')

    # Remove bot name (case-insensitive)
    bot_name = bot.user.display_name
    # Match bot name with optional punctuation/whitespace around it
    pattern = re.compile(rf'\b{re.escape(bot_name)}\b[,:]?\s*', re.IGNORECASE)
    content = pattern.sub('', content)

    return content.strip()


@bot.event
async def on_message(message):
    """Handle incoming messages."""
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Only respond if bot is mentioned or in DM
    if not is_bot_mentioned(message):
        await bot.process_commands(message)
        return

    # Check rate limit
    if not check_rate_limit(message.author.id):
        await message.reply(
            f"⏱️ Rate limit exceeded. Please wait before sending more messages.",
            mention_author=False
        )
        return

    # Get conversation history
    channel_id = message.channel.id
    conversation = conversations[channel_id]

    # Clean mention and bot name from message
    content = clean_bot_mention(message.content)

    # Skip if message is empty after cleaning
    if not content:
        await message.reply(
            "Hi! How can I help you?",
            mention_author=False
        )
        return

    # Record interaction for personality evolution
    personality.record_interaction(message.author.id, content)

    # Add user message to conversation
    conversation.append({"role": "user", "content": content})

    # Show typing indicator
    async with message.channel.typing():
        # Get Claude's response
        messages_list = list(conversation)
        response_text = await get_claude_response(messages_list)

        # Add assistant response to conversation
        conversation.append({"role": "assistant", "content": response_text})

    # Split and send response
    chunks = split_message(response_text)
    for chunk in chunks:
        await message.reply(chunk, mention_author=False)

    # Process other commands
    await bot.process_commands(message)


@bot.tree.command(name="ask", description="Ask Claude a question")
@app_commands.describe(question="Your question for Claude")
async def ask_command(interaction: discord.Interaction, question: str):
    """Slash command to ask Claude a question."""
    # Check rate limit
    if not check_rate_limit(interaction.user.id):
        await interaction.response.send_message(
            "⏱️ Rate limit exceeded. Please wait before sending more questions.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    # Get conversation history
    channel_id = interaction.channel_id
    conversation = conversations[channel_id]

    # Add user message
    conversation.append({"role": "user", "content": question})

    # Get Claude's response
    messages_list = list(conversation)
    response_text = await get_claude_response(messages_list)

    # Add assistant response
    conversation.append({"role": "assistant", "content": response_text})

    # Split and send response
    chunks = split_message(response_text)
    await interaction.followup.send(chunks[0])
    for chunk in chunks[1:]:
        await interaction.followup.send(chunk)


@bot.tree.command(name="clear", description="Clear conversation history")
async def clear_command(interaction: discord.Interaction):
    """Slash command to clear conversation history."""
    channel_id = interaction.channel_id
    conversations[channel_id].clear()
    await interaction.response.send_message(
        "🗑️ Conversation history cleared!",
        ephemeral=True
    )


@bot.tree.command(name="history", description="Show conversation history length")
async def history_command(interaction: discord.Interaction):
    """Slash command to check conversation history."""
    channel_id = interaction.channel_id
    conversation = conversations[channel_id]

    user_messages = sum(1 for msg in conversation if msg["role"] == "user")
    assistant_messages = sum(1 for msg in conversation if msg["role"] == "assistant")

    await interaction.response.send_message(
        f"📊 Conversation history:\n"
        f"• User messages: {user_messages}\n"
        f"• Assistant messages: {assistant_messages}\n"
        f"• Total: {len(conversation)} messages\n"
        f"• Max capacity: {config.MAX_CONVERSATION_HISTORY} messages",
        ephemeral=True
    )


@bot.tree.command(name="ping", description="Check bot latency")
async def ping_command(interaction: discord.Interaction):
    """Slash command to check bot latency."""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(
        f"🏓 Pong! Latency: {latency}ms",
        ephemeral=True
    )


@bot.tree.command(name="admin", description="[Admin] Admin panel and statistics")
async def admin_command(interaction: discord.Interaction):
    """Admin-only command to view bot statistics."""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            "❌ This command is only available to bot administrators.",
            ephemeral=True
        )
        return

    total_conversations = len(conversations)
    total_messages = sum(len(conv) for conv in conversations.values())
    total_users_tracked = len(rate_limits)

    admin_info = (
        f"🔧 **Admin Panel**\n\n"
        f"**Statistics:**\n"
        f"• Active conversations: {total_conversations}\n"
        f"• Total messages stored: {total_messages}\n"
        f"• Users tracked: {total_users_tracked}\n"
        f"• Guilds: {len(bot.guilds)}\n\n"
        f"**Your Info:**\n"
        f"• User ID: {interaction.user.id}\n"
        f"• Admin: ✅ Yes\n"
        f"• Total Admins: {len(config.ADMIN_LIST)}"
    )

    await interaction.response.send_message(admin_info, ephemeral=True)


@bot.tree.command(name="setmodel", description="[Admin] Force a specific Claude model for next response")
@app_commands.describe(
    model="Choose the model: haiku (fast), sonnet (balanced), opus (powerful)"
)
@app_commands.choices(model=[
    app_commands.Choice(name="Haiku (Fast & Cheap)", value="haiku"),
    app_commands.Choice(name="Sonnet (Balanced)", value="sonnet"),
    app_commands.Choice(name="Opus (Most Capable)", value="opus"),
])
async def setmodel_command(interaction: discord.Interaction, model: str):
    """Admin-only command to override model selection."""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            "❌ This command is only available to bot administrators.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"✅ Model preference noted: **{model.title()}**\n"
        f"Note: Currently model selection is automatic. "
        f"This command is for future functionality.",
        ephemeral=True
    )


@bot.tree.command(name="clearall", description="[Admin] Clear all conversation histories")
async def clearall_command(interaction: discord.Interaction):
    """Admin-only command to clear all conversation histories."""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            "❌ This command is only available to bot administrators.",
            ephemeral=True
        )
        return

    count = len(conversations)
    conversations.clear()

    await interaction.response.send_message(
        f"🗑️ Cleared {count} conversation histories!",
        ephemeral=True
    )


@bot.tree.command(name="personality", description="View the bot's current personality traits")
async def personality_command(interaction: discord.Interaction):
    """View bot's evolving personality."""
    summary = personality.get_personality_summary()
    traits = summary['traits']

    # Create trait bars
    def trait_bar(value: int) -> str:
        filled = int(value / 10)
        empty = 10 - filled
        return f"{'█' * filled}{'░' * empty} {value}%"

    personality_info = (
        f"🎭 **Bot Personality**\n\n"
        f"**Traits:**\n"
        f"😊 Friendliness: {trait_bar(traits['friendliness'])}\n"
        f"🎩 Formality: {trait_bar(traits['formality'])}\n"
        f"😄 Humor: {trait_bar(traits['humor'])}\n"
        f"📝 Verbosity: {trait_bar(traits['verbosity'])}\n"
        f"🤝 Helpfulness: {trait_bar(traits['helpfulness'])}\n\n"
        f"**Experience:**\n"
        f"• Interactions: {summary['interactions']}\n"
        f"• Unique users: {summary['unique_users']}\n"
        f"• Uptime: {summary['uptime_hours']:.1f} hours\n\n"
    )

    if summary['top_topics']:
        topics_str = ", ".join(f"{k} ({v})" for k, v in list(summary['top_topics'].items())[:3])
        personality_info += f"**Top Topics:** {topics_str}\n"

    await interaction.response.send_message(personality_info, ephemeral=True)


@bot.tree.command(name="systemprompt", description="[Admin] View current system prompt")
async def systemprompt_command(interaction: discord.Interaction):
    """Admin command to view the current personality system prompt."""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            "❌ This command is only available to bot administrators.",
            ephemeral=True
        )
        return

    system_prompt = personality.get_system_prompt()

    await interaction.response.send_message(
        f"**Current System Prompt:**\n\n{system_prompt}",
        ephemeral=True
    )


@bot.tree.command(name="resetpersonality", description="[Admin] Reset personality to default")
async def resetpersonality_command(interaction: discord.Interaction):
    """Admin command to reset bot personality."""
    if not is_admin(interaction.user.id):
        await interaction.response.send_message(
            "❌ This command is only available to bot administrators.",
            ephemeral=True
        )
        return

    old_interactions = personality.interaction_count
    personality.reset_personality()

    await interaction.response.send_message(
        f"🔄 Personality reset to default!\n"
        f"Previous interactions: {old_interactions}",
        ephemeral=True
    )


if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)
