# Evolving Personality System

DisClaude features an **evolving personality system** that adapts and changes based on interactions with users.

---

## How It Works

The bot's personality is defined by 5 core traits that shift over time based on conversations:

### Personality Traits

| Trait | Range | Description |
|-------|-------|-------------|
| **Friendliness** | 0-100 | Cold & distant → Warm & enthusiastic |
| **Formality** | 0-100 | Casual & playful → Professional & formal |
| **Humor** | 0-100 | Serious & straightforward → Witty & humorous |
| **Verbosity** | 0-100 | Concise & brief → Detailed & verbose |
| **Helpfulness** | 0-100 | Minimal effort → Maximum effort |

All traits start at **50** (balanced) except Helpfulness which starts at **70**.

---

## Personality Evolution

### What Affects Personality?

The bot **learns and adapts** based on:

#### 1. **Topic Detection**
- **Coding questions** → More formal, less verbose
- **Polite language** ("please", "thanks") → More friendly
- **Humor/jokes** ("lol", "haha", emojis) → More humorous, less formal
- **Requests for detail** ("explain", "elaborate") → More verbose, more helpful
- **Requests for brevity** ("quick", "brief", "tldr") → Less verbose

#### 2. **Interaction Frequency**
- Every **10 interactions**, personality naturally drifts toward balance
- Prevents extreme personality shifts
- Keeps the bot feeling natural

#### 3. **Cumulative Experience**
- **20+ interactions** → Bot becomes familiar with the community
- **100+ interactions** → Mature, experienced tone

### Example Evolution

```
User: "hey lol can you help? 😂"
→ Increases: Humor +5, Friendliness +3
→ Decreases: Formality -5

User: "Please explain in detail how async/await works"
→ Increases: Verbosity +5, Helpfulness +3, Formality +5
```

---

## System Prompt Generation

The personality traits generate a **dynamic system prompt** that instructs Claude how to behave.

### Example System Prompts

**Balanced Personality (all traits ~50):**
```
You are DisClaude, a helpful Discord assistant powered by Claude AI.
You are friendly and approachable.
You can make light jokes when appropriate.
You are helpful and thorough in your responses.
```

**Experienced, Casual Bot (many interactions, low formality, high humor):**
```
You are DisClaude, a helpful Discord assistant powered by Claude AI.
You are warm, enthusiastic, and use friendly emojis occasionally.
You use casual language and can be playful.
You enjoy witty remarks and occasional jokes.
You go above and beyond to help users, offering examples and alternatives.
You've had 150 conversations and have developed a mature, experienced tone.
You've noticed this community enjoys humor.
```

**Professional Coding Assistant (high formality, low verbosity):**
```
You are DisClaude, a helpful Discord assistant powered by Claude AI.
You are professional and direct.
You communicate formally and professionally.
You keep responses concise and to the point.
You're particularly knowledgeable about programming.
```

---

## Commands

### `/personality` (Everyone)
View the current personality traits and statistics.

**Example Output:**
```
🎭 Bot Personality

Traits:
😊 Friendliness: ████████░░ 75%
🎩 Formality: ████░░░░░░ 40%
😄 Humor: ██████░░░░ 60%
📝 Verbosity: █████░░░░░ 50%
🤝 Helpfulness: ████████░░ 80%

Experience:
• Interactions: 47
• Unique users: 8
• Uptime: 12.3 hours

Top Topics: humor (12), coding (8), polite (5)
```

### `/systemprompt` (Admin Only)
View the exact system prompt currently being used.

Shows how personality traits translate into Claude's instructions.

### `/resetpersonality` (Admin Only)
Reset the personality to default state.

**Warning:** This clears all personality evolution and statistics!

---

## Personality Persistence

### Current Implementation
- Personality is stored **in-memory**
- Resets when the bot restarts

### Future Enhancements
To make personality persistent across restarts, you could:

1. **Add periodic saving to file:**
```python
import json
import os

# Save personality state
def save_personality():
    with open('personality_state.json', 'w') as f:
        json.dump(personality.to_dict(), f)

# Load personality state on startup
if os.path.exists('personality_state.json'):
    with open('personality_state.json', 'r') as f:
        data = json.load(f)
        personality = PersonalityTracker.from_dict(data)
```

2. **Use a database** (PostgreSQL, SQLite, Redis)
3. **Use Railway's persistent storage**

---

## Customization

### Adjusting Evolution Speed

In `personality.py`, modify trait adjustment amounts:

```python
# Current (moderate evolution)
self._adjust_trait('friendliness', 3)

# Faster evolution
self._adjust_trait('friendliness', 10)

# Slower evolution
self._adjust_trait('friendliness', 1)
```

### Adding Custom Traits

You can add new personality dimensions:

```python
self.personality_traits = {
    'friendliness': 50,
    'formality': 50,
    'humor': 50,
    'verbosity': 50,
    'helpfulness': 70,
    'technicality': 50,  # New trait!
    'creativity': 50,     # New trait!
}
```

### Custom Topic Detection

Add your own topic triggers in `record_interaction()`:

```python
if any(word in content_lower for word in ['music', 'song', 'artist']):
    self.topics['music'] += 1
    self._adjust_trait('creativity', 5)
    self._adjust_trait('formality', -3)
```

---

## Best Practices

### For Server Admins

1. **Monitor Personality Regularly**
   - Use `/personality` to check current state
   - Ensure traits align with community culture

2. **Reset When Needed**
   - If personality drifts too far, use `/resetpersonality`
   - Good to reset after major community changes

3. **Encourage Interaction**
   - More interactions = more refined personality
   - Personality evolves best with diverse conversations

### For Users

1. **Natural Interaction**
   - Just talk normally - the bot learns from you!
   - Your language style influences the bot

2. **Variety Helps**
   - Ask different types of questions
   - Mix serious and casual conversation

3. **Feedback**
   - Check `/personality` to see how your interactions shaped the bot
   - Fun to see community impact!

---

## Technical Details

### Architecture

```
User Message
    ↓
personality.record_interaction()  ← Analyzes content
    ↓
Adjusts personality traits
    ↓
personality.get_system_prompt()   ← Generates dynamic prompt
    ↓
Sends to Claude API with system prompt
    ↓
Claude responds based on personality
```

### Memory Usage

- **Minimal** - Only stores:
  - 5 trait values (integers)
  - Topic counts (dictionary)
  - User interaction counts (dictionary)
  - Timestamps

### Performance Impact

- **Negligible**
  - Personality recording: < 1ms
  - System prompt generation: < 1ms
  - No API calls for personality logic

---

## Examples

### Community Scenarios

#### Coding Discord Server
After 100 interactions focused on programming:
- **Formality:** 70% (professional tone)
- **Verbosity:** 40% (concise code examples)
- **Helpfulness:** 90% (goes deep into solutions)
- **Result:** Technical, efficient assistant

#### Casual Friend Group
After 100 interactions with jokes and emojis:
- **Friendliness:** 85% (warm and enthusiastic)
- **Formality:** 25% (very casual)
- **Humor:** 80% (makes jokes)
- **Result:** Fun, playful chatbot

#### Mixed Community
Balanced mix of questions:
- **All traits:** 45-55% (balanced)
- **Result:** Adaptable, well-rounded assistant

---

## FAQ

**Q: Does personality affect which Claude model is used?**
A: No, personality only affects the system prompt. Model selection is based on question complexity.

**Q: Can users see the personality changing in real-time?**
A: Yes! Use `/personality` to see current traits. You'll notice the bot's tone shifting gradually.

**Q: What happens if personality traits hit 0 or 100?**
A: Traits are capped at 0-100. Natural drift prevents getting stuck at extremes.

**Q: Can I manually set personality traits?**
A: Currently no, but you could add an admin command to do this.

**Q: Is personality per-channel or global?**
A: Global - one personality across all channels and servers.

**Q: Could I make per-server personalities?**
A: Yes! Modify the code to use `personality_trackers[guild_id]` instead of one global instance.

---

## Contributing Ideas

Want to enhance the personality system? Here are ideas:

1. **Sentiment Analysis** - Adjust traits based on message positivity/negativity
2. **Time-Based Changes** - Different personality during day/night
3. **Mood System** - Temporary emotional states that affect responses
4. **User Affinity** - Remember individual users and adjust behavior per-user
5. **Learning from Reactions** - Track emoji reactions to responses
6. **Personality Presets** - Quick-switch between "Professional", "Casual", "Funny" modes

---

**Enjoy watching your bot's personality evolve! 🎭**
