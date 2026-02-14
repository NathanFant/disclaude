"""Diagnostic to find where skill XP is stored in Hypixel API."""
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

UUID = "47fb7b99858042c3a7b4795af44ea41d"
API_KEY = config.HYPIXEL_API_KEY

print("="*70)
print("DIAGNOSING SKILL DATA STRUCTURE")
print("="*70)

# Fetch profiles
params = urllib.parse.urlencode({'key': API_KEY, 'uuid': UUID})
url = f"https://api.hypixel.net/v2/skyblock/profiles?{params}"

with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())
    profiles = data.get('profiles', [])

# Find the selected profile (Papaya)
selected_profile = None
for profile in profiles:
    if profile.get('selected'):
        selected_profile = profile
        break

if not selected_profile:
    print("No selected profile found")
    sys.exit(1)

print(f"Selected Profile: {selected_profile.get('cute_name')}")

# Get player data
members = selected_profile.get('members', {})
player_data = members.get(UUID)

if not player_data:
    print("Player data not found")
    sys.exit(1)

print(f"\n[Top-level keys in player_data]")
print(f"Keys: {list(player_data.keys())[:20]}")

# Search for skill-related keys
print(f"\n[Searching for skill/experience keys]")
skill_keys = []
for key in player_data.keys():
    if 'skill' in key.lower() or 'experience' in key.lower() or 'xp' in key.lower():
        skill_keys.append(key)
        print(f"  - {key}: {player_data[key]}")

# Always check nested structures
print(f"\n[Checking nested structures]")
for key in ['leveling', 'player_data', 'profile', 'player_stats']:
    if key in player_data:
        nested = player_data[key]
        if isinstance(nested, dict):
            print(f"\n  [{key}]")
            print(f"    All keys: {list(nested.keys())}")
            # Look for experience keys
            exp_keys = [k for k in nested.keys() if 'experience' in k.lower()]
            if exp_keys:
                print(f"    Experience keys found:")
                for ek in exp_keys[:10]:
                    print(f"      - {ek}: {nested[ek]}")

# Check specific expected keys
print(f"\n[Checking expected skill keys]")
skills = ['farming', 'mining', 'combat', 'foraging', 'fishing', 'enchanting', 'alchemy', 'taming']
for skill in skills:
    key = f'experience_skill_{skill}'
    value = player_data.get(key, 'NOT FOUND')
    print(f"  {key}: {value}")

print("\n" + "="*70)
