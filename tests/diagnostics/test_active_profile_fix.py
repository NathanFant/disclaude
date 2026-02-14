"""Test the fixed get_active_profile method."""
import asyncio
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

from hypixel_client import hypixel_client

async def test_active_profile():
    """Test that get_active_profile correctly identifies the selected profile."""
    print("="*70)
    print("TESTING FIXED get_active_profile METHOD")
    print("="*70)

    username = "NathanFant"

    # Get UUID
    print(f"\n[Step 1] Getting UUID for {username}...")
    uuid = await hypixel_client.get_uuid_from_username(username)
    print(f"UUID: {uuid}")

    # Get active profile
    print(f"\n[Step 2] Getting active profile...")
    profile = await hypixel_client.get_active_profile(uuid)

    if profile:
        print(f"\n✅ SUCCESS!")
        print(f"Active Profile: {profile.get('cute_name')}")
        print(f"Profile ID: {profile.get('profile_id')}")
        print(f"Selected: {profile.get('selected', False)}")

        # Get player data from profile
        print(f"\n[Step 3] Getting player data from profile...")
        player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)

        if player_data:
            print(f"✅ Player data retrieved")
            print(f"Player data keys: {list(player_data.keys())[:10]}...")

            # Check for objectives
            objectives = player_data.get('objectives', {})
            if objectives:
                print(f"\nObjectives found: {len(objectives)}")

                # Find most recent objective
                most_recent = None
                most_recent_time = 0

                for obj_name, obj_data in objectives.items():
                    if isinstance(obj_data, dict) and 'completed_at' in obj_data:
                        timestamp = obj_data['completed_at']
                        if timestamp > most_recent_time:
                            most_recent_time = timestamp
                            most_recent = obj_name

                if most_recent:
                    from datetime import datetime
                    dt = datetime.fromtimestamp(most_recent_time / 1000)
                    print(f"Most recent activity: {most_recent}")
                    print(f"Timestamp: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"❌ Failed to get player data")
    else:
        print(f"\n❌ FAILED to get active profile")

    # Clean up
    await hypixel_client.close()

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nExpected result: Active profile should be 'Papaya' (selected: True)")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_active_profile())
