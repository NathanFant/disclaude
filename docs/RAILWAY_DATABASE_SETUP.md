# Railway PostgreSQL Setup Guide

Your `/sblink` profiles aren't persisting because the database isn't configured on Railway yet.

## Quick Fix (5 minutes)

### Step 1: Add PostgreSQL to Railway

1. Go to your Railway project: https://railway.app
2. Click **"+ New"** button in your project
3. Select **"Database"**
4. Choose **"PostgreSQL"**
5. Railway will create the database ✅

### Step 2: Link Database to Bot Service

1. Click on your **bot service** (not the database)
2. Go to **"Variables"** tab
3. Look for `DATABASE_URL` variable

**If DATABASE_URL exists:**
- ✅ You're done! Skip to Step 3

**If DATABASE_URL does NOT exist:**
1. Click **"+ New Variable"**
2. Click **"Add Reference"**
3. Select your PostgreSQL database
4. Choose `DATABASE_URL`
5. Click **"Add"**

### Step 3: Verify Setup

In Railway bot service logs, look for:

**✅ Success (PostgreSQL):**
```
[DATABASE] Connecting to: postgresql://...
[DATABASE] Creating tables...
[DATABASE] Database initialized
[USER_PROFILES] Database-backed storage initialized
```

**❌ Problem (SQLite):**
```
[DATABASE] Connecting to: sqlite:///disclaude.db
```

If you see SQLite, the DATABASE_URL isn't linked correctly. Go back to Step 2.

### Step 4: Test It

1. In Discord: `/sblink username:YourMinecraftName`
2. You should see your link with UUID and profile info
3. **Manually trigger a redeploy** in Railway (or wait for next auto-deploy)
4. After redeployment, try `/sb`
5. Your link should still work! ✅

---

## Checking Database Status on Railway

### Option 1: Check Bot Logs

Railway → Your Bot Service → Deployments → Latest → Logs

Look for the `[DATABASE]` lines on startup.

### Option 2: Run Diagnostic Script

SSH into Railway and run:

```bash
python check_database.py
```

This will tell you:
- ✅ or ❌ Database type (PostgreSQL vs SQLite)
- ✅ or ❌ Connection status
- Number of linked profiles

### Option 3: Query Database Directly

Railway → PostgreSQL Service → Data tab → Run query:

```sql
SELECT * FROM user_profiles;
```

This shows all linked Discord → Minecraft profiles.

---

## Troubleshooting

### Issue: Logs show "sqlite:///disclaude.db"

**Problem:** DATABASE_URL not set or linked incorrectly

**Fix:**
1. Railway → Bot Service → Variables
2. Delete any incorrect DATABASE_URL
3. Click "+ New Variable" → "Add Reference"
4. Select PostgreSQL → DATABASE_URL
5. Redeploy

### Issue: "No module named 'psycopg2'"

**Problem:** Missing database dependencies

**Fix:**
1. Check that `requirements.txt` includes:
   ```
   SQLAlchemy>=2.0.0
   psycopg2-binary>=2.9.0
   ```
2. Redeploy (Railway will install dependencies)

### Issue: "Could not connect to database"

**Problem:** Database not ready or wrong URL

**Fix:**
1. Wait 1-2 minutes after creating PostgreSQL
2. Check DATABASE_URL format starts with `postgresql://`
3. Railway auto-corrects `postgres://` to `postgresql://` in code
4. Redeploy

### Issue: Profiles work, then disappear

**Problem:** Using SQLite (ephemeral filesystem)

**Fix:**
1. Add PostgreSQL (Step 1)
2. Link DATABASE_URL (Step 2)
3. Users must re-link with `/sblink` (one-time migration)

---

## Migration: SQLite → PostgreSQL

If you already have users linked with SQLite:

**Option 1: Have users re-link** (Recommended)
```
Everyone: /sblink username:YourName
```

**Option 2: Manual data migration** (Advanced)

1. Before switching to PostgreSQL, download SQLite data:
   ```bash
   # In Railway shell (with SQLite)
   python -c "
   from database import SessionLocal, UserProfile
   import json

   db = SessionLocal()
   profiles = db.query(UserProfile).all()

   data = [
       {
           'discord_id': p.discord_id,
           'minecraft_username': p.minecraft_username,
           'minecraft_uuid': p.minecraft_uuid
       }
       for p in profiles
   ]

   with open('profiles_backup.json', 'w') as f:
       json.dump(data, f)

   print(json.dumps(data, indent=2))
   "
   ```

2. Save the JSON output

3. After switching to PostgreSQL, restore:
   ```bash
   # In Railway shell (with PostgreSQL)
   python -c "
   import json
   from database import SessionLocal, UserProfile, init_db

   # Your saved data here
   data = [
       {'discord_id': 123456, 'minecraft_username': 'Name', 'minecraft_uuid': 'uuid'},
       # ... more profiles
   ]

   init_db()
   db = SessionLocal()

   for profile_data in data:
       profile = UserProfile(**profile_data)
       db.add(profile)

   db.commit()
   db.close()
   print(f'Migrated {len(data)} profiles')
   "
   ```

---

## Verifying It Works

1. **Link account:** `/sblink username:NathanFant`
2. **Check it works:** `/sb` (should show your stats)
3. **Trigger redeploy** in Railway
4. **Test again:** `/sb` (should still show your stats) ✅

If step 4 fails, PostgreSQL isn't configured correctly.

---

## Database Info

**Free Tier:**
- PostgreSQL: 500MB storage
- Plenty for Discord bot user profiles
- Included in Railway's $5 usage credit

**Storage estimates:**
- Each profile: ~100 bytes
- 500MB = ~5 million profiles
- You won't hit the limit with a Discord bot 😄

---

## Quick Checklist

- [ ] PostgreSQL service added to Railway project
- [ ] DATABASE_URL linked to bot service
- [ ] Bot redeployed
- [ ] Logs show `postgresql://...` (not `sqlite:///`)
- [ ] Logs show "Database initialized"
- [ ] `/sblink` command works
- [ ] `/sb` command shows stats
- [ ] After redeploy, `/sb` still works ✅

---

**Need help?** Check the logs for `[DATABASE]` messages to see what's happening.
