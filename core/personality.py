"""Personality system for the Discord bot."""
from collections import defaultdict
from datetime import datetime
import json


class PersonalityTracker:
    """Tracks and evolves bot personality based on interactions."""

    def __init__(self):
        self.interaction_count = 0
        self.topics = defaultdict(int)  # topic -> count
        self.user_interactions = defaultdict(int)  # user_id -> count
        self.personality_traits = {
            'friendliness': 50,      # 0-100: cold to warm
            'formality': 50,         # 0-100: casual to formal
            'humor': 50,             # 0-100: serious to humorous
            'verbosity': 50,         # 0-100: concise to verbose
            'helpfulness': 70,       # 0-100: minimal to maximum effort
        }
        self.start_time = datetime.now()
        self.last_personality_shift = datetime.now()

    def record_interaction(self, user_id: int, content: str, is_question: bool = True):
        """Record an interaction and update personality traits."""
        self.interaction_count += 1
        self.user_interactions[user_id] += 1

        # Detect topics/themes
        content_lower = content.lower()

        # Track topics
        if any(word in content_lower for word in ['code', 'program', 'function', 'bug', 'error']):
            self.topics['coding'] += 1
            self._adjust_trait('formality', 5)  # More formal for coding
            self._adjust_trait('verbosity', -3)  # More concise for code

        if any(word in content_lower for word in ['help', 'please', 'thanks', 'thank you']):
            self.topics['polite'] += 1
            self._adjust_trait('friendliness', 3)

        if any(word in content_lower for word in ['lol', 'haha', 'funny', '😂', '🤣']):
            self.topics['humor'] += 1
            self._adjust_trait('humor', 5)
            self._adjust_trait('formality', -5)

        if any(word in content_lower for word in ['explain', 'detail', 'elaborate', 'more']):
            self.topics['detailed'] += 1
            self._adjust_trait('verbosity', 5)
            self._adjust_trait('helpfulness', 3)

        if any(word in content_lower for word in ['quick', 'brief', 'short', 'tldr']):
            self.topics['brief'] += 1
            self._adjust_trait('verbosity', -5)

        # Evolve based on interaction frequency
        if self.interaction_count % 10 == 0:
            self._natural_evolution()

    def _adjust_trait(self, trait: str, amount: int):
        """Adjust a personality trait, keeping it within bounds."""
        if trait in self.personality_traits:
            self.personality_traits[trait] = max(0, min(100,
                self.personality_traits[trait] + amount))

    def _natural_evolution(self):
        """Natural personality drift over time."""
        # Gradually shift toward balanced personality
        for trait, value in self.personality_traits.items():
            if value > 60:
                self._adjust_trait(trait, -1)
            elif value < 40:
                self._adjust_trait(trait, 1)

        self.last_personality_shift = datetime.now()

    def get_system_prompt(self) -> str:
        """Generate a system prompt based on current personality."""
        traits = self.personality_traits

        # Base personality
        prompt_parts = [
            "You are DisClaude, a helpful Discord assistant powered by Claude AI.",
        ]

        # Friendliness
        if traits['friendliness'] > 70:
            prompt_parts.append("You are warm, enthusiastic, and use friendly emojis occasionally.")
        elif traits['friendliness'] > 40:
            prompt_parts.append("You are friendly and approachable.")
        else:
            prompt_parts.append("You are professional and direct.")

        # Formality
        if traits['formality'] > 70:
            prompt_parts.append("You communicate formally and professionally.")
        elif traits['formality'] < 30:
            prompt_parts.append("You use casual language and can be playful.")

        # Humor
        if traits['humor'] > 70:
            prompt_parts.append("You enjoy witty remarks and occasional jokes.")
        elif traits['humor'] > 40:
            prompt_parts.append("You can make light jokes when appropriate.")

        # Verbosity
        if traits['verbosity'] > 70:
            prompt_parts.append("You provide detailed, comprehensive explanations.")
        elif traits['verbosity'] < 30:
            prompt_parts.append("You keep responses concise and to the point.")

        # Helpfulness
        if traits['helpfulness'] > 80:
            prompt_parts.append("You go above and beyond to help users, offering examples and alternatives.")
        elif traits['helpfulness'] > 50:
            prompt_parts.append("You are helpful and thorough in your responses.")

        # Add interaction-based context
        if self.interaction_count > 100:
            prompt_parts.append(f"You've had {self.interaction_count} conversations and have developed a mature, experienced tone.")
        elif self.interaction_count > 20:
            prompt_parts.append("You're becoming familiar with the community.")

        # Top topics influence
        if self.topics:
            top_topic = max(self.topics.items(), key=lambda x: x[1])[0]
            if top_topic == 'coding' and self.topics[top_topic] > 10:
                prompt_parts.append("You're particularly knowledgeable about programming.")
            elif top_topic == 'humor' and self.topics[top_topic] > 10:
                prompt_parts.append("You've noticed this community enjoys humor.")

        return " ".join(prompt_parts)

    def get_personality_summary(self) -> dict:
        """Get a summary of current personality state."""
        return {
            'traits': self.personality_traits.copy(),
            'interactions': self.interaction_count,
            'unique_users': len(self.user_interactions),
            'top_topics': dict(sorted(self.topics.items(), key=lambda x: x[1], reverse=True)[:5]),
            'uptime_hours': (datetime.now() - self.start_time).total_seconds() / 3600,
            'system_prompt': self.get_system_prompt()
        }

    def reset_personality(self):
        """Reset personality to default state."""
        self.__init__()

    def to_dict(self) -> dict:
        """Serialize personality state to dictionary."""
        return {
            'interaction_count': self.interaction_count,
            'topics': dict(self.topics),
            'user_interactions': dict(self.user_interactions),
            'personality_traits': self.personality_traits.copy(),
            'start_time': self.start_time.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PersonalityTracker':
        """Deserialize personality state from dictionary."""
        tracker = cls()
        tracker.interaction_count = data.get('interaction_count', 0)
        tracker.topics = defaultdict(int, data.get('topics', {}))
        tracker.user_interactions = defaultdict(int, data.get('user_interactions', {}))
        tracker.personality_traits = data.get('personality_traits', tracker.personality_traits)
        if 'start_time' in data:
            tracker.start_time = datetime.fromisoformat(data['start_time'])
        return tracker
