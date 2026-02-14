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
                if response.status == 200:
                    data = await response.json()
                    return data.get('id')
                return None
        except Exception as e:
            print(f"Error fetching UUID for {username}: {e}")
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
            params = {"key": self.api_key, "uuid": uuid}
            async with self.session.get(f"{self.BASE_URL}/skyblock/profiles", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('profiles', [])
                return None
        except Exception as e:
            print(f"Error fetching Skyblock profiles: {e}")
            return None

    async def get_active_profile(self, uuid: str) -> Optional[Dict[str, Any]]:
        """Get the player's currently selected Skyblock profile."""
        profiles = await self.get_skyblock_profiles(uuid)
        if not profiles:
            return None

        # Find the profile with the most recent save
        active_profile = None
        latest_save = 0

        for profile in profiles:
            if not profile or 'members' not in profile:
                continue

            member_data = profile['members'].get(uuid)
            if member_data:
                last_save = member_data.get('last_save', 0)
                if last_save > latest_save:
                    latest_save = last_save
                    active_profile = profile

        return active_profile

    async def get_player_data_from_profile(self, profile: Dict[str, Any], uuid: str) -> Optional[Dict[str, Any]]:
        """Extract player-specific data from a profile."""
        if not profile or 'members' not in profile:
            return None

        return profile['members'].get(uuid)


# Global client instance
hypixel_client = HypixelClient()
