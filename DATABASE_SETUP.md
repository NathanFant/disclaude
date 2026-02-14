# Database Setup for Railway

The bot now uses a **PostgreSQL database** to persist user data across deployments!

---

## Why Database?

Railway's filesystem is **ephemeral** - any files written are lost when the bot restarts or redeploys. To persist data like:
- Discord → Minecraft account links
- User profiles
- Scheduled reminders (future)

We need a database!

---

## Setup in Railway (5 minutes)

### Step 1: Add PostgreSQL Database

1. Go to your Railway project
2. Click **"+ New"** button
3. Select **"Database"**
4. Choose **"PostgreSQL"**
5. Railway will create the database and set environment variables automatically!

### Step 2: Link to Your Service

1. Go to your bot service (not the database)
2. Click **"Variables"** tab
3. You should see **`DATABASE_URL`** automatically added
4. If not, manually add it:
   - **Name**: `DATABASE_URL`
   - **Value**: Click "Reference" → Select PostgreSQL → `DATABASE_URL`

### Step 3: Redeploy

Railway will auto-redeploy. Watch the logs for:

```
[DATABASE] Connecting to: postgresql://...
[DATABASE] Creating tables...
[DATABASE] Database initialized
[USER_PROFILES] Database-backed storage initialized
```

### Step 4: Test It

Link your account:
```
/sblink username:YourMinecraftName
```

Then **redeploy the bot manually** (or wait for next deployment) and try:
```
/sb
```

Your link should persist! ✅

---

## How It Works

### Local Development (SQLite)

When running locally (no `DATABASE_URL` set):
- Uses **SQLite** database file (`disclaude.db`)
- File stored in project directory
- Good for testing

### Production (PostgreSQL)

When running on Railway (with `DATABASE_URL`):
- Uses **PostgreSQL** database
- Data persists across deployments
- Shared across all bot instances
- Free tier: 500MB storage (plenty for Discord bots)

---

## Database Schema

### `user_profiles` Table

| Column | Type | Description |
|--------|------|-------------|
| `discord_id` | BIGINT | Discord user ID (primary key) |
| `minecraft_username` | VARCHAR | Minecraft username |
| `minecraft_uuid` | VARCHAR | Minecraft UUID |

**Example:**
```sql
discord_id          | minecraft_username | minecraft_uuid
--------------------|--------------------|----------------------------------
123456789012345678  | NathanFant        | abc123def456...
987654321098765432  | Technoblade       | xyz789...
```

---

## Verifying Database Connection

### Check Railway Logs

Look for these messages on startup:

✅ **Success:**
```
[DATABASE] Connecting to: postgresql://default:***@...
[DATABASE] Creating tables...
[DATABASE] Database initialized
[USER_PROFILES] Database-backed storage initialized
```

❌ **Failed:**
```
[DATABASE] Error: ...
```

### Common Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `DATABASE_URL` not found | PostgreSQL not linked | Add PostgreSQL service and link it |
| Connection refused | Database not ready | Wait a minute, redeploy |
| Authentication failed | Wrong credentials | Re-link the DATABASE_URL variable |

---

## Migrating Existing Data

If you had users linked before the database:

**Option 1: Have users re-link**
```
Everyone: /sblink username:YourName
```

**Option 2: Manual import** (if you have the old JSON file)
```python
# Local script to import from user_profiles.json
import json
from database import engine, UserProfile, SessionLocal

with open('user_profiles.json', 'r') as f:
    data = json.load(f)

db = SessionLocal()
for discord_id, username in data['profiles'].items():
    uuid = data['uuids'].get(discord_id)
    if uuid:
        profile = UserProfile(
            discord_id=int(discord_id),
            minecraft_username=username,
            minecraft_uuid=uuid
        )
        db.add(profile)
db.commit()
db.close()
```

---

## Database Management

### View All Linked Users

**Option 1: Railway Dashboard**
1. Go to PostgreSQL service
2. Click "Data" tab
3. Run query:
   ```sql
   SELECT * FROM user_profiles;
   ```

**Option 2: psql (if you have it installed)**
```bash
# Get DATABASE_URL from Railway
psql $DATABASE_URL

# List all profiles
SELECT * FROM user_profiles;

# Count profiles
SELECT COUNT(*) FROM user_profiles;
```

### Backup Database

Railway has automatic backups, but you can also:

```bash
# Export data
pg_dump $DATABASE_URL > backup.sql

# Restore data
psql $DATABASE_URL < backup.sql
```

---

## Future Enhancements

The database can be extended to store:

### Scheduled Reminders
```python
class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    message = Column(String)
    scheduled_time = Column(DateTime)
```

### Personality State
```python
class PersonalityState(Base):
    __tablename__ = 'personality'
    id = Column(Integer, primary_key=True)
    trait_name = Column(String)
    trait_value = Column(Integer)
    updated_at = Column(DateTime)
```

### Skyblock Cache
```python
class SkyblockCache(Base):
    __tablename__ = 'skyblock_cache'
    uuid = Column(String, primary_key=True)
    data = Column(JSON)
    cached_at = Column(DateTime)
```

---

## Cost

**Railway Free Tier:**
- PostgreSQL: 500MB storage
- Shared CPU
- Free for hobby projects

**If you exceed free tier:**
- $5/month for more resources
- Worth it for a reliable Discord bot!

---

## Troubleshooting

### "No module named 'psycopg2'"

Missing dependencies. Redeploy with updated `requirements.txt`.

### "Can't connect to database"

1. Check `DATABASE_URL` is set in Railway
2. Make sure PostgreSQL service is running
3. Wait 1-2 minutes after creating database
4. Redeploy the bot

### "Table doesn't exist"

Database tables are created automatically on first run. Check logs for:
```
[DATABASE] Creating tables...
```

If missing, manually trigger:
```python
from database import init_db
init_db()
```

---

## Quick Start Checklist

- [ ] Add PostgreSQL to Railway project
- [ ] Link `DATABASE_URL` to bot service
- [ ] Redeploy bot
- [ ] Check logs for database initialization
- [ ] Test with `/sblink username:YourName`
- [ ] Manually redeploy
- [ ] Verify with `/sb` - should remember you!

---

**Your bot now has persistent storage! 🎉📊**
