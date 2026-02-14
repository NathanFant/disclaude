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


async def get_claude_response(messages: list) -> str:
    """Get response from Claude API."""
    try:
        response = await asyncio.to_thread(
            client.messages.create,
            model=config.CLAUDE_MODEL,
            max_tokens=1024,
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


if __name__ == "__main__":
    bot.run(config.DISCORD_TOKEN)
