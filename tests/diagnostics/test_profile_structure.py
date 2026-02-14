"""Test to inspect the actual Skyblock profile data structure."""
import urllib.request
import urllib.parse
import json
import os
import sys

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

# Test data
UUID = "47fb7b99858042c3a7b4795af44ea41d"
API_KEY = config.HYPIXEL_API_KEY

print("="*70)
print("INSPECTING SKYBLOCK PROFILE DATA STRUCTURE")
print("="*70)

# Fetch profiles
params = urllib.parse.urlencode({'key': API_KEY, 'uuid': UUID})
url = f"https://api.hypixel.net/v2/skyblock/profiles?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    profiles = data.get('profiles', [])

print(f"\nFound {len(profiles)} profiles\n")

for i, profile in enumerate(profiles):
    print(f"\n{'='*70}")
    print(f"PROFILE {i+1}: {profile.get('cute_name')}")
    print(f"{'='*70}")

    # Top-level profile keys
    print(f"\n[Top-level profile keys]")
    print(f"Keys: {list(profile.keys())}")

    # Check for last_save at profile level
    if 'last_save' in profile:
        print(f"\n✅ Found 'last_save' at profile level: {profile['last_save']}")

    # Check members
    members = profile.get('members', {})
    print(f"\n[Members]")
    print(f"Number of members: {len(members)}")
    print(f"Member UUIDs: {list(members.keys())}")

    # Find our UUID
    our_uuid = UUID.replace('-', '')
    if our_uuid in members:
        member_data = members[our_uuid]
        print(f"\n[Our Member Data]")
        print(f"Top-level keys in member data: {list(member_data.keys())[:20]}...")  # First 20 keys

        # Check for last_save
        if 'last_save' in member_data:
            print(f"\n✅ Found 'last_save' in member data: {member_data['last_save']}")

            # Convert timestamp to human readable
            from datetime import datetime
            timestamp = member_data['last_save']
            if timestamp > 0:
                dt = datetime.fromtimestamp(timestamp / 1000)  # Hypixel uses milliseconds
                print(f"   Date: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"\n❌ No 'last_save' field in member data")
            print(f"   Looking for similar fields...")
            for key in member_data.keys():
                if 'save' in key.lower() or 'time' in key.lower() or 'date' in key.lower():
                    print(f"   - {key}: {member_data[key]}")

    # Check for banking or other profile-level info
    if 'banking' in profile:
        banking = profile['banking']
        if 'last_save' in banking:
            print(f"\n✅ Found 'last_save' in banking: {banking['last_save']}")

print("\n" + "="*70)
print("INSPECTION COMPLETE")
print("="*70)
