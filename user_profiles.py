"""User profile storage for linking Discord users to Minecraft usernames."""
from typing import Optional
from database import UserProfile, get_db, init_db


class UserProfiles:
    """Persistent storage for user profiles using database."""

    def __init__(self):
        # Initialize database tables
        init_db()
        print("[USER_PROFILES] Database-backed storage initialized")

    def link_user(self, discord_id: int, minecraft_username: str, minecraft_uuid: str):
        """Link a Discord user to their Minecraft account."""
        db = get_db()
        try:
            # Check if user already exists
            existing = db.query(UserProfile).filter(UserProfile.discord_id == discord_id).first()

            if existing:
                # Update existing
                existing.minecraft_username = minecraft_username
                existing.minecraft_uuid = minecraft_uuid
                print(f"[USER_PROFILES] Updated {discord_id} -> {minecraft_username}")
            else:
                # Create new
                profile = UserProfile(
                    discord_id=discord_id,
                    minecraft_username=minecraft_username,
                    minecraft_uuid=minecraft_uuid
                )
                db.add(profile)
                print(f"[USER_PROFILES] Created {discord_id} -> {minecraft_username}")

            db.commit()
        except Exception as e:
            print(f"[USER_PROFILES] Error linking user: {e}")
            db.rollback()
        finally:
            db.close()

    def get_username(self, discord_id: int) -> Optional[str]:
        """Get linked Minecraft username for a Discord user."""
        db = get_db()
        try:
            profile = db.query(UserProfile).filter(UserProfile.discord_id == discord_id).first()
            return profile.minecraft_username if profile else None
        finally:
            db.close()

    def get_uuid(self, discord_id: int) -> Optional[str]:
        """Get linked Minecraft UUID for a Discord user."""
        db = get_db()
        try:
            profile = db.query(UserProfile).filter(UserProfile.discord_id == discord_id).first()
            return profile.minecraft_uuid if profile else None
        finally:
            db.close()

    def is_linked(self, discord_id: int) -> bool:
        """Check if a Discord user has linked their Minecraft account."""
        db = get_db()
        try:
            profile = db.query(UserProfile).filter(UserProfile.discord_id == discord_id).first()
            return profile is not None
        finally:
            db.close()

    def unlink_user(self, discord_id: int):
        """Unlink a Discord user from their Minecraft account."""
        db = get_db()
        try:
            profile = db.query(UserProfile).filter(UserProfile.discord_id == discord_id).first()
            if profile:
                db.delete(profile)
                db.commit()
                print(f"[USER_PROFILES] Unlinked {discord_id}")
        except Exception as e:
            print(f"[USER_PROFILES] Error unlinking user: {e}")
            db.rollback()
        finally:
            db.close()


# Global user profiles instance
user_profiles = UserProfiles()
