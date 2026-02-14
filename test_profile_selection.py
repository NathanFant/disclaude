"""Test profile selection logic using standard library."""
import urllib.request
import urllib.parse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

# Load .env.local
env_local_path = os.path.join(os.path.dirname(__file__), '.env.local')
if os.path.exists(env_local_path):
    with open(env_local_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

if 'ATHROPIC_API_KEY' in os.environ and 'ANTHROPIC_API_KEY' not in os.environ:
    os.environ['ANTHROPIC_API_KEY'] = os.environ['ATHROPIC_API_KEY']

import config

def get_active_profile_logic(profiles, uuid):
    """Replicate the get_active_profile logic."""
    clean_uuid = uuid.replace('-', '')

    print("\n[Method 1: Checking for 'selected' field]")
    for profile in profiles:
        if profile.get('selected'):
            print(f"✅ Found selected profile: {profile.get('cute_name')}")
            return profile

    print("  No profile with 'selected: true' at profile level")

    print("\n[Method 2: Finding most recent activity from objectives]")
    active_profile = None
    latest_timestamp = 0
    latest_activity = None

    for profile in profiles:
        if not profile or 'members' not in profile:
            continue

        member_data = profile['members'].get(clean_uuid)
        if not member_data:
            continue

        objectives = member_data.get('objectives', {})
        if objectives:
            for obj_data in objectives.values():
                if isinstance(obj_data, dict) and 'completed_at' in obj_data:
                    timestamp = obj_data['completed_at']
                    if timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                        active_profile = profile
                        latest_activity = datetime.fromtimestamp(timestamp / 1000)

    if active_profile:
        print(f"✅ Found active profile by timestamp: {active_profile.get('cute_name')}")
        print(f"   Last activity: {latest_activity.strftime('%Y-%m-%d %H:%M:%S')}")
        return active_profile

    print("  No recent activity found")

    print("\n[Method 3: Fallback to first available profile]")
    for profile in profiles:
        if profile.get('members', {}).get(clean_uuid):
            print(f"✅ Using first available profile: {profile.get('cute_name')}")
            return profile

    print("❌ No profile found")
    return None


print("="*70)
print("TESTING PROFILE SELECTION LOGIC")
print("="*70)

UUID = "47fb7b99858042c3a7b4795af44ea41d"
API_KEY = config.HYPIXEL_API_KEY

# Fetch profiles
params = urllib.parse.urlencode({'key': API_KEY, 'uuid': UUID})
url = f"https://api.hypixel.net/v2/skyblock/profiles?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    profiles = data.get('profiles', [])

print(f"\nFetched {len(profiles)} profiles")
print("\nProfile summary:")
for i, p in enumerate(profiles, 1):
    selected = "⭐ SELECTED" if p.get('selected') else ""
    print(f"  {i}. {p.get('cute_name'):15} {selected}")

# Test the logic
active = get_active_profile_logic(profiles, UUID)

print("\n" + "="*70)
print("RESULT")
print("="*70)
if active:
    print(f"✅ Active Profile: {active.get('cute_name')}")
    print(f"   Profile ID: {active.get('profile_id')}")
    print(f"   Selected: {active.get('selected', False)}")
else:
    print("❌ Failed to determine active profile")

print("\n" + "="*70)
print("Expected: Papaya (the profile with 'selected: true')")
print("="*70)
