"""Hypixel API client for Skyblock data."""
import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import config


class HypixelClient:
    """Client for interacting with Hypixel API."""

    BASE_URL = "https://api.hypixel.net/v2"
    MOJANG_API = "https://api.mojang.com/users/profiles/minecraft"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.HYPIXEL_API_KEY
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_uuid_from_username(self, username: str) -> Optional[str]:
        """Get Minecraft UUID from username using Mojang API."""
        await self._ensure_session()
        try:
            async with self.session.get(f"{self.MOJANG_API}/{username}") as response:
                print(f"[HYPIXEL] Mojang API status for {username}: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    uuid = data.get('id')
                    print(f"[HYPIXEL] Got UUID for {username}: {uuid}")
                    return uuid
                elif response.status == 204:
                    print(f"[HYPIXEL] Username not found: {username}")
                    return None
                else:
                    print(f"[HYPIXEL] Mojang API error: {response.status}")
                    return None
        except Exception as e:
            print(f"[HYPIXEL] Error fetching UUID for {username}: {e}")
            return None

    async def get_player(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get player data from Hypixel API."""
        await self._ensure_session()
        try:
            params = {"key": self.api_key, "uuid": uuid}
            async with self.session.get(f"{self.BASE_URL}/player", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('player')
                return None
        except Exception as e:
            print(f"Error fetching player data: {e}")
            return None

    async def get_skyblock_profiles(self, uuid: str) -> Optional[list]:
        """Get Skyblock profiles for a player."""
        await self._ensure_session()
        try:
            # Ensure UUID has no dashes (Hypixel API requirement)
            clean_uuid = uuid.replace('-', '')

            params = {"key": self.api_key, "uuid": clean_uuid}
            print(f"[HYPIXEL] Fetching Skyblock profiles for UUID: {clean_uuid}")

            async with self.session.get(f"{self.BASE_URL}/skyblock/profiles", params=params) as response:
                print(f"[HYPIXEL] Skyblock API status: {response.status}")

                if response.status == 200:
                    data = await response.json()

                    # Check for API errors
                    if not data.get('success', False):
                        cause = data.get('cause', 'Unknown error')
                        print(f"[HYPIXEL] API returned success=false: {cause}")
                        return None

                    profiles = data.get('profiles')
                    if profiles is None:
                        print(f"[HYPIXEL] No Skyblock profiles found for {clean_uuid}")
                        return []

                    print(f"[HYPIXEL] Found {len(profiles)} Skyblock profile(s)")
                    return profiles
                elif response.status == 403:
                    print(f"[HYPIXEL] API key is invalid or missing!")
                    return None
                elif response.status == 429:
                    print(f"[HYPIXEL] Rate limited!")
                    return None
                else:
                    print(f"[HYPIXEL] HTTP error {response.status}")
                    text = await response.text()
                    print(f"[HYPIXEL] Response: {text}")
                    return None
        except Exception as e:
            print(f"[HYPIXEL] Error fetching Skyblock profiles: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def get_active_profile(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get the player's currently selected Skyblock profile."""
        # Clean UUID for consistency
        clean_uuid = uuid.replace('-', '')

        profiles = await self.get_skyblock_profiles(clean_uuid)
        if not profiles:
            print(f"[HYPIXEL] No profiles returned for {clean_uuid}")
            return None

        # Method 1: Check for 'selected' field at profile level
        for profile in profiles:
            if profile.get('selected'):
                print(f"[HYPIXEL] Found selected profile: {profile.get('cute_name', 'Unknown')}")
                return profile

        # Method 2: Find profile with most recent activity (from objectives timestamps)
        active_profile = None
        latest_timestamp = 0

        for profile in profiles:
            if not profile or 'members' not in profile:
                print(f"[HYPIXEL] Skipping invalid profile (no members)")
                continue

            # Get member data
            member_data = profile['members'].get(clean_uuid) or profile['members'].get(uuid)
            if not member_data:
                continue

            # Look for the most recent timestamp in objectives
            objectives = member_data.get('objectives', {})
            if objectives:
                for _, obj_data in objectives.items():
                    if isinstance(obj_data, dict) and 'completed_at' in obj_data:
                        timestamp = obj_data['completed_at']
                        if timestamp > latest_timestamp:
                            latest_timestamp = timestamp
                            active_profile = profile

        if active_profile:
            print(f"[HYPIXEL] Found active profile by timestamp: {active_profile.get('cute_name', 'Unknown')}")
            return active_profile

        # Method 3: Fallback to first profile with player data
        for profile in profiles:
            if profile.get('members', {}).get(clean_uuid) or profile.get('members', {}).get(uuid):
                print(f"[HYPIXEL] Using first available profile: {profile.get('cute_name', 'Unknown')}")
                return profile

        print(f"[HYPIXEL] No active profile found for {clean_uuid}")
        return None

    async def get_player_data_from_profile(self, profile: Dict[str, Any], uuid: str) -> Optional[Dict[str, Any]]:
        """Extract player-specific data from a profile."""
        if not profile or 'members' not in profile:
            return None

        # Try both with and without dashes
        clean_uuid = uuid.replace('-', '')
        return profile['members'].get(clean_uuid) or profile['members'].get(uuid)


# Global client instance
hypixel_client = HypixelClient()
