# Claude Discord Bot

A feature-rich Discord bot powered by Claude AI with conversation memory, slash commands, and rate limiting.

## Features

- 🤖 **Claude AI Integration** - Responds using Claude Sonnet 4.5
- 💭 **Conversation Memory** - Remembers context within channels
- ⚡ **Slash Commands** - Modern Discord command interface
- 🛡️ **Rate Limiting** - Prevents spam and controls API costs
- 📝 **Long Message Support** - Automatically splits messages over Discord's limit

## Commands

### Slash Commands

- `/ask [question]` - Ask Claude a question
- `/clear` - Clear conversation history for the current channel
- `/history` - View conversation history stats
- `/ping` - Check bot latency

### Mention

- Mention the bot (`@BotName`) in any message to get a response with conversation context

## Setup

### Prerequisites

- Python 3.8 or higher
- Discord bot account ([create one here](https://discord.com/developers/applications))
- Anthropic API key ([get one here](https://console.anthropic.com))

### 1. Clone/Download

```bash
# If you're using this boilerplate, it's already in your directory!
cd discord-bot
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# You need:
# - DISCORD_TOKEN (from Discord Developer Portal)
# - ANTHROPIC_API_KEY (from console.anthropic.com)
```

### 4. Set Up Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application (or select existing)
3. Go to **Bot** section
   - Copy the **Token** → Put in `.env` as `DISCORD_TOKEN`
   - Enable **MESSAGE CONTENT INTENT** (required!)
4. Go to **OAuth2 > URL Generator**
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Messages/View Channels`, `Use Slash Commands`
   - Copy generated URL and invite bot to your server

### 5. Run the Bot

```bash
python bot.py
```

You should see:

```
YourBotName#1234 has connected to Discord!
Bot is in 1 guilds
Synced 4 slash command(s)
```

## Configuration

Edit `.env` to customize:

```env
# Bot behavior
COMMAND_PREFIX=!                  # Prefix for text commands (optional)
MAX_CONVERSATION_HISTORY=10       # Messages to remember per channel
RATE_LIMIT_MESSAGES=5             # Max messages per time window
RATE_LIMIT_SECONDS=60             # Time window in seconds
```

## Hosting

For 24/7 operation, see hosting options:

- **Railway** - Easy deployment with free tier
- **fly.io** - Good free tier for small bots
- **Oracle Cloud** - Best free tier (permanent)
- **Your own VPS** - Full control

See setup guide: [How to host for free](#)

## Usage Examples

### In Discord:

**Mention the bot:**

```
@ClaudeBot what's the weather like today?
```

**Use slash commands:**

```
/ask How do I create a function in Python?
/clear
/history
```

## Cost Estimation

- **Hosting**: Free (with free tiers) to ~$5-10/mo
- **Claude API**: ~$0.003-0.015 per message
  - 100 messages/day ≈ $3-45/month
  - 1000 messages/day ≈ $30-450/month

Use rate limiting to control costs!

## Troubleshooting

### Bot doesn't respond to messages

- Check **MESSAGE CONTENT INTENT** is enabled in Discord Developer Portal
- Make sure you're mentioning the bot or using slash commands

### "Module not found" error

- Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
- Reinstall requirements: `pip install -r requirements.txt`

### Slash commands not showing

- Wait a few minutes after starting bot (Discord needs to sync)
- Try kicking and re-inviting the bot with updated permissions

### Rate limit errors from Anthropic

- You're hitting API rate limits
- Increase `RATE_LIMIT_SECONDS` or decrease usage
- Check your API tier at console.anthropic.com

## Development

### Project Structure

```
discord-bot/
├── bot.py              # Main bot code
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create from .env.example)
├── .env.example       # Example environment file
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

### Adding Features

To add new slash commands, use this template:

```python
@bot.tree.command(name="mycommand", description="Description here")
async def my_command(interaction: discord.Interaction):
    await interaction.response.send_message("Response here")
```

## License

This is a boilerplate project - use it however you want!

## Support

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Discord Developer Portal](https://discord.com/developers/docs)

---

Built with ❤️ using Claude AI
