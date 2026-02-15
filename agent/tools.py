"""Tool executor for agent capabilities.

Executes tools that Claude can call to perform actions.
"""
from typing import Dict, Any
import json
from datetime import datetime

from skyblock.client import hypixel_client
from skyblock.analyzer import skyblock_analyzer
from skyblock.profiles import user_profiles
from core.scheduler import smart_scheduler


class ToolExecutor:
    """Executes tools that Claude can call."""

    @staticmethod
    async def execute(tool_name: str, tool_input: Dict[str, Any]) -> str:
        """Execute a tool and return the result as JSON string.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            JSON string with tool execution results
        """
        print(f"[TOOL] Executing: {tool_name}")
        print(f"[TOOL] Input: {tool_input}")

        try:
            if tool_name == "get_skyblock_stats":
                result = await ToolExecutor.get_skyblock_stats(tool_input)

            elif tool_name == "link_minecraft_account":
                result = await ToolExecutor.link_minecraft_account(tool_input)

            elif tool_name == "create_reminder":
                result = await ToolExecutor.create_reminder(tool_input)

            elif tool_name == "check_user_link_status":
                result = await ToolExecutor.check_user_link_status(tool_input)

            else:
                result = json.dumps({
                    "error": f"Unknown tool: {tool_name}",
                    "success": False
                })

            print(f"[TOOL] Result: {result}")
            return result

        except Exception as e:
            error_result = json.dumps({
                "error": str(e),
                "tool": tool_name,
                "success": False
            })
            print(f"[TOOL] Error: {error_result}")
            return error_result

    @staticmethod
    async def get_skyblock_stats(input_data: Dict[str, Any]) -> str:
        """Get Skyblock stats for a Discord user.

        Args:
            input_data: {"discord_id": "123456789"}

        Returns:
            JSON with stats or error
        """
        try:
            discord_id = int(input_data['discord_id'])
        except (KeyError, ValueError) as e:
            return json.dumps({
                "error": "Invalid discord_id parameter",
                "success": False
            })

        # Check if user is linked
        if not user_profiles.is_linked(discord_id):
            return json.dumps({
                "error": "User not linked",
                "message": "User needs to link their Minecraft account first",
                "success": False,
                "linked": False
            })

        # Get user's UUID and username
        uuid = user_profiles.get_uuid(discord_id)
        username = user_profiles.get_username(discord_id)

        # Fetch Skyblock profile
        profile = await hypixel_client.get_active_profile(uuid)
        if not profile:
            return json.dumps({
                "error": "No Skyblock profile found",
                "message": "User has not played Hypixel Skyblock",
                "success": False,
                "username": username
            })

        # Get player data
        player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)
        if not player_data:
            return json.dumps({
                "error": "Could not load player data from profile",
                "success": False
            })

        # Analyze skills
        skill_analysis = skyblock_analyzer.analyze_skills(player_data)
        slayer_analysis = skyblock_analyzer.analyze_slayers(player_data)

        # Build result
        skills_dict = {
            name: {
                "level": data['level'],
                "progress": data.get('progress', 0)
            }
            for name, data in skill_analysis.get('skills', {}).items()
        }

        result = {
            "success": True,
            "username": username,
            "uuid": uuid,
            "profile_name": profile.get('cute_name'),
            "skill_average": round(skill_analysis.get('skill_average', 0), 1),
            "skills": skills_dict,
            "total_slayer_xp": slayer_analysis.get('total_slayer_xp', 0),
            "purse": player_data.get('currencies', {}).get('coin_purse', 0),
            "bank": profile.get('banking', {}).get('balance', 0)
        }

        return json.dumps(result)

    @staticmethod
    async def link_minecraft_account(input_data: Dict[str, Any]) -> str:
        """Link a Discord user to their Minecraft account.

        Args:
            input_data: {
                "discord_id": "123456789",
                "minecraft_username": "PlayerName"
            }

        Returns:
            JSON with link status
        """
        try:
            discord_id = int(input_data['discord_id'])
            username = input_data['minecraft_username']
        except (KeyError, ValueError):
            return json.dumps({
                "error": "Invalid parameters",
                "success": False
            })

        # Get UUID from Mojang API
        uuid = await hypixel_client.get_uuid_from_username(username)
        if not uuid:
            return json.dumps({
                "error": "Minecraft user not found",
                "username": username,
                "success": False,
                "message": f"Could not find Minecraft player '{username}'"
            })

        # Store the link
        user_profiles.link_user(discord_id, username, uuid)

        result = {
            "success": True,
            "linked": True,
            "username": username,
            "uuid": uuid
        }

        # Try to fetch Skyblock profile
        profile = await hypixel_client.get_active_profile(uuid)
        if profile:
            result["skyblock_profile_found"] = True
            result["profile_name"] = profile.get('cute_name')

            # Get skill average
            player_data = await hypixel_client.get_player_data_from_profile(profile, uuid)
            if player_data:
                skill_analysis = skyblock_analyzer.analyze_skills(player_data)
                result["skill_average"] = round(skill_analysis.get('skill_average', 0), 1)
        else:
            result["skyblock_profile_found"] = False
            result["message"] = "No Skyblock profile found (player may not have played Skyblock)"

        return json.dumps(result)

    @staticmethod
    async def create_reminder(input_data: Dict[str, Any]) -> str:
        """Create a reminder for a user.

        Args:
            input_data: {
                "user_id": "123456789",
                "channel_id": "987654321",
                "message": "Reminder text",
                "time": "2024-03-15T14:30:00Z"
            }

        Returns:
            JSON with reminder status
        """
        try:
            user_id = int(input_data['user_id'])
            channel_id = int(input_data['channel_id'])
            message = input_data['message']
            time_str = input_data['time']
        except (KeyError, ValueError):
            return json.dumps({
                "error": "Invalid parameters",
                "success": False
            })

        # Parse ISO 8601 time
        try:
            # Handle both with and without timezone
            if time_str.endswith('Z'):
                target_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            else:
                target_time = datetime.fromisoformat(time_str)
        except ValueError as e:
            return json.dumps({
                "error": f"Invalid time format: {e}",
                "success": False,
                "message": "Time must be in ISO 8601 format (e.g., '2024-03-15T14:30:00Z')"
            })

        # Check if time is in the future
        if target_time <= datetime.now(target_time.tzinfo):
            return json.dumps({
                "error": "Time must be in the future",
                "success": False,
                "provided_time": time_str
            })

        # Schedule reminder (send_function will be set in bot.py)
        # For now, just return success - actual scheduling happens in bot
        result = {
            "success": True,
            "scheduled": True,
            "user_id": user_id,
            "channel_id": channel_id,
            "message": message,
            "scheduled_for": target_time.isoformat(),
            "note": "Reminder creation requested - bot will handle scheduling"
        }

        return json.dumps(result)

    @staticmethod
    async def check_user_link_status(input_data: Dict[str, Any]) -> str:
        """Check if a user has linked their Minecraft account.

        Args:
            input_data: {"discord_id": "123456789"}

        Returns:
            JSON with link status
        """
        try:
            discord_id = int(input_data['discord_id'])
        except (KeyError, ValueError):
            return json.dumps({
                "error": "Invalid discord_id",
                "success": False
            })

        is_linked = user_profiles.is_linked(discord_id)

        if is_linked:
            username = user_profiles.get_username(discord_id)
            uuid = user_profiles.get_uuid(discord_id)

            return json.dumps({
                "success": True,
                "linked": True,
                "username": username,
                "uuid": uuid
            })
        else:
            return json.dumps({
                "success": True,
                "linked": False,
                "message": "User has not linked their Minecraft account"
            })


# Global tool executor instance
tool_executor = ToolExecutor()
