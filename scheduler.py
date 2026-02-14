"""Smart scheduler for reminders and cron jobs."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from typing import Optional, Dict, Any, Callable
import asyncio


class SmartScheduler:
    """Intelligent scheduler for reminders and scheduled tasks."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduled_tasks = {}  # task_id -> task_info
        self.task_counter = 0
        self.started = False

    def start(self):
        """Start the scheduler."""
        if not self.started:
            self.scheduler.start()
            self.started = True
            print("[SCHEDULER] Started scheduler")

    def stop(self):
        """Stop the scheduler."""
        if self.started:
            self.scheduler.shutdown()
            self.started = False
            print("[SCHEDULER] Stopped scheduler")

    async def schedule_reminder(
        self,
        when: datetime,
        channel_id: int,
        user_id: int,
        message: str,
        send_function: Callable,
        original_message: str = None
    ) -> str:
        """Schedule a reminder to be sent later."""
        self.task_counter += 1
        task_id = f"reminder_{self.task_counter}"

        # Create the job
        async def send_reminder():
            """Send the reminder when it's time."""
            reminder_text = (
                f"⏰ **Reminder** <@{user_id}>\n\n"
                f"{message}\n\n"
            )
            if original_message:
                reminder_text += f"_You asked: \"{original_message}\"_"

            await send_function(channel_id, reminder_text)

            # Remove from scheduled tasks
            if task_id in self.scheduled_tasks:
                del self.scheduled_tasks[task_id]

        # Add job to scheduler
        job = self.scheduler.add_job(
            send_reminder,
            trigger=DateTrigger(run_date=when),
            id=task_id,
            name=f"Reminder for user {user_id}"
        )

        # Store task info
        self.scheduled_tasks[task_id] = {
            'id': task_id,
            'when': when,
            'channel_id': channel_id,
            'user_id': user_id,
            'message': message,
            'original_message': original_message,
            'job': job
        }

        return task_id

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        if task_id in self.scheduled_tasks:
            try:
                self.scheduler.remove_job(task_id)
                del self.scheduled_tasks[task_id]
                return True
            except Exception as e:
                print(f"[SCHEDULER] Error canceling task {task_id}: {e}")
                return False
        return False

    def get_user_tasks(self, user_id: int) -> list:
        """Get all scheduled tasks for a user."""
        return [
            task for task in self.scheduled_tasks.values()
            if task['user_id'] == user_id
        ]

    def get_all_tasks(self) -> list:
        """Get all scheduled tasks."""
        return list(self.scheduled_tasks.values())

    def get_task_count(self) -> int:
        """Get total number of scheduled tasks."""
        return len(self.scheduled_tasks)


# Global scheduler instance
smart_scheduler = SmartScheduler()
