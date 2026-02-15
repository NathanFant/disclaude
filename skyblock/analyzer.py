"""Skyblock data analyzer and progression advisor."""
from typing import Dict, Any, List, Tuple, Optional
import math
import base64
import gzip
import io
try:
    import nbtlib
    NBT_AVAILABLE = True
except ImportError:
    NBT_AVAILABLE = False


class SkyblockAnalyzer:
    """Analyzes Skyblock data and provides progression advice."""

    # Skill level requirements (cumulative XP)
    SKILL_XP_REQUIREMENTS = [
        0, 50, 175, 375, 675, 1175, 1925, 2925, 4425, 6425,
        9925, 14925, 22425, 32425, 47425, 67425, 97425, 147425,
        222425, 322425, 522425, 822425, 1222425, 1722425, 2322425,
        3022425, 3822425, 4722425, 5722425, 6822425, 8022425, 9322425,
        10722425, 12222425, 13822425, 15522425, 17322425, 19222425,
        21222425, 23322425, 25522425, 27822425, 30222425, 32722425,
        35322425, 38072425, 40972425, 44072425, 47472425, 51172425,
        55172425, 59472425, 64072425, 68972425, 74172425, 79672425,
        85472425, 91572425, 97972425, 104672425, 111672425
    ]

    def __init__(self):
        pass

    def _decode_inventory_data(self, data: str) -> Optional[Any]:
        """Decode base64 + gzip + NBT inventory data."""
        if not NBT_AVAILABLE or not data:
            return None

        try:
            # Decode base64
            decoded = base64.b64decode(data)
            # Decompress gzip
            decompressed = gzip.decompress(decoded)
            # Parse NBT
            nbt_data = nbtlib.File.parse(io.BytesIO(decompressed))
            return nbt_data
        except Exception as e:
            print(f"[ANALYZER] Error decoding inventory: {e}")
            return None

    def _parse_item_name(self, item_tag: Any) -> str:
        """Extract display name from item NBT."""
        try:
            # Try to get display name from tag
            if hasattr(item_tag, 'get'):
                tag = item_tag.get('tag', {})
                display = tag.get('display', {})
                name = display.get('Name', '')
                if name:
                    # Clean up Minecraft formatting codes
                    import re
                    name = re.sub(r'§[0-9a-fk-or]', '', str(name))
                    return name

                # Fall back to item ID
                item_id = item_tag.get('id', 'Unknown')
                return str(item_id).replace('minecraft:', '').replace('_', ' ').title()
            return 'Unknown Item'
        except Exception:
            return 'Unknown Item'

    def analyze_equipment(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze player's armor and equipment."""
        if not NBT_AVAILABLE:
            return {'error': 'NBT parsing not available'}

        equipment = {
            'armor': {'helmet': None, 'chestplate': None, 'leggings': None, 'boots': None},
            'has_data': False
        }

        # Try to get armor inventory
        inv_armor_data = player_data.get('inv_armor', {}).get('data')
        if inv_armor_data:
            armor_nbt = self._decode_inventory_data(inv_armor_data)
            if armor_nbt:
                try:
                    items = armor_nbt.get('i', [])
                    # Armor slots: 0=boots, 1=leggings, 2=chestplate, 3=helmet
                    slot_names = ['boots', 'leggings', 'chestplate', 'helmet']
                    for idx, slot_name in enumerate(slot_names):
                        if idx < len(items) and items[idx]:
                            item_name = self._parse_item_name(items[idx])
                            if item_name and item_name != 'Unknown Item':
                                equipment['armor'][slot_name] = item_name
                                equipment['has_data'] = True
                except Exception as e:
                    print(f"[ANALYZER] Error parsing armor: {e}")

        return equipment

    def calculate_skill_level(self, xp: float, skill_name: str = "default") -> Tuple[int, float]:
        """Calculate skill level and progress to next level from XP."""
        # Runecrafting and social have different caps
        max_level = 25 if skill_name.lower() in ['runecrafting', 'social'] else 60

        level = 0
        for i, required_xp in enumerate(self.SKILL_XP_REQUIREMENTS):
            if i >= max_level:
                break
            if xp >= required_xp:
                level = i
            else:
                break

        # Calculate progress to next level
        if level < max_level:
            current_xp = self.SKILL_XP_REQUIREMENTS[level]
            next_xp = self.SKILL_XP_REQUIREMENTS[level + 1]
            progress = ((xp - current_xp) / (next_xp - current_xp)) * 100
        else:
            progress = 100.0

        return level, progress

    def analyze_skills(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze player skills and calculate levels."""
        if not player_data:
            return {}

        # Skills are in player_data['player_data']['experience'] with SKILL_<NAME> format
        experience_data = player_data.get('player_data', {}).get('experience', {})

        skills = [
            'farming', 'mining', 'combat', 'foraging', 'fishing',
            'enchanting', 'alchemy', 'taming', 'carpentry', 'runecrafting', 'social'
        ]

        skill_data = {}
        total_skill_level = 0
        skill_count = 0

        for skill in skills:
            # Try new format first (SKILL_UPPERCASE), then old format for backwards compatibility
            xp_key_new = f'SKILL_{skill.upper()}'
            xp_key_old = f'experience_skill_{skill}'

            xp = experience_data.get(xp_key_new, player_data.get(xp_key_old, 0))

            level, progress = self.calculate_skill_level(xp, skill)

            skill_data[skill] = {
                'level': level,
                'xp': xp,
                'progress': progress
            }

            # Don't count carpentry, runecrafting, social in skill average
            if skill not in ['carpentry', 'runecrafting', 'social']:
                total_skill_level += level
                skill_count += 1

        skill_average = total_skill_level / skill_count if skill_count > 0 else 0

        return {
            'skills': skill_data,
            'skill_average': skill_average,
            'total_skill_level': total_skill_level
        }

    def analyze_slayers(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze slayer progress."""
        if not player_data or 'slayer' not in player_data:
            return {}

        slayer_bosses = player_data.get('slayer', {}).get('slayer_bosses', {})

        slayer_data = {}
        total_slayer_xp = 0

        for boss_name, boss_data in slayer_bosses.items():
            xp = boss_data.get('xp', 0)
            total_slayer_xp += xp

            slayer_data[boss_name] = {
                'xp': xp,
                'kills': boss_data.get('boss_kills_tier_0', 0) +
                        boss_data.get('boss_kills_tier_1', 0) +
                        boss_data.get('boss_kills_tier_2', 0) +
                        boss_data.get('boss_kills_tier_3', 0) +
                        boss_data.get('boss_kills_tier_4', 0)
            }

        return {
            'slayers': slayer_data,
            'total_slayer_xp': total_slayer_xp
        }

    def calculate_networth_estimate(self, player_data: Dict[str, Any]) -> float:
        """Rough estimate of networth based on purse and bank."""
        purse = player_data.get('currencies', {}).get('coin_purse', 0)

        # Try to get bank balance (might be in banking data)
        bank = 0
        if 'profile' in player_data and 'banking' in player_data['profile']:
            bank = player_data['profile']['banking'].get('balance', 0)

        return purse + bank

    def get_progression_tips(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate personalized progression tips based on analysis."""
        tips = []

        # Skill-based tips
        if 'skills' in analysis:
            skill_avg = analysis.get('skill_average', 0)

            if skill_avg < 15:
                tips.append("🌱 **Early Game Focus**: Your skill average is low. Focus on leveling combat, farming, and mining for a solid foundation.")

            if skill_avg < 30:
                tips.append("📈 **Mid-Game Grind**: Work on getting all skills to level 20+ for better gear access and money-making methods.")

            # Check individual skills
            skills = analysis.get('skills', {})
            low_skills = [name for name, data in skills.items()
                         if data['level'] < skill_avg - 5 and name not in ['carpentry', 'runecrafting', 'social']]

            if low_skills:
                tips.append(f"⚠️ **Weak Skills**: Your {', '.join(low_skills[:3])} skills are lagging behind. Balance them for better progression.")

        # Slayer-based tips
        if 'slayers' in analysis:
            total_slayer = analysis.get('total_slayer_xp', 0)

            if total_slayer < 100000:
                tips.append("⚔️ **Start Slayers**: Begin doing slayer quests! They're essential for combat progression and coins.")

            if total_slayer > 0:
                slayers = analysis.get('slayers', {})
                for boss, data in slayers.items():
                    if data['xp'] < 10000:
                        tips.append(f"🎯 **{boss.title()} Slayer**: You haven't progressed much in {boss}. Try some runs!")

        # General tips
        if not tips:
            tips.append("✨ **Doing Great!** Keep grinding and set specific goals. Consider working toward dungeons or getting minion slots!")

        return tips[:5]  # Return max 5 tips

    def format_skill_display(self, skill_name: str, skill_data: Dict[str, Any]) -> str:
        """Format a skill for display."""
        level = skill_data['level']
        progress = skill_data.get('progress', 0)

        # Create progress bar
        filled = int(progress / 10)
        empty = 10 - filled
        bar = f"{'█' * filled}{'░' * empty}"

        return f"**{skill_name.title()}** {level} {bar} {progress:.1f}%"

    def get_profile_summary(self, player_data: Dict[str, Any], profile: Dict[str, Any]) -> str:
        """Generate a comprehensive profile summary."""
        profile_name = profile.get('cute_name', 'Unknown')

        # Analyze data
        skill_analysis = self.analyze_skills(player_data)
        slayer_analysis = self.analyze_slayers(player_data)

        summary_parts = [
            f"🏝️ **Skyblock Profile: {profile_name}**\n"
        ]

        # Skills
        if skill_analysis:
            skill_avg = skill_analysis.get('skill_average', 0)
            summary_parts.append(f"📊 **Skill Average:** {skill_avg:.1f}\n")

            # Top 3 skills
            skills = skill_analysis.get('skills', {})
            sorted_skills = sorted(skills.items(), key=lambda x: x[1]['level'], reverse=True)[:3]

            summary_parts.append("**Top Skills:**")
            for skill_name, skill_data in sorted_skills:
                summary_parts.append(self.format_skill_display(skill_name, skill_data))

        # Slayers
        if slayer_analysis:
            total_slayer = slayer_analysis.get('total_slayer_xp', 0)
            summary_parts.append(f"\n⚔️ **Total Slayer XP:** {total_slayer:,.0f}")

        # Coins
        purse = player_data.get('currencies', {}).get('coin_purse', 0)
        summary_parts.append(f"\n💰 **Purse:** {purse:,.2f} coins")

        return "\n".join(summary_parts)


# Global analyzer instance
skyblock_analyzer = SkyblockAnalyzer()
