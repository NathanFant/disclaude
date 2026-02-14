"""User profile storage for linking Discord users to Minecraft usernames."""
from collections import defaultdict
from typing import Optional


class UserProfiles:
    """Simple in-memory storage for user profiles."""

    def __init__(self):
        # discord_user_id -> minecraft_username
        self.profiles = {}
        # discord_user_id -> minecraft_uuid
        self.uuids = {}

    def link_user(self, discord_id: int, minecraft_username: str, minecraft_uuid: str):
        """Link a Discord user to their Minecraft account."""
        self.profiles[discord_id] = minecraft_username
        self.uuids[discord_id] = minecraft_uuid

    def get_username(self, discord_id: int) -> Optional[str]:
        """Get linked Minecraft username for a Discord user."""
        return self.profiles.get(discord_id)

    def get_uuid(self, discord_id: int) -> Optional[str]:
        """Get linked Minecraft UUID for a Discord user."""
        return self.uuids.get(discord_id)

    def is_linked(self, discord_id: int) -> bool:
        """Check if a Discord user has linked their Minecraft account."""
        return discord_id in self.profiles

    def unlink_user(self, discord_id: int):
        """Unlink a Discord user from their Minecraft account."""
        self.profiles.pop(discord_id, None)
        self.uuids.pop(discord_id, None)


# Global user profiles instance
user_profiles = UserProfiles()
