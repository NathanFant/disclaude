# Hypixel Skyblock Integration

DisClaude now integrates with the Hypixel API to track your Skyblock progress and provide personalized progression tips!

---

## Setup

### 1. Get a Hypixel API Key

1. Log into Hypixel (`mc.hypixel.net`)
2. Run the command: `/api new`
3. Copy the API key (it looks like: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

### 2. Add API Key to Railway

1. Go to your Railway project
2. Click **Variables**
3. Add new variable:
   - **Name**: `HYPIXEL_API_KEY`
   - **Value**: Your Hypixel API key (paste it without quotes)
4. Save and wait for auto-redeploy

### 3. Link Your Minecraft Account

In Discord, use:
```
/sblink username:YourMinecraftName
```

Now you're ready to use all Skyblock features!

---

## Commands

### `/sblink <username>`
**Link your Minecraft account to Discord**

- **Example**: `/sblink username:Technoblade`
- **Purpose**: Links your Discord to your Minecraft account
- **Note**: You only need to do this once
- **Privacy**: Link is stored in-memory (resets on bot restart)

---

### `/sb [username]`
**View your Skyblock profile and stats**

Shows comprehensive Skyblock statistics:
- Skill levels with progress bars
- Skill average (used for gear requirements)
- Slayer XP and kills
- Coin purse
- Profile name

**Usage:**
```
/sb                    # View your linked account
/sb username:Player    # View any player
```

**Example Output:**
```
🏝️ Skyblock Profile: Strawberry (Player: YourName)

📊 Skill Average: 32.4

Skills:
**Combat** 45 ████████░░ 67.3%
**Mining** 38 ██████░░░░ 42.1%
**Farming** 35 █████░░░░░ 23.8%
**Foraging** 30 ████░░░░░░ 15.6%
**Fishing** 28 ███░░░░░░░ 8.9%
**Enchanting** 32 █████░░░░░ 34.2%
**Alchemy** 29 ████░░░░░░ 19.5%
**Taming** 25 ██░░░░░░░░ 5.1%

⚔️ Total Slayer XP: 1,234,567
💰 Purse: 45,678,900 coins
```

---

### `/sbtips [username]`
**Get personalized progression advice**

Analyzes your stats and provides actionable tips:
- Identifies weak skills that need attention
- Suggests next progression steps
- Highlights untouched slayers
- Provides context-specific advice

**Usage:**
```
/sbtips                    # Tips for your linked account
/sbtips username:Player    # Tips for any player
```

**Example Output:**
```
💡 Progression Tips for YourName

🌱 Early Game Focus: Your skill average is low. Focus on
leveling combat, farming, and mining for a solid foundation.

⚠️ Weak Skills: Your foraging, fishing skills are lagging
behind. Balance them for better progression.

⚔️ Start Slayers: Begin doing slayer quests! They're
essential for combat progression and coins.

🎯 Zombie Slayer: You haven't progressed much in zombie.
Try some runs!
```

---

### `/sbunlink`
**Unlink your Minecraft account**

- Removes the link between Discord and Minecraft
- You can re-link anytime with `/sblink`

---

## Features

### Skill Tracking

Tracks all 8 main skills:
- **Combat** - Fighting mobs and players
- **Mining** - Breaking blocks
- **Farming** - Harvesting crops
- **Foraging** - Chopping wood
- **Fishing** - Catching fish
- **Enchanting** - Enchanting items
- **Alchemy** - Brewing potions
- **Taming** - Taming pets

Also tracks:
- **Carpentry** (minor skill)
- **Runecrafting** (minor skill)
- **Social** (minor skill)

### Skill Average Calculation

The bot calculates your **true skill average** (only counting the 8 main skills):
- Does not include Carpentry, Runecrafting, or Social
- Matches in-game requirements for gear/dungeons
- Shows progress bars for each skill

### Slayer Progress

Tracks all slayer types:
- **Revenant Horror** (Zombie)
- **Tarantula Broodfather** (Spider)
- **Sven Packmaster** (Wolf)
- **Voidgloom Seraph** (Enderman)
- **Inferno Demonlord** (Blaze)

Shows:
- Total XP per slayer type
- Total kills across all tiers
- Combined slayer XP

### Progression Tips

Smart analysis system that provides tips based on:

**Skill Average Ranges:**
- < 15: Early game tips (foundation building)
- < 30: Mid game tips (balanced progression)
- 30+: Advanced tips (optimization)

**Individual Skills:**
- Detects skills lagging behind average
- Suggests specific skills to level
- Prioritizes skills based on importance

**Slayer Progress:**
- Encourages starting slayers early
- Identifies neglected slayer types
- Suggests balanced slayer progression

---

## How It Works

### Data Flow

```
User runs /sb
    ↓
Bot checks if user is linked
    ↓
Fetches UUID from Mojang API
    ↓
Fetches Skyblock profiles from Hypixel API
    ↓
Finds most recently played profile
    ↓
Analyzes skills, slayers, coins
    ↓
Generates formatted display
    ↓
Sends to Discord
```

### API Endpoints Used

1. **Mojang API**: `https://api.mojang.com/users/profiles/minecraft/{username}`
   - Converts username to UUID
   - Free, no key required

2. **Hypixel Player API**: `https://api.hypixel.net/v2/player?uuid={uuid}`
   - Gets basic player info
   - Requires API key

3. **Hypixel Skyblock API**: `https://api.hypixel.net/v2/skyblock/profiles?uuid={uuid}`
   - Gets all Skyblock profiles
   - Includes skills, slayers, inventory, coins, etc.
   - Requires API key

### Skill Level Calculation

Skills use cumulative XP requirements:
- Level 1: 50 XP
- Level 10: 9,925 XP
- Level 20: 522,425 XP
- Level 30: 8,022,425 XP
- Level 40: 25,522,425 XP
- Level 50: 55,172,425 XP
- Level 60: 111,672,425 XP (max for most skills)

Some skills have different caps:
- **Runecrafting**: Max level 25
- **Social**: Max level 25
- **Others**: Max level 60

---

## Advanced Usage

### Checking Other Players

You don't need to link an account to check stats:

```
/sb username:Technoblade
/sbtips username:Refraction
```

Useful for:
- Comparing with friends
- Checking guild members
- Scouting competitive players

### Privacy & Security

**What's Stored:**
- Discord User ID ↔ Minecraft Username mapping (in-memory)
- Minecraft UUID (in-memory)

**What's NOT Stored:**
- API responses are not cached
- No permanent storage
- Resets when bot restarts

**API Key Security:**
- Stored in Railway environment variables
- Never exposed in bot responses
- Only used for Hypixel API calls

---

## Troubleshooting

### "Hypixel API key not configured"

**Problem**: `HYPIXEL_API_KEY` not set in Railway

**Solution:**
1. Get API key: `/api new` on Hypixel
2. Add to Railway Variables
3. Wait for redeploy

---

### "No Skyblock profiles found"

**Problem**: Player hasn't played Skyblock or API can't access

**Solution:**
- Make sure you've played Skyblock
- Check that your username is correct
- Ensure your Skyblock profiles are not hidden (API settings in-game)

---

### "Could not find Minecraft user"

**Problem**: Invalid username or Mojang API issue

**Solution:**
- Double-check spelling of username
- Try again in a few seconds (API might be rate-limited)
- Make sure it's a Java Edition account

---

### Stats seem outdated

**Problem**: Stats not updating immediately

**Solution:**
- Hypixel API caches data for a few minutes
- Play a bit, wait 5 minutes, then check again
- Data updates when you save and quit on Hypixel

---

## Future Enhancements

Possible additions:

### More Stats
- [ ] Dungeon stats (floor completions, class levels)
- [ ] Minion slots
- [ ] Collections progress
- [ ] Fairy souls found
- [ ] Pet score
- [ ] Museum completion

### Analysis Features
- [ ] Compare two players
- [ ] Track progress over time (requires database)
- [ ] Networth calculation (more accurate)
- [ ] Goal tracking ("Get combat 50", "1M slayer XP")

### Social Features
- [ ] Guild leaderboards
- [ ] Friend comparison
- [ ] Skyblock team stats

### AI Integration
- [ ] Ask Claude for Skyblock advice (uses personality + stats)
- [ ] "What should I do next?" with context-aware suggestions
- [ ] Money-making method recommendations

---

## API Rate Limits

Hypixel API limits:
- **120 requests per minute** per API key
- The bot uses ~2-3 requests per command

**If you hit limits:**
- Each `/sb` command uses 2 API calls
- With 120 req/min limit, you can check ~60 players/minute
- For most Discord servers, this is more than enough

---

## Examples

### Solo Player

```
/sblink username:Steve
/sb
/sbtips
```

You'll see your stats and get personalized advice based on your progression.

### Guild Officer Checking Members

```
/sb username:Member1
/sb username:Member2
/sbtips username:Member3
```

Check guild members' progress without linking.

### Competitive Player

Link your account, then regularly check:
```
/sb  # Check your progress
/sbtips  # Get optimization tips
```

Compare with competition:
```
/sb username:TopPlayer
```

---

## Technical Details

### File Structure

```
hypixel_client.py       # API client for Hypixel/Mojang
skyblock_analyzer.py    # Stats analysis and tip generation
user_profiles.py        # Discord ↔ Minecraft linking
bot.py                  # Discord commands
```

### Dependencies

Already included in `requirements.txt`:
- `aiohttp` - Async HTTP requests
- `discord.py` - Discord bot framework

### Memory Usage

- User profiles: ~50 bytes per linked user
- Minimal memory footprint
- No caching of API responses

---

## Contributing

Want to add more Skyblock features? Ideas:

1. **Parse inventory data** - Check for specific items
2. **Collection analysis** - Track collection levels
3. **Dungeon stats** - Show catacombs progress
4. **Price tracking** - Bazaar/AH price checks
5. **Enchantment tracking** - Which enchants you have

Pull requests welcome!

---

**Happy Skyblocking! 🏝️⛏️**
