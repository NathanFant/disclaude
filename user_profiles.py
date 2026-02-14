"""User profile storage for linking Discord users to Minecraft usernames."""
from collections import defaultdict
from typing import Optional
import json
import os


class UserProfiles:
    """Persistent storage for user profiles."""

    def __init__(self, storage_file: str = "user_profiles.json"):
        self.storage_file = storage_file
        # discord_user_id -> minecraft_username
        self.profiles = {}
        # discord_user_id -> minecraft_uuid
        self.uuids = {}
        self.load()

    def load(self):
        """Load profiles from disk."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                    # Convert string keys back to ints
                    self.profiles = {int(k): v for k, v in data.get('profiles', {}).items()}
                    self.uuids = {int(k): v for k, v in data.get('uuids', {}).items()}
                    print(f"[USER_PROFILES] Loaded {len(self.profiles)} linked accounts")
            except Exception as e:
                print(f"[USER_PROFILES] Error loading profiles: {e}")
                self.profiles = {}
                self.uuids = {}
        else:
            print("[USER_PROFILES] No existing profiles file, starting fresh")

    def save(self):
        """Save profiles to disk."""
        try:
            data = {
                'profiles': {str(k): v for k, v in self.profiles.items()},
                'uuids': {str(k): v for k, v in self.uuids.items()}
            }
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[USER_PROFILES] Saved {len(self.profiles)} profiles")
        except Exception as e:
            print(f"[USER_PROFILES] Error saving profiles: {e}")

    def link_user(self, discord_id: int, minecraft_username: str, minecraft_uuid: str):
        """Link a Discord user to their Minecraft account."""
        self.profiles[discord_id] = minecraft_username
        self.uuids[discord_id] = minecraft_uuid
        self.save()  # Persist immediately
        print(f"[USER_PROFILES] Linked {discord_id} -> {minecraft_username} ({minecraft_uuid})")

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
        self.save()  # Persist immediately


# Global user profiles instance
user_profiles = UserProfiles()
