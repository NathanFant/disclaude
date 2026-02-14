"""Natural language time parser for scheduling."""
import dateparser
from datetime import datetime, timedelta
from typing import Optional, Tuple
import re


class TimeParser:
    """Parse natural language time expressions."""

    def __init__(self):
        # Common reminder patterns
        self.reminder_patterns = [
            # "remind me in X minutes/hours/days"
            r'remind me (?:in )?(\d+) (minute|hour|day|week)s?',
            # "in X minutes/hours"
            r'in (\d+) (minute|hour|day|week)s?',
            # "X minutes/hours from now"
            r'(\d+) (minute|hour|day|week)s? from now',
            # "tomorrow", "next week", etc.
            r'(tomorrow|tonight|next week|next month)',
            # "at 3pm", "at 14:00"
            r'at (\d{1,2}:?\d{0,2}\s?(?:am|pm|AM|PM)?)',
        ]

    def detect_reminder_request(self, message: str) -> bool:
        """Check if message contains a reminder request."""
        message_lower = message.lower()

        # Keywords that suggest a reminder
        reminder_keywords = [
            'remind me', 'reminder', 'remind us', 'alert me',
            'notify me', 'ping me', 'tell me', 'let me know',
            'don\'t forget', 'remember to'
        ]

        # Time indicators
        time_indicators = [
            'in', 'at', 'tomorrow', 'tonight', 'later',
            'next week', 'next month', 'minutes', 'hours',
            'days', 'weeks'
        ]

        has_reminder_keyword = any(keyword in message_lower for keyword in reminder_keywords)
        has_time_indicator = any(indicator in message_lower for indicator in time_indicators)

        return has_reminder_keyword or (has_time_indicator and len(message.split()) < 20)

    def parse_time_from_message(self, message: str) -> Optional[Tuple[datetime, str]]:
        """
        Extract time and reminder message from natural language.

        Returns:
            Tuple of (datetime, reminder_message) or None if can't parse
        """
        message_lower = message.lower()

        # Try to extract time expression
        time_expression = None
        reminder_message = message

        # Pattern matching for common formats
        for pattern in self.reminder_patterns:
            match = re.search(pattern, message_lower)
            if match:
                if len(match.groups()) == 2:
                    # "X units" format
                    amount = int(match.group(1))
                    unit = match.group(2)
                    time_expression = f"{amount} {unit}s from now"
                elif len(match.groups()) == 1:
                    # Direct time expression
                    time_expression = match.group(1)
                break

        # If no pattern match, try dateparser on the whole message
        if not time_expression:
            parsed = dateparser.parse(
                message,
                settings={
                    'PREFER_DATES_FROM': 'future',
                    'RELATIVE_BASE': datetime.now()
                }
            )
            if parsed and parsed > datetime.now():
                # Extract what the reminder is about
                reminder_message = self._extract_reminder_content(message)
                return parsed, reminder_message
            return None

        # Parse the time expression
        parsed_time = dateparser.parse(
            time_expression,
            settings={
                'PREFER_DATES_FROM': 'future',
                'RELATIVE_BASE': datetime.now()
            }
        )

        if not parsed_time or parsed_time <= datetime.now():
            return None

        # Extract the reminder content
        reminder_message = self._extract_reminder_content(message)

        return parsed_time, reminder_message

    def _extract_reminder_content(self, message: str) -> str:
        """Extract what the reminder is about from the message."""
        message_lower = message.lower()

        # Remove common reminder phrases
        remove_phrases = [
            'remind me to ', 'remind me ', 'reminder to ', 'reminder ',
            'alert me to ', 'alert me ', 'notify me to ', 'notify me ',
            'ping me to ', 'ping me ', 'tell me to ', 'tell me ',
            'let me know to ', 'let me know ', 'don\'t forget to ',
            'remember to '
        ]

        content = message
        for phrase in remove_phrases:
            if phrase in message_lower:
                # Find the phrase and remove everything up to and including it
                idx = message_lower.find(phrase)
                content = message[idx + len(phrase):]
                break

        # Remove time expressions from the content
        for pattern in self.reminder_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        # Clean up
        content = content.strip()
        content = re.sub(r'\s+', ' ', content)  # Remove extra spaces

        # If content is too short or empty, use original message
        if len(content) < 3:
            content = message

        return content

    def format_time_until(self, target_time: datetime) -> str:
        """Format how long until the target time."""
        now = datetime.now()
        delta = target_time - now

        if delta.total_seconds() < 60:
            return "less than a minute"
        elif delta.total_seconds() < 3600:
            minutes = int(delta.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''}"
        elif delta.total_seconds() < 86400:
            hours = int(delta.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''}"
        else:
            days = delta.days
            return f"{days} day{'s' if days != 1 else ''}"


# Global time parser instance
time_parser = TimeParser()
