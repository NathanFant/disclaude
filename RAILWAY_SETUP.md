# Railway Deployment Guide

## Quick Fix for "401 Unauthorized" Error

If you're getting a `discord.errors.LoginFailure: Improper token has been passed.` error, your Discord token is not set correctly in Railway.

### Fix Steps:

1. **Get a Fresh Discord Token**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Select your application
   - Go to **Bot** section
   - Click **Reset Token** (this invalidates the old one)
   - Copy the new token immediately (you won't see it again!)

2. **Set the Token in Railway**
   - Go to your Railway project
   - Click on your service/deployment
   - Go to **Variables** tab
   - Find `DISCORD_TOKEN` or add it if missing
   - **IMPORTANT**: Paste the token WITHOUT any quotes, spaces, or extra characters
   - Example format: `XXXXX.YYYYY.ZZZZZ` (your actual token will be much longer)
   - Click outside the field to save

3. **Redeploy**
   - Railway should auto-redeploy when you change variables
   - If not, click **Deploy** → **Redeploy**

## Common Mistakes:

❌ **Wrong**: `"YOUR_TOKEN_HERE"` (has quotes)
❌ **Wrong**: `DISCORD_TOKEN=YOUR_TOKEN_HERE` (has variable name)
❌ **Wrong**: Token with spaces or newlines

✅ **Correct**: Just the raw token value, no quotes or extra text

## Environment Variables Needed:

| Variable | Required | Example | Where to Get |
|----------|----------|---------|--------------|
| `DISCORD_TOKEN` | ✅ Yes | `MTIzNDU2...` | [Discord Developer Portal](https://discord.com/developers/applications) → Bot |
| `ANTHROPIC_API_KEY` | ✅ Yes | `sk-ant-api03-...` | [Anthropic Console](https://console.anthropic.com) → API Keys |
| `MAX_CONVERSATION_HISTORY` | ❌ No | `10` | Defaults to 10 |
| `RATE_LIMIT_MESSAGES` | ❌ No | `5` | Defaults to 5 |
| `RATE_LIMIT_SECONDS` | ❌ No | `60` | Defaults to 60 |

## Verifying It Works:

After deployment, check Railway logs. You should see:
```
DisClaude#1234 has connected to Discord!
Bot is in X guilds
Synced 4 slash command(s)
```

If you still see `401 Unauthorized`, the token is still wrong. Double-check you copied it correctly.
