"""Direct tests for Hypixel API endpoints without pytest."""
import aiohttp
import asyncio
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import config
from hypixel_client import hypixel_client


async def test_mojang_api():
    """Test 1: Mojang API - Get UUID from username."""
    print("\n" + "="*60)
    print("TEST 1: Mojang API - Get UUID from username")
    print("="*60)

    username = "NathanFant"
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    print(f"URL: {url}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            status = response.status
            print(f"Status: {status}")

            if status == 200:
                data = await response.json()
                print(f"✅ SUCCESS - Got 200 response")
                print(f"Response: {data}")
                print(f"UUID: {data.get('id')}")
                print(f"Username: {data.get('name')}")
                return data.get('id')
            else:
                print(f"❌ FAILED - Expected 200, got {status}")
                text = await response.text()
                print(f"Response: {text}")
                return None


async def test_hypixel_skyblock_profiles(uuid):
    """Test 2: Hypixel API - Get Skyblock profiles."""
    print("\n" + "="*60)
    print("TEST 2: Hypixel Skyblock Profiles API")
    print("="*60)

    if not uuid:
        print("❌ SKIPPED - No UUID available")
        return None

    api_key = config.HYPIXEL_API_KEY
    if not api_key:
        print("❌ SKIPPED - HYPIXEL_API_KEY not configured")
        return None

    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"UUID (original): {uuid}")

    # Remove dashes
    clean_uuid = uuid.replace('-', '')
    print(f"UUID (cleaned): {clean_uuid}")

    url = f"https://api.hypixel.net/v2/skyblock/profiles"
    params = {
        "key": api_key,
        "uuid": clean_uuid
    }
    print(f"URL: {url}")
    print(f"Params: uuid={clean_uuid}")

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            status = response.status
            print(f"Status: {status}")

            if status == 200:
                data = await response.json()
                print(f"✅ SUCCESS - Got 200 response")
                print(f"Response keys: {list(data.keys())}")
                print(f"Success field: {data.get('success')}")

                if data.get('success'):
                    profiles = data.get('profiles')
                    if profiles is None:
                        print(f"⚠️  No Skyblock profiles found")
                        print(f"   (Player hasn't played Hypixel Skyblock)")
                        return []
                    else:
                        print(f"Found {len(profiles)} profile(s)")
                        for i, profile in enumerate(profiles):
                            print(f"\nProfile {i+1}:")
                            print(f"  - ID: {profile.get('profile_id')}")
                            print(f"  - Name: {profile.get('cute_name')}")
                            print(f"  - Members: {len(profile.get('members', {}))}")
                        return profiles
                else:
                    cause = data.get('cause', 'Unknown')
                    print(f"❌ API returned success=false")
                    print(f"   Cause: {cause}")
                    return None
            elif status == 403:
                print(f"❌ FAILED - 403 Forbidden")
                print(f"   API key is invalid or missing permissions")
                text = await response.text()
                print(f"   Response: {text}")
                return None
            elif status == 429:
                print(f"❌ FAILED - 429 Rate Limited")
                return None
            else:
                print(f"❌ FAILED - Expected 200, got {status}")
                text = await response.text()
                print(f"Response: {text}")
                return None


async def test_hypixel_client_wrapper():
    """Test 3: Our HypixelClient wrapper methods."""
    print("\n" + "="*60)
    print("TEST 3: HypixelClient Wrapper Methods")
    print("="*60)

    username = "NathanFant"

    # Test get_uuid_from_username
    print(f"\n[get_uuid_from_username]")
    uuid = await hypixel_client.get_uuid_from_username(username)
    if uuid:
        print(f"✅ Got UUID: {uuid}")
    else:
        print(f"❌ Failed to get UUID")
        return

    # Test get_skyblock_profiles
    print(f"\n[get_skyblock_profiles]")
    profiles = await hypixel_client.get_skyblock_profiles(uuid)
    if profiles is None:
        print(f"❌ API error (returned None)")
    elif len(profiles) == 0:
        print(f"⚠️  No profiles found (player hasn't played Skyblock)")
    else:
        print(f"✅ Got {len(profiles)} profile(s)")

    # Test get_active_profile
    print(f"\n[get_active_profile]")
    profile = await hypixel_client.get_active_profile(uuid)
    if profile:
        print(f"✅ Got active profile: {profile.get('cute_name')}")

        # Test get_player_data_from_profile
        print(f"\n[get_player_data_from_profile]")
        player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)
        if player_data:
            print(f"✅ Got player data")
            print(f"   Data has {len(player_data)} keys")
            print(f"   Sample keys: {list(player_data.keys())[:5]}")
        else:
            print(f"❌ Failed to get player data")
    else:
        print(f"⚠️  No active profile found")


async def test_uuid_formats():
    """Test 4: Test both dashed and non-dashed UUID formats."""
    print("\n" + "="*60)
    print("TEST 4: UUID Format Compatibility")
    print("="*60)

    username = "NathanFant"

    # Get UUID
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}") as response:
            data = await response.json()
            uuid_no_dashes = data['id']

    # Create dashed version
    uuid_with_dashes = f"{uuid_no_dashes[:8]}-{uuid_no_dashes[8:12]}-{uuid_no_dashes[12:16]}-{uuid_no_dashes[16:20]}-{uuid_no_dashes[20:]}"

    print(f"UUID (no dashes): {uuid_no_dashes}")
    print(f"UUID (with dashes): {uuid_with_dashes}")

    api_key = config.HYPIXEL_API_KEY
    if not api_key:
        print("❌ SKIPPED - No API key")
        return

    # Test with dashes
    print(f"\nTesting WITH dashes...")
    async with aiohttp.ClientSession() as session:
        url = f"https://api.hypixel.net/v2/skyblock/profiles"
        params = {"key": api_key, "uuid": uuid_with_dashes}
        async with session.get(url, params=params) as response:
            status = response.status
            print(f"Status: {status}")
            if status == 200:
                data = await response.json()
                print(f"✅ Dashed UUID works - success: {data.get('success')}")
            else:
                print(f"❌ Dashed UUID failed")

    # Test without dashes
    print(f"\nTesting WITHOUT dashes...")
    async with aiohttp.ClientSession() as session:
        params = {"key": api_key, "uuid": uuid_no_dashes}
        async with session.get(url, params=params) as response:
            status = response.status
            print(f"Status: {status}")
            if status == 200:
                data = await response.json()
                print(f"✅ Non-dashed UUID works - success: {data.get('success')}")
            else:
                print(f"❌ Non-dashed UUID failed")


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("HYPIXEL API ENDPOINT TESTS")
    print("="*60)
    print(f"Testing with username: NathanFant")
    print(f"API Key configured: {'Yes' if config.HYPIXEL_API_KEY else 'No'}")

    try:
        # Test 1: Mojang API
        uuid = await test_mojang_api()

        # Test 2: Hypixel Skyblock Profiles
        await test_hypixel_skyblock_profiles(uuid)

        # Test 3: HypixelClient wrapper
        await test_hypixel_client_wrapper()

        # Test 4: UUID formats
        await test_uuid_formats()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETE")
        print("="*60)

    finally:
        # Clean up
        await hypixel_client.close()


if __name__ == "__main__":
    asyncio.run(main())
