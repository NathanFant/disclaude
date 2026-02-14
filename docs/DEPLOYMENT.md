# Deployment Guide

Complete guide for deploying the DisClaude bot with CI/CD, testing, and Railway deployment.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Running Tests](#running-tests)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Railway Deployment](#railway-deployment)
6. [Environment Variables](#environment-variables)
7. [Admin Setup](#admin-setup)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Python 3.11 or higher
- Git
- GitHub account (for CI/CD)
- Railway account (for hosting)
- Discord bot token
- Anthropic API key

---

## Local Development Setup

### 1. Clone and Install

```bash
git clone https://github.com/your-username/disclaude.git
cd disclaude

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Linux/Mac
export DISCORD_TOKEN="your_discord_token_here"
export ANTHROPIC_API_KEY="your_anthropic_key_here"
export ADMIN_USER_IDS="98113812770598912"  # Your Discord user ID

# Windows PowerShell
$env:DISCORD_TOKEN="your_discord_token_here"
$env:ANTHROPIC_API_KEY="your_anthropic_key_here"
$env:ADMIN_USER_IDS="98113812770598912"
```

### 3. Run Locally

```bash
python bot.py
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_config.py -v
```

### Run with Coverage

```bash
pip install pytest-cov
pytest tests/ --cov=. --cov-report=html
```

### Test Before Committing

```bash
# Always run tests before pushing!
pytest tests/ -v && git push
```

---

## CI/CD Pipeline

### GitHub Actions Workflow

The project uses GitHub Actions for automated testing and deployment.

**Location**: `.github/workflows/ci.yml`

**Triggers**:
- Push to `main` branch
- Pull requests to `main` branch

**Pipeline Steps**:

1. **Checkout Code** - Gets latest code from repository
2. **Set up Python** - Installs Python 3.11
3. **Install Dependencies** - Installs from `requirements.txt`
4. **Run Tests** - Executes all tests with pytest
5. **Deploy** - Confirms Railway auto-deployment

### Viewing CI/CD Results

1. Go to your GitHub repository
2. Click **Actions** tab
3. View workflow runs and logs

### CI/CD Secrets Setup

Add these secrets to your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:
   - `DISCORD_TOKEN` (optional, for testing)
   - `ANTHROPIC_API_KEY` (optional, for testing)

**Note**: Tests will use dummy values if secrets are not set.

---

## Railway Deployment

### First-Time Setup

1. **Create Railway Account**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

2. **Create New Project**
   - Click **New Project**
   - Select **Deploy from GitHub repo**
   - Choose your `disclaude` repository
   - Railway auto-detects Python project

3. **Configure Environment Variables**

   Go to your project → **Variables** and add:

   | Variable | Value | Required |
   |----------|-------|----------|
   | `DISCORD_TOKEN` | Your Discord bot token | ✅ Yes |
   | `ANTHROPIC_API_KEY` | Your Anthropic API key | ✅ Yes |
   | `ADMIN_USER_IDS` | Your Discord user ID (comma-separated for multiple) | ✅ Yes |
   | `MAX_CONVERSATION_HISTORY` | `10` | ❌ No (default: 10) |
   | `RATE_LIMIT_MESSAGES` | `5` | ❌ No (default: 5) |
   | `RATE_LIMIT_SECONDS` | `60` | ❌ No (default: 60) |

4. **Deploy**
   - Railway deploys automatically after variables are set
   - Monitor logs for successful connection

### Auto-Deployment

Railway automatically deploys when you push to the `main` branch:

```bash
git add .
git commit -m "Update bot"
git push origin main
# Railway auto-deploys in ~2 minutes
```

### Manual Redeploy

If needed, manually redeploy:
- Go to Railway project
- Click **Deploy** → **Redeploy**

### Viewing Logs

1. Go to your Railway project
2. Click on your service
3. Click **View Logs**
4. Look for:
   ```
   DisClaude#1234 has connected to Discord!
   Bot is in X guilds
   Synced X slash command(s)
   ```

---

## Environment Variables

### Required Variables

#### `DISCORD_TOKEN`
- **Description**: Your Discord bot token
- **Where to get**: [Discord Developer Portal](https://discord.com/developers/applications) → Your App → Bot → Reset Token
- **Example**: `MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.XyZ123...` (70+ characters)

#### `ANTHROPIC_API_KEY`
- **Description**: Your Anthropic API key for Claude
- **Where to get**: [Anthropic Console](https://console.anthropic.com) → API Keys
- **Example**: `sk-ant-api03-...`

#### `ADMIN_USER_IDS`
- **Description**: Comma-separated list of Discord user IDs with admin privileges
- **Where to get**: Right-click your profile in Discord → Copy ID (enable Developer Mode first)
- **Example**: `98113812770598912` or `123456789,987654321` (multiple admins)

### Optional Variables

#### `COMMAND_PREFIX`
- **Default**: `!`
- **Description**: Prefix for text commands (legacy)

#### `MAX_CONVERSATION_HISTORY`
- **Default**: `10`
- **Description**: Number of messages to remember per channel

#### `RATE_LIMIT_MESSAGES`
- **Default**: `5`
- **Description**: Maximum messages per time window

#### `RATE_LIMIT_SECONDS`
- **Default**: `60`
- **Description**: Time window for rate limiting (in seconds)

---

## Admin Setup

### Making Yourself Admin

1. **Get Your Discord User ID**
   - Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
   - Right-click your profile → **Copy ID**
   - You'll get something like: `98113812770598912`

2. **Add to Railway**
   - Go to Railway → Your Project → Variables
   - Add or update: `ADMIN_USER_IDS` = `98113812770598912`
   - Railway will auto-redeploy

3. **Verify Admin Access**
   - In Discord, type: `/admin`
   - You should see the admin panel with statistics

### Admin Commands

| Command | Description |
|---------|-------------|
| `/admin` | View bot statistics and admin panel |
| `/setmodel` | Force a specific Claude model (future feature) |
| `/clearall` | Clear all conversation histories across all channels |

### Multiple Admins

To add multiple admins, separate IDs with commas:

```bash
ADMIN_USER_IDS=98113812770598912,123456789012345678,987654321098765432
```

---

## Dynamic Model Selection

The bot automatically chooses the best Claude model based on question complexity:

### Model Tiers

| Model | Use Case | Cost | Speed |
|-------|----------|------|-------|
| **Haiku** | Simple questions, greetings | Cheapest | Fastest |
| **Sonnet** | Most questions, balanced | Medium | Balanced |
| **Opus** | Complex tasks, code, analysis | Highest | Slowest |

### Automatic Selection Examples

**→ Haiku** (Simple):
- "hello"
- "what is Python?"
- "ping"

**→ Sonnet** (Balanced):
- "How do I sort a list in Python?"
- "Explain object-oriented programming"

**→ Opus** (Complex):
- "Write a program that..."
- "Debug this code: ```...```"
- "Compare and contrast..."
- Long, detailed questions

---

## Troubleshooting

### Tests Failing

**Problem**: `pytest` command not found

**Solution**:
```bash
pip install pytest pytest-asyncio
```

**Problem**: Import errors during tests

**Solution**: Make sure environment variables are set:
```bash
export DISCORD_TOKEN="A"*70  # Dummy token for tests
export ANTHROPIC_API_KEY="sk-ant-test"
pytest tests/ -v
```

### Railway Deployment Issues

**Problem**: `ValueError: DISCORD_TOKEN appears invalid`

**Solution**:
- Check Railway Variables tab
- Make sure token is 70+ characters
- No quotes, no `DISCORD_TOKEN=` prefix
- Just the raw token value

**Problem**: Bot not responding in Discord

**Solution**:
1. Check Railway logs for connection message
2. Verify **MESSAGE CONTENT INTENT** is enabled in Discord Developer Portal
3. Re-invite bot with correct permissions

**Problem**: Admin commands not working

**Solution**:
1. Verify `ADMIN_USER_IDS` is set in Railway
2. Verify your Discord User ID is correct
3. Redeploy Railway after adding the variable

### GitHub Actions Failing

**Problem**: Tests fail on GitHub but pass locally

**Solution**:
- Check that test dependencies are in `requirements.txt`
- Ensure tests don't require external services
- Check GitHub Actions logs for specific errors

---

## Deployment Checklist

Before deploying to production:

- [ ] All tests pass locally (`pytest tests/ -v`)
- [ ] Environment variables are set in Railway
- [ ] `ADMIN_USER_IDS` includes your Discord user ID
- [ ] Discord bot has **MESSAGE CONTENT INTENT** enabled
- [ ] Code is pushed to `main` branch
- [ ] GitHub Actions CI passes
- [ ] Railway deployment logs show successful connection
- [ ] Bot responds to `/ping` in Discord
- [ ] Admin commands work (`/admin`)

---

## Quick Reference

### Deploy New Changes

```bash
# 1. Run tests
pytest tests/ -v

# 2. Commit and push
git add .
git commit -m "Description of changes"
git push origin main

# 3. Monitor Railway
# Go to Railway → View Logs
# Wait for successful deployment
```

### Check Bot Status

```bash
# Railway Logs
railway logs

# Or visit Railway dashboard → View Logs
```

### Emergency Rollback

If something breaks:

1. Go to Railway → Deployments
2. Find last working deployment
3. Click **Redeploy**

---

## Additional Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Railway Documentation](https://docs.railway.app/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pytest Documentation](https://docs.pytest.org/)

---

**Questions or Issues?**
Open an issue on GitHub or check the logs in Railway!
