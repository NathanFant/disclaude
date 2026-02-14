# Smart Reminder System

DisClaude now features an **intelligent reminder system** that automatically detects when you want to be reminded about something - no slash commands needed!

---

## How It Works

Just **mention the bot naturally** and ask for a reminder:

```
@DisClaude remind me in 30 minutes to check the oven
@DisClaude remind me tomorrow at 3pm to call mom
@DisClaude don't forget to remind me about the meeting next week
```

The bot will:
1. ✅ Detect it's a reminder request
2. ⏰ Parse the time (30 minutes, tomorrow 3pm, next week)
3. 📝 Extract what you want to be reminded about
4. 🔔 Schedule the reminder
5. ✅ Confirm with you

When the time comes, you'll get pinged with your reminder!

---

## Natural Language Examples

### Relative Time

```
@DisClaude remind me in 5 minutes
@DisClaude remind me in 2 hours to take a break
@DisClaude remind me in 3 days about the dentist
@DisClaude alert me in 1 week
```

### Specific Times

```
@DisClaude remind me at 3pm to start dinner
@DisClaude remind me at 14:00
@DisClaude notify me at 9am tomorrow
```

### Natural Expressions

```
@DisClaude remind me tomorrow to submit the report
@DisClaude remind me tonight to lock the door
@DisClaude remind me next Monday about the meeting
@DisClaude ping me next week
```

### Alternative Phrasings

All of these work:
- "remind me..."
- "reminder to..."
- "alert me..."
- "notify me..."
- "ping me..."
- "tell me..."
- "let me know..."
- "don't forget..."

---

## What Gets Detected

The bot looks for:
1. **Reminder keywords**: "remind", "alert", "notify", "ping", "tell me", etc.
2. **Time indicators**: "in", "at", "tomorrow", "next week", "minutes", "hours", etc.
3. **Context**: Short messages with time expressions

### Examples That Work

✅ "remind me in 30 minutes to check the oven"
✅ "in 2 hours ping me"
✅ "tomorrow at 3pm don't forget"
✅ "alert me next week"
✅ "remind me to call mom tomorrow"

### Examples That Don't

❌ "I should probably remember this tomorrow" (too vague)
❌ "remind" (no time specified)
❌ "in 5 minutes" (no reminder keyword when not mentioned)

---

## Commands

### `/reminders`
**View your scheduled reminders**

Shows all your upcoming reminders with:
- What you're being reminded about
- When it will trigger
- How long until it fires

**Example Output:**
```
⏰ Your Scheduled Reminders

1. check the oven
   🕐 February 13 at 03:30 PM (25 minutes)

2. call mom
   🕐 February 14 at 03:00 PM (1 day)

3. meeting
   🕐 February 20 at 09:00 AM (7 days)
```

---

### `/cancelreminder <number>`
**Cancel a scheduled reminder**

Use the number from `/reminders` to cancel a specific reminder.

**Example:**
```
/cancelreminder number:2
✅ Canceled reminder: call mom
```

---

### `/allreminders` (Admin Only)
**View all reminders across all users**

Shows up to 20 upcoming reminders from all users.
Useful for admins to monitor scheduler usage.

---

## Features

### Smart Time Parsing

The bot understands various time formats:

| Format | Example | Result |
|--------|---------|--------|
| Minutes | "in 30 minutes" | 30 min from now |
| Hours | "in 2 hours" | 2 hours from now |
| Days | "in 3 days" | 3 days from now |
| Weeks | "in 1 week" | 7 days from now |
| Tomorrow | "tomorrow" | Next day, same time |
| Tonight | "tonight" | Today at 8 PM |
| Specific time | "at 3pm" | Today at 3 PM |
| Combined | "tomorrow at 3pm" | Next day at 3 PM |
| Natural | "next Monday" | Next Monday, current time |

### Intelligent Content Extraction

The bot extracts what you want to be reminded about:

**Input:** "remind me in 30 minutes to check the oven"
**Extracts:** "check the oven"

**Input:** "don't forget to call mom tomorrow at 3pm"
**Extracts:** "call mom"

**Input:** "remind me about the meeting next week"
**Extracts:** "about the meeting"

### Confirmation Message

When you set a reminder, you get instant confirmation:

```
✅ Got it! I'll remind you in 30 minutes
📝 Reminder: check the oven
🕐 Time: February 13, 2026 at 03:30 PM
```

### Reminder Delivery

When the time comes:

```
⏰ Reminder @YourName

check the oven

You asked: "remind me in 30 minutes to check the oven"
```

---

## How The Detection Works

### Step 1: Keyword Detection

Checks for reminder-related words:
- remind, reminder, alert, notify, ping, tell me, let me know, don't forget

### Step 2: Time Expression Detection

Looks for time indicators:
- in, at, tomorrow, tonight, later, next week, minutes, hours, days

### Step 3: Message Analysis

If found, parses:
1. **Time expression** → Converts to datetime
2. **Reminder content** → Extracts what to remind about
3. **Validates** → Must be in the future

### Step 4: Scheduling

Uses APScheduler to:
- Schedule a one-time job
- Store task metadata
- Execute at the specified time

---

## Technical Details

### Architecture

```
User mentions bot + reminder request
    ↓
time_parser.detect_reminder_request()
    ↓
Detects: keywords + time indicators
    ↓
time_parser.parse_time_from_message()
    ↓
Extracts: datetime + reminder content
    ↓
smart_scheduler.schedule_reminder()
    ↓
Creates scheduled job
    ↓
Confirms to user
    ↓
[Time passes...]
    ↓
Scheduler triggers at specified time
    ↓
send_scheduled_message()
    ↓
User gets pinged with reminder
```

### Components

**scheduler.py**
- `SmartScheduler` class
- Uses APScheduler (AsyncIO-based)
- Manages scheduled tasks
- Stores task metadata

**time_parser.py**
- `TimeParser` class
- Uses dateparser library
- Regex patterns for common formats
- Natural language time parsing

**bot.py**
- Integration in `on_message` event
- Automatic detection and scheduling
- Commands for management

### Storage

**In-Memory (Current):**
- Scheduled tasks stored in memory
- Resets when bot restarts
- Fast and simple

**Future Enhancement:**
- Persist to database (SQLite/PostgreSQL)
- Survive bot restarts
- Long-term reminder support

---

## Limitations

### Time Parsing

**Works:**
- ✅ "in 30 minutes"
- ✅ "tomorrow at 3pm"
- ✅ "next week"

**Doesn't Work:**
- ❌ "in a bit" (too vague)
- ❌ "later" (no specific time)
- ❌ "soon" (ambiguous)

### Persistence

- ⚠️ Reminders are lost if bot restarts
- For long-term reminders (weeks/months), consider persistence

### Rate Limits

- Bot message rate limits still apply
- If many reminders fire simultaneously, they'll queue

---

## Examples

### Quick Reminder

```
User: @DisClaude remind me in 5 minutes
Bot: ✅ Got it! I'll remind you in 5 minutes
     📝 Reminder: remind me
     🕐 Time: February 13, 2026 at 02:35 PM

[5 minutes later]
Bot: ⏰ Reminder @User
     remind me
     You asked: "remind me in 5 minutes"
```

### Specific Task

```
User: @DisClaude remind me tomorrow at 2pm to submit the report
Bot: ✅ Got it! I'll remind you in 1 day
     📝 Reminder: submit the report
     🕐 Time: February 14, 2026 at 02:00 PM

[Next day at 2pm]
Bot: ⏰ Reminder @User
     submit the report
     You asked: "remind me tomorrow at 2pm to submit the report"
```

### Multiple Reminders

```
User: @DisClaude remind me in 30 minutes to check email
Bot: ✅ Got it! I'll remind you in 30 minutes...

User: @DisClaude remind me at 5pm to start dinner
Bot: ✅ Got it! I'll remind you in 2 hours...

User: /reminders
Bot: ⏰ Your Scheduled Reminders
     1. check email (28 minutes)
     2. start dinner (2 hours)
```

---

## Advanced Usage

### Chaining with Personality

Since the bot has personality, you can be more natural:

```
@DisClaude hey, can you ping me in an hour? I need to remember to take out the trash
```

The bot will:
1. Detect reminder request
2. Schedule it
3. Respond with personality-appropriate confirmation

### Integration with Other Features

```
@DisClaude remind me tomorrow to check my Skyblock stats
```

When reminded, you can then:
```
@DisClaude /sb
```

---

## Future Enhancements

Possible additions:

### Recurring Reminders
- [ ] "Remind me every day at 9am"
- [ ] "Remind me every Monday"
- [ ] Cron-like syntax support

### Reminder Templates
- [ ] Save common reminders
- [ ] Quick preset reminders
- [ ] Reminder categories

### Advanced Features
- [ ] Snooze functionality
- [ ] Reminder notes/details
- [ ] Attach images/links
- [ ] Share reminders with others

### Persistence
- [ ] Database storage
- [ ] Survive bot restarts
- [ ] Long-term reminders (months/years)

### Smart Features
- [ ] Location-based reminders (if integrated with location API)
- [ ] Conditional reminders (if X then remind)
- [ ] Reminder chains (after X, remind about Y)

---

## Troubleshooting

### "Reminder not detected"

**Problem**: Bot responds normally instead of scheduling

**Solution**:
- Make sure you're mentioning the bot
- Use clear reminder keywords ("remind me", "alert me")
- Include a time expression ("in 30 minutes", "tomorrow")

### "Invalid time"

**Problem**: Time parsing fails

**Solution**:
- Use standard formats: "in X minutes/hours/days"
- For specific times: "at 3pm" or "at 14:00"
- For dates: "tomorrow", "next Monday"
- Avoid vague terms: "later", "soon", "in a bit"

### "Reminder didn't fire"

**Problem**: Didn't receive reminder at scheduled time

**Possible causes**:
- Bot was offline/restarted (reminders are lost)
- Discord outage
- Bot was removed from server
- Channel was deleted

**Solution**:
- Check `/reminders` to verify it's scheduled
- For important reminders, use external services too

### "Too many reminders"

**Problem**: Want to clean up old reminders

**Solution**:
```
/reminders              # View all
/cancelreminder number:1  # Cancel specific ones
```

---

## Best Practices

### For Users

1. **Be Specific**
   - ✅ "remind me in 30 minutes to check the oven"
   - ❌ "remind me later"

2. **Use Clear Timeframes**
   - ✅ "tomorrow at 3pm"
   - ❌ "sometime tomorrow"

3. **Keep Content Short**
   - ✅ "call mom"
   - ❌ "make sure to remember to call mom and also text dad and maybe check in with my sister too"

4. **Check Your Reminders**
   - Use `/reminders` to verify they're set
   - Cancel ones you don't need

### For Admins

1. **Monitor Usage**
   - Use `/allreminders` to see activity
   - Watch for spam/abuse

2. **Restart Considerations**
   - Reminders are lost on restart
   - Warn users if planning maintenance

3. **Rate Limiting**
   - Consider limiting reminders per user if needed
   - Current implementation has no limits

---

**Never forget anything again! ⏰🔔**
