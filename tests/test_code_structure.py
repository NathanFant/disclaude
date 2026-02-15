"""Test code structure without requiring dependencies."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_purse_path_fix():
    """Test that purse code uses correct path."""
    print("\n" + "="*70)
    print("TEST: Purse Path Fix in Code")
    print("="*70)

    # Read bot.py and check for correct purse path
    with open('bot.py', 'r') as f:
        bot_content = f.read()

    # Check that we're using the new path
    assert "get('currencies', {}).get('coin_purse'" in bot_content, \
        "bot.py should use currencies.coin_purse"
    print("✅ bot.py uses correct purse path: currencies.coin_purse")

    # Check we're not using old path
    assert "player_data.get('coin_purse', 0)" not in bot_content, \
        "bot.py should not use old coin_purse path"
    print("✅ bot.py does not use old purse path")

    # Read analyzer.py
    with open('skyblock/analyzer.py', 'r') as f:
        analyzer_content = f.read()

    # Check analyzer uses new path
    assert "get('currencies', {}).get('coin_purse'" in analyzer_content, \
        "analyzer.py should use currencies.coin_purse"
    print("✅ analyzer.py uses correct purse path: currencies.coin_purse")

    # Read agent/tools.py
    with open('agent/tools.py', 'r') as f:
        tools_content = f.read()

    # Check tools uses new path
    assert "get('currencies', {}).get('coin_purse'" in tools_content, \
        "tools.py should use currencies.coin_purse"
    print("✅ agent/tools.py uses correct purse path: currencies.coin_purse")

    print("\n✅ PURSE PATH FIX TEST PASSED")
    return True


def test_bank_display_added():
    """Test that bank display was added to bot.py."""
    print("\n" + "="*70)
    print("TEST: Bank Display Added")
    print("="*70)

    with open('bot.py', 'r') as f:
        bot_content = f.read()

    # Check for bank display code
    assert "'banking' in profile" in bot_content, \
        "bot.py should check for banking in profile"
    print("✅ bot.py checks for banking data")

    assert "Bank:" in bot_content or "🏦" in bot_content, \
        "bot.py should display bank balance"
    print("✅ bot.py displays bank balance")

    # Check that we're accessing bank from profile, not player_data
    assert "profile['banking']" in bot_content or "profile.get('banking'" in bot_content, \
        "bot.py should get bank from profile level"
    print("✅ bot.py accesses bank from profile level")

    # Check agent/tools.py for bank
    with open('agent/tools.py', 'r') as f:
        tools_content = f.read()

    assert '"bank"' in tools_content or "'bank'" in tools_content, \
        "tools.py should include bank in result"
    print("✅ agent/tools.py includes bank in result")

    print("\n✅ BANK DISPLAY TEST PASSED")
    return True


def test_scheduler_daily_task():
    """Test that scheduler has daily task method."""
    print("\n" + "="*70)
    print("TEST: Scheduler Daily Task Method")
    print("="*70)

    with open('core/scheduler.py', 'r') as f:
        scheduler_content = f.read()

    # Check for CronTrigger import
    assert "from apscheduler.triggers.cron import CronTrigger" in scheduler_content, \
        "scheduler.py should import CronTrigger"
    print("✅ scheduler.py imports CronTrigger")

    # Check for schedule_daily_task method
    assert "def schedule_daily_task" in scheduler_content, \
        "scheduler.py should have schedule_daily_task method"
    print("✅ scheduler.py has schedule_daily_task method")

    # Check that it uses CronTrigger
    assert "CronTrigger(hour=" in scheduler_content, \
        "schedule_daily_task should use CronTrigger"
    print("✅ schedule_daily_task uses CronTrigger")

    print("\n✅ SCHEDULER DAILY TASK TEST PASSED")
    return True


def test_hypixel_keepalive_scheduled():
    """Test that Hypixel keep-alive is scheduled in bot.py."""
    print("\n" + "="*70)
    print("TEST: Hypixel Keep-Alive Scheduled")
    print("="*70)

    with open('bot.py', 'r') as f:
        bot_content = f.read()

    # Check for keep-alive function
    assert "async def keep_hypixel_api_alive" in bot_content, \
        "bot.py should have keep_hypixel_api_alive function"
    print("✅ bot.py has keep_hypixel_api_alive function")

    # Check that it's scheduled
    assert "schedule_daily_task" in bot_content, \
        "bot.py should call schedule_daily_task"
    print("✅ bot.py calls schedule_daily_task")

    assert "hypixel_api_keepalive" in bot_content, \
        "bot.py should schedule hypixel_api_keepalive task"
    print("✅ bot.py schedules hypixel_api_keepalive task")

    # Check that it's scheduled at 8pm
    assert "hour=20" in bot_content, \
        "Keep-alive should be scheduled at hour 20 (8pm)"
    print("✅ Keep-alive scheduled at 8pm (hour=20)")

    print("\n✅ HYPIXEL KEEP-ALIVE SCHEDULED TEST PASSED")
    return True


def run_all_tests():
    """Run all code structure tests."""
    print("\n" + "="*70)
    print("CODE STRUCTURE TESTS")
    print("="*70)

    try:
        test_purse_path_fix()
        test_bank_display_added()
        test_scheduler_daily_task()
        test_hypixel_keepalive_scheduled()

        print("\n" + "="*70)
        print("✅ ALL CODE STRUCTURE TESTS PASSED!")
        print("="*70)
        print("\nAll changes have been verified:")
        print("  ✅ Purse uses correct path (currencies.coin_purse)")
        print("  ✅ Bank display added (profile.banking.balance)")
        print("  ✅ Daily scheduler method added")
        print("  ✅ Hypixel API keep-alive scheduled at 8pm daily")
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = run_all_tests()
    sys.exit(0 if result else 1)
