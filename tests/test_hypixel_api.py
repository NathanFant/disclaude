"""Tests for Hypixel API endpoints to validate correct API usage."""
import pytest
import aiohttp
import asyncio
import os
from hypixel_client import hypixel_client
import config


class TestHypixelAPIEndpoints:
    """Test actual Hypixel API endpoints."""

    # Test data
    TEST_USERNAME = "NathanFant"
    TEST_UUID = None  # Will be fetched from Mojang API

    @pytest.mark.asyncio
    async def test_mojang_api_get_uuid_from_username(self):
        """Test Mojang API: Get UUID from username."""
        print(f"\n[TEST] Testing Mojang API with username: {self.TEST_USERNAME}")

        async with aiohttp.ClientSession() as session:
            url = f"https://api.mojang.com/users/profiles/minecraft/{self.TEST_USERNAME}"
            print(f"[TEST] URL: {url}")

            async with session.get(url) as response:
                print(f"[TEST] Response status: {response.status}")
                assert response.status == 200, f"Expected 200, got {response.status}"

                data = await response.json()
                print(f"[TEST] Response data: {data}")

                # Validate response structure
                assert 'id' in data, "Response missing 'id' field"
                assert 'name' in data, "Response missing 'name' field"

                # Store UUID for next tests
                TestHypixelAPIEndpoints.TEST_UUID = data['id']
                print(f"[TEST] ✅ Got UUID: {self.TEST_UUID}")
                print(f"[TEST] ✅ Username: {data['name']}")

    @pytest.mark.asyncio
    async def test_hypixel_api_key_configured(self):
        """Test that Hypixel API key is configured."""
        print(f"\n[TEST] Checking Hypixel API key configuration")

        api_key = config.HYPIXEL_API_KEY
        assert api_key is not None, "HYPIXEL_API_KEY not set in environment"
        assert len(api_key) > 0, "HYPIXEL_API_KEY is empty"

        print(f"[TEST] ✅ API key configured: {api_key[:8]}...")

    @pytest.mark.asyncio
    async def test_hypixel_skyblock_profiles_with_uuid(self):
        """Test Hypixel API: Get Skyblock profiles using UUID."""
        # First get the UUID
        if not self.TEST_UUID:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.mojang.com/users/profiles/minecraft/{self.TEST_USERNAME}"
                async with session.get(url) as response:
                    data = await response.json()
                    TestHypixelAPIEndpoints.TEST_UUID = data['id']

        print(f"\n[TEST] Testing Hypixel Skyblock API with UUID: {self.TEST_UUID}")

        api_key = config.HYPIXEL_API_KEY
        assert api_key, "API key not configured"

        # Remove dashes from UUID (Hypixel requirement)
        clean_uuid = self.TEST_UUID.replace('-', '')

        async with aiohttp.ClientSession() as session:
            url = f"https://api.hypixel.net/v2/skyblock/profiles"
            params = {
                "key": api_key,
                "uuid": clean_uuid
            }
            print(f"[TEST] URL: {url}")
            print(f"[TEST] Params: uuid={clean_uuid}, key={api_key[:8]}...")

            async with session.get(url, params=params) as response:
                print(f"[TEST] Response status: {response.status}")

                if response.status == 403:
                    text = await response.text()
                    print(f"[TEST] ❌ 403 Forbidden - API key invalid or missing")
                    print(f"[TEST] Response: {text}")
                    pytest.fail("API key is invalid or forbidden")

                if response.status == 429:
                    print(f"[TEST] ❌ 429 Rate Limited")
                    pytest.fail("Rate limited")

                assert response.status == 200, f"Expected 200, got {response.status}. Response: {await response.text()}"

                data = await response.json()
                print(f"[TEST] Response keys: {data.keys()}")

                # Validate response structure
                assert 'success' in data, "Response missing 'success' field"
                assert data['success'] is True, f"API returned success=false: {data.get('cause', 'Unknown')}"

                print(f"[TEST] ✅ API success: {data['success']}")

                # Check profiles
                profiles = data.get('profiles')
                if profiles is None:
                    print(f"[TEST] ⚠️  No Skyblock profiles found for {self.TEST_USERNAME}")
                    print(f"[TEST] This means the player hasn't played Hypixel Skyblock")
                else:
                    print(f"[TEST] ✅ Found {len(profiles)} Skyblock profile(s)")

                    for i, profile in enumerate(profiles):
                        print(f"\n[TEST] Profile {i + 1}:")
                        print(f"[TEST]   - Profile ID: {profile.get('profile_id')}")
                        print(f"[TEST]   - Name: {profile.get('cute_name')}")
                        print(f"[TEST]   - Members: {len(profile.get('members', {}))}")

                        # Check if our UUID is in the members
                        members = profile.get('members', {})
                        if clean_uuid in members:
                            member_data = members[clean_uuid]
                            last_save = member_data.get('last_save', 0)
                            print(f"[TEST]   - ✅ Found player in this profile")
                            print(f"[TEST]   - Last save: {last_save}")

    @pytest.mark.asyncio
    async def test_hypixel_client_wrapper_get_uuid(self):
        """Test our HypixelClient wrapper: get_uuid_from_username."""
        print(f"\n[TEST] Testing HypixelClient.get_uuid_from_username()")

        uuid = await hypixel_client.get_uuid_from_username(self.TEST_USERNAME)

        assert uuid is not None, f"Failed to get UUID for {self.TEST_USERNAME}"
        print(f"[TEST] ✅ HypixelClient.get_uuid_from_username() returned: {uuid}")

        # Store for next test
        if not self.TEST_UUID:
            TestHypixelAPIEndpoints.TEST_UUID = uuid

    @pytest.mark.asyncio
    async def test_hypixel_client_wrapper_get_profiles(self):
        """Test our HypixelClient wrapper: get_skyblock_profiles."""
        print(f"\n[TEST] Testing HypixelClient.get_skyblock_profiles()")

        # Ensure we have UUID
        if not self.TEST_UUID:
            uuid = await hypixel_client.get_uuid_from_username(self.TEST_USERNAME)
            TestHypixelAPIEndpoints.TEST_UUID = uuid
        else:
            uuid = self.TEST_UUID

        assert uuid, "No UUID available for testing"

        profiles = await hypixel_client.get_skyblock_profiles(uuid)

        # profiles can be None (error), [] (no profiles), or list of profiles
        assert profiles is not None, "get_skyblock_profiles() returned None (API error)"

        if len(profiles) == 0:
            print(f"[TEST] ⚠️  No Skyblock profiles (player hasn't played Skyblock)")
        else:
            print(f"[TEST] ✅ HypixelClient.get_skyblock_profiles() returned {len(profiles)} profile(s)")

    @pytest.mark.asyncio
    async def test_hypixel_client_wrapper_get_active_profile(self):
        """Test our HypixelClient wrapper: get_active_profile."""
        print(f"\n[TEST] Testing HypixelClient.get_active_profile()")

        # Ensure we have UUID
        if not self.TEST_UUID:
            uuid = await hypixel_client.get_uuid_from_username(self.TEST_USERNAME)
            TestHypixelAPIEndpoints.TEST_UUID = uuid
        else:
            uuid = self.TEST_UUID

        assert uuid, "No UUID available for testing"

        profile = await hypixel_client.get_active_profile(uuid)

        if profile is None:
            print(f"[TEST] ⚠️  No active profile found (player may not have Skyblock profiles)")
        else:
            print(f"[TEST] ✅ HypixelClient.get_active_profile() returned profile: {profile.get('cute_name')}")

            # Test get_player_data_from_profile
            player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)

            if player_data:
                print(f"[TEST] ✅ Player data extracted from profile")
                print(f"[TEST]   - Data keys: {list(player_data.keys())[:10]}...")  # First 10 keys
            else:
                print(f"[TEST] ❌ Failed to extract player data from profile")

    @pytest.mark.asyncio
    async def test_direct_api_call_with_dashed_uuid(self):
        """Test if Hypixel API accepts UUID with dashes."""
        print(f"\n[TEST] Testing Hypixel API with dashed UUID")

        # Get UUID with dashes from Mojang
        async with aiohttp.ClientSession() as session:
            url = f"https://api.mojang.com/users/profiles/minecraft/{self.TEST_USERNAME}"
            async with session.get(url) as response:
                data = await response.json()
                uuid_no_dashes = data['id']

        # Add dashes to UUID (standard UUID format)
        uuid_with_dashes = f"{uuid_no_dashes[:8]}-{uuid_no_dashes[8:12]}-{uuid_no_dashes[12:16]}-{uuid_no_dashes[16:20]}-{uuid_no_dashes[20:]}"

        print(f"[TEST] UUID without dashes: {uuid_no_dashes}")
        print(f"[TEST] UUID with dashes: {uuid_with_dashes}")

        api_key = config.HYPIXEL_API_KEY

        # Test with dashes
        async with aiohttp.ClientSession() as session:
            url = f"https://api.hypixel.net/v2/skyblock/profiles"
            params = {
                "key": api_key,
                "uuid": uuid_with_dashes
            }
            print(f"[TEST] Testing with dashed UUID...")

            async with session.get(url, params=params) as response:
                print(f"[TEST] Status with dashed UUID: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print(f"[TEST] ✅ Dashed UUID accepted, success: {data.get('success')}")
                else:
                    print(f"[TEST] ⚠️  Dashed UUID failed with status {response.status}")

        # Test without dashes
        async with aiohttp.ClientSession() as session:
            params = {
                "key": api_key,
                "uuid": uuid_no_dashes
            }
            print(f"[TEST] Testing with non-dashed UUID...")

            async with session.get(url, params=params) as response:
                print(f"[TEST] Status with non-dashed UUID: {response.status}")

                if response.status == 200:
                    data = await response.json()
                    print(f"[TEST] ✅ Non-dashed UUID accepted, success: {data.get('success')}")
                else:
                    print(f"[TEST] ⚠️  Non-dashed UUID failed with status {response.status}")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
