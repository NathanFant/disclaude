"""Simple API tests using standard library."""
import urllib.request
import urllib.parse
import json
import os
import sys

# Load environment variables
sys.path.insert(0, os.path.dirname(__file__))

# Set dummy tokens for testing (config requires them)
if 'DISCORD_TOKEN' not in os.environ:
    os.environ['DISCORD_TOKEN'] = 'MTIzNDU2Nzg5MDEyMzQ1Njc4OTAxMjM0NTY3ODkw.ABCDEF.1234567890123456789012345678901234567890'
if 'ANTHROPIC_API_KEY' not in os.environ:
    os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-api03-dummy_key_for_testing_purposes_only'

import config


def test_mojang_api(username="NathanFant"):
    """Test Mojang API to get UUID."""
    print("\n" + "="*70)
    print("TEST 1: Mojang API - Get UUID from Username")
    print("="*70)

    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    print(f"URL: {url}")
    print(f"Username: {username}")

    try:
        with urllib.request.urlopen(url) as response:
            status = response.status
            data = json.loads(response.read().decode())

            print(f"\n✅ STATUS: {status}")
            print(f"Response: {json.dumps(data, indent=2)}")

            uuid = data.get('id')
            name = data.get('name')

            print(f"\n📋 RESULTS:")
            print(f"  UUID: {uuid}")
            print(f"  Username: {name}")

            if status == 200:
                print(f"\n✅ TEST PASSED - Got 200 response")
                return uuid
            else:
                print(f"\n❌ TEST FAILED - Expected 200, got {status}")
                return None

    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP ERROR: {e.code} - {e.reason}")
        return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return None


def test_hypixel_skyblock_profiles(uuid):
    """Test Hypixel Skyblock Profiles API."""
    print("\n" + "="*70)
    print("TEST 2: Hypixel Skyblock Profiles API")
    print("="*70)

    if not uuid:
        print("❌ SKIPPED - No UUID provided")
        return None

    api_key = config.HYPIXEL_API_KEY
    if not api_key:
        print("❌ SKIPPED - HYPIXEL_API_KEY not configured in environment")
        print("   Set HYPIXEL_API_KEY in your .env file or environment variables")
        return None

    print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
    print(f"UUID (original): {uuid}")

    # Clean UUID (remove dashes)
    clean_uuid = uuid.replace('-', '')
    print(f"UUID (cleaned): {clean_uuid}")

    # Build URL with parameters
    params = {
        'key': api_key,
        'uuid': clean_uuid
    }
    query_string = urllib.parse.urlencode(params)
    url = f"https://api.hypixel.net/v2/skyblock/profiles?{query_string}"

    print(f"\nURL: https://api.hypixel.net/v2/skyblock/profiles")
    print(f"Params: uuid={clean_uuid}, key={api_key[:8]}...")

    try:
        with urllib.request.urlopen(url) as response:
            status = response.status
            data = json.loads(response.read().decode())

            print(f"\n✅ STATUS: {status}")
            print(f"Response keys: {list(data.keys())}")

            success = data.get('success', False)
            print(f"Success field: {success}")

            if status == 200:
                print(f"\n✅ TEST PASSED - Got 200 response")

                if success:
                    profiles = data.get('profiles')

                    if profiles is None:
                        print(f"\n⚠️  NO PROFILES FOUND")
                        print(f"   This means the player hasn't played Hypixel Skyblock")
                        print(f"   (This is not an API error - API responded correctly)")
                        return []

                    print(f"\n📋 RESULTS:")
                    print(f"  Found {len(profiles)} Skyblock profile(s)")

                    for i, profile in enumerate(profiles):
                        print(f"\n  Profile {i+1}:")
                        print(f"    - Profile ID: {profile.get('profile_id', 'N/A')}")
                        print(f"    - Cute Name: {profile.get('cute_name', 'N/A')}")
                        print(f"    - Members: {len(profile.get('members', {}))}")

                        # Check if UUID is in members
                        members = profile.get('members', {})
                        if clean_uuid in members:
                            print(f"    - ✅ Player found in this profile")
                            member_data = members[clean_uuid]
                            last_save = member_data.get('last_save', 0)
                            print(f"    - Last save timestamp: {last_save}")

                    return profiles
                else:
                    cause = data.get('cause', 'Unknown error')
                    print(f"\n❌ API returned success=false")
                    print(f"   Cause: {cause}")
                    return None
            else:
                print(f"\n❌ TEST FAILED - Expected 200, got {status}")
                return None

    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP ERROR: {e.code} - {e.reason}")

        if e.code == 403:
            print(f"   API key is invalid or doesn't have permissions")
        elif e.code == 429:
            print(f"   Rate limited - too many requests")

        # Try to read error response
        try:
            error_data = json.loads(e.read().decode())
            print(f"   Error response: {json.dumps(error_data, indent=2)}")
        except:
            pass

        return None
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_uuid_with_dashes(uuid_no_dashes):
    """Test if API accepts UUID with dashes."""
    print("\n" + "="*70)
    print("TEST 3: UUID Format Testing (With vs Without Dashes)")
    print("="*70)

    if not uuid_no_dashes:
        print("❌ SKIPPED - No UUID provided")
        return

    api_key = config.HYPIXEL_API_KEY
    if not api_key:
        print("❌ SKIPPED - HYPIXEL_API_KEY not configured")
        return

    # Create dashed version
    uuid_with_dashes = f"{uuid_no_dashes[:8]}-{uuid_no_dashes[8:12]}-{uuid_no_dashes[12:16]}-{uuid_no_dashes[16:20]}-{uuid_no_dashes[20:]}"

    print(f"UUID (no dashes): {uuid_no_dashes}")
    print(f"UUID (with dashes): {uuid_with_dashes}")

    # Test WITH dashes
    print(f"\n[Testing WITH dashes]")
    params = urllib.parse.urlencode({'key': api_key, 'uuid': uuid_with_dashes})
    url = f"https://api.hypixel.net/v2/skyblock/profiles?{params}"

    try:
        with urllib.request.urlopen(url) as response:
            status = response.status
            data = json.loads(response.read().decode())
            success = data.get('success', False)
            print(f"  Status: {status}")
            print(f"  Success: {success}")
            if status == 200 and success:
                print(f"  ✅ Dashed UUID WORKS")
            else:
                print(f"  ❌ Dashed UUID FAILED")
    except Exception as e:
        print(f"  ❌ Dashed UUID ERROR: {e}")

    # Test WITHOUT dashes
    print(f"\n[Testing WITHOUT dashes]")
    params = urllib.parse.urlencode({'key': api_key, 'uuid': uuid_no_dashes})
    url = f"https://api.hypixel.net/v2/skyblock/profiles?{params}"

    try:
        with urllib.request.urlopen(url) as response:
            status = response.status
            data = json.loads(response.read().decode())
            success = data.get('success', False)
            print(f"  Status: {status}")
            print(f"  Success: {success}")
            if status == 200 and success:
                print(f"  ✅ Non-dashed UUID WORKS")
            else:
                print(f"  ❌ Non-dashed UUID FAILED")
    except Exception as e:
        print(f"  ❌ Non-dashed UUID ERROR: {e}")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("HYPIXEL API ENDPOINT VALIDATION TESTS")
    print("="*70)
    print(f"\nTest Username: NathanFant")
    print(f"Test UUID: 47fb7b99858042c3a7b4795af44ea41d")
    print(f"API Key Configured: {'Yes' if config.HYPIXEL_API_KEY else 'No'}")

    # Test 1: Mojang API
    uuid = test_mojang_api("NathanFant")

    # Test 2: Hypixel Skyblock Profiles (also test with known UUID)
    if uuid:
        test_hypixel_skyblock_profiles(uuid)
        test_uuid_with_dashes(uuid)
    else:
        # Fallback to known UUID if Mojang API fails
        print("\n⚠️  Mojang API failed, using known UUID for remaining tests")
        uuid = "47fb7b99858042c3a7b4795af44ea41d"
        test_hypixel_skyblock_profiles(uuid)
        test_uuid_with_dashes(uuid)

    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
    print("\nSUMMARY:")
    print("- If all tests show ✅ with status 200, the API calls are working correctly")
    print("- If Skyblock profiles test shows 'No profiles found', it means the player")
    print("  hasn't played Hypixel Skyblock (this is expected behavior, not an error)")
    print("- If you see 403 errors, check your HYPIXEL_API_KEY is valid")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
