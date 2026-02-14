"""Deep inspection for timestamp fields in Skyblock profiles."""
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

UUID = "47fb7b99858042c3a7b4795af44ea41d"
API_KEY = config.HYPIXEL_API_KEY

def find_timestamps(data, path="", max_depth=3, current_depth=0):
    """Recursively find all fields that look like timestamps."""
    timestamps = []

    if current_depth > max_depth:
        return timestamps

    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # Check if this looks like a timestamp
            if isinstance(value, (int, float)):
                # Timestamps are usually 10 or 13 digits
                if 1000000000 < value < 9999999999999:
                    try:
                        # Try as seconds
                        if value < 10000000000:
                            dt = datetime.fromtimestamp(value)
                        else:
                            # Try as milliseconds
                            dt = datetime.fromtimestamp(value / 1000)

                        timestamps.append({
                            'path': current_path,
                            'value': value,
                            'date': dt.strftime('%Y-%m-%d %H:%M:%S')
                        })
                    except:
                        pass

            # Recurse into nested structures
            elif isinstance(value, (dict, list)):
                timestamps.extend(find_timestamps(value, current_path, max_depth, current_depth + 1))

    elif isinstance(data, list):
        for i, item in enumerate(data[:5]):  # Only check first 5 items
            current_path = f"{path}[{i}]"
            timestamps.extend(find_timestamps(item, current_path, max_depth, current_depth + 1))

    return timestamps


print("="*70)
print("SEARCHING FOR TIMESTAMP FIELDS IN SKYBLOCK PROFILES")
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
    print(f"Profile ID: {profile.get('profile_id')}")
    print(f"Selected: {profile.get('selected', False)}")
    print(f"{'='*70}")

    # Check for 'selected' field at profile level
    if profile.get('selected'):
        print(f"⭐ This is the SELECTED profile!")

    # Find all timestamps in this profile
    our_uuid = UUID.replace('-', '')
    if our_uuid in profile.get('members', {}):
        member_data = profile['members'][our_uuid]

        print(f"\n[Searching for timestamps in member data...]")
        timestamps = find_timestamps(member_data, max_depth=3)

        if timestamps:
            # Sort by date (most recent first)
            timestamps.sort(key=lambda x: x['value'], reverse=True)

            print(f"\nFound {len(timestamps)} timestamp fields:")
            for ts in timestamps[:10]:  # Show top 10
                print(f"  {ts['path']}")
                print(f"    Value: {ts['value']}")
                print(f"    Date: {ts['date']}")
                print()
        else:
            print(f"  ❌ No timestamp fields found")

print("\n" + "="*70)
print("RECOMMENDATION")
print("="*70)
print("\nTo find the active profile:")
print("1. Use the 'selected' field at profile level (if present)")
print("2. Or use the most recent timestamp from member data")
print("="*70)
