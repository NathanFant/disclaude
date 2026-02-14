"""Diagnostic tool to check database connection and data."""
import os
import sys

# Load .env.local if exists
env_local_path = os.path.join(os.path.dirname(__file__), '.env.local')
if os.path.exists(env_local_path):
    with open(env_local_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

from database.db import DATABASE_URL, engine, SessionLocal, UserProfile, init_db

print("="*70)
print("DATABASE CONNECTION DIAGNOSTIC")
print("="*70)

# Check DATABASE_URL
print(f"\n[1] Database URL Check")
print(f"DATABASE_URL: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL.split('///')[0]}")

if DATABASE_URL.startswith('sqlite'):
    print("⚠️  Using SQLite (local file-based database)")
    print("   This will NOT persist on Railway deployments!")
    print("   SQLite file location: disclaude.db")
elif DATABASE_URL.startswith('postgresql'):
    print("✅ Using PostgreSQL (persistent database)")
    print("   This WILL persist on Railway deployments")
else:
    print("❌ Unknown database type")

# Test connection
print(f"\n[2] Connection Test")
try:
    db = SessionLocal()
    print("✅ Successfully connected to database")
    db.close()
except Exception as e:
    print(f"❌ Failed to connect to database: {e}")
    sys.exit(1)

# Check if tables exist
print(f"\n[3] Table Check")
try:
    init_db()
    print("✅ Tables initialized (user_profiles table exists)")
except Exception as e:
    print(f"❌ Failed to initialize tables: {e}")
    sys.exit(1)

# Check for existing data
print(f"\n[4] Data Check")
try:
    db = SessionLocal()
    profiles = db.query(UserProfile).all()

    if profiles:
        print(f"✅ Found {len(profiles)} linked profile(s):")
        for profile in profiles:
            print(f"   - Discord ID: {profile.discord_id}")
            print(f"     Minecraft: {profile.minecraft_username}")
            print(f"     UUID: {profile.minecraft_uuid}")
    else:
        print("⚠️  No profiles found in database")
        print("   This is normal if no one has used /sblink yet")

    db.close()
except Exception as e:
    print(f"❌ Failed to query database: {e}")
    sys.exit(1)

# Recommendations
print(f"\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)

if DATABASE_URL.startswith('sqlite'):
    print("\n⚠️  YOU ARE USING SQLITE - PROFILES WILL NOT PERSIST ON RAILWAY!")
    print("\nTo fix this, you need to:")
    print("1. Add PostgreSQL database to your Railway project")
    print("2. Link DATABASE_URL to your bot service")
    print("3. Redeploy the bot")
    print("\nSee DATABASE_SETUP.md for detailed instructions")
elif DATABASE_URL.startswith('postgresql'):
    print("\n✅ PostgreSQL is configured correctly!")
    print("   Profiles will persist across deployments")

    if not profiles:
        print("\n💡 No profiles linked yet. Test with:")
        print("   /sblink username:YourMinecraftName")

print("\n" + "="*70)
