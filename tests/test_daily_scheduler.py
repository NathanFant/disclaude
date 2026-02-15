"""Test daily scheduler functionality."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import asyncio
from core.scheduler import SmartScheduler
from datetime import datetime


async def test_daily_scheduler():
    """Test that daily tasks can be scheduled."""
    print("\n" + "="*70)
    print("TEST: Daily Scheduler")
    print("="*70)

    scheduler = SmartScheduler()
    scheduler.start()

    # Track if task was registered
    task_executed = False

    async def test_task():
        """Simple test task."""
        nonlocal task_executed
        task_executed = True
        print("✅ Test task executed!")

    try:
        # Schedule a daily task
        scheduler.schedule_daily_task(
            task_id="test_daily_task",
            task_function=test_task,
            hour=20,
            minute=0
        )

        # Check that the job was added to the scheduler
        jobs = scheduler.scheduler.get_jobs()
        job_ids = [job.id for job in jobs]

        print(f"Scheduled jobs: {job_ids}")
        assert "test_daily_task" in job_ids, "Daily task should be scheduled"
        print("✅ Daily task successfully scheduled")

        # Get the job details
        job = scheduler.scheduler.get_job("test_daily_task")
        print(f"✅ Job details:")
        print(f"   - ID: {job.id}")
        print(f"   - Name: {job.name}")
        print(f"   - Trigger: {job.trigger}")
        print(f"   - Next run: {job.next_run_time}")

        # Verify it's a cron trigger
        assert hasattr(job.trigger, 'fields'), "Should be a cron trigger"
        print("✅ Trigger is correctly set as cron")

        # Clean up
        scheduler.scheduler.remove_job("test_daily_task")
        scheduler.stop()

        print("\n✅ DAILY SCHEDULER TEST PASSED")
        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        scheduler.stop()
        return False


async def test_hypixel_keepalive_function():
    """Test the Hypixel API keep-alive function."""
    print("\n" + "="*70)
    print("TEST: Hypixel API Keep-Alive Function")
    print("="*70)

    # Import the keep-alive function
    # We need to mock discord to import bot.py
    import unittest.mock as mock
    sys.modules['discord'] = mock.MagicMock()
    sys.modules['discord.ext'] = mock.MagicMock()
    sys.modules['discord.ext.commands'] = mock.MagicMock()
    sys.modules['discord.app_commands'] = mock.MagicMock()

    from skyblock.client import hypixel_client

    try:
        # Test the API call that the keep-alive would make
        test_uuid = "47fb7b99858042c3a7b4795af44ea41d"
        print(f"Testing Hypixel API with UUID: {test_uuid}")

        profile = await hypixel_client.get_active_profile(test_uuid)

        if profile:
            print(f"✅ API call successful - Profile: {profile.get('cute_name', 'Unknown')}")
        else:
            print("⚠️  API call completed but no profile returned")

        await hypixel_client.close()

        print("\n✅ HYPIXEL KEEP-ALIVE TEST PASSED")
        return True

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        await hypixel_client.close()
        return False


async def run_all_tests():
    """Run all scheduler tests."""
    print("\n" + "="*70)
    print("DAILY SCHEDULER TESTS")
    print("="*70)

    try:
        result1 = await test_daily_scheduler()
        result2 = await test_hypixel_keepalive_function()

        if result1 and result2:
            print("\n" + "="*70)
            print("✅ ALL SCHEDULER TESTS PASSED!")
            print("="*70)
            return True
        else:
            print("\n" + "="*70)
            print("❌ SOME TESTS FAILED")
            print("="*70)
            return False

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)
