"""Test deploy notification functionality."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_deploy_notification_exists():
    """Test that deploy notification function exists."""
    print("\n" + "="*70)
    print("TEST: Deploy Notification Function")
    print("="*70)

    with open('bot.py', 'r') as f:
        bot_content = f.read()

    # Check for deploy notification function
    assert "async def send_deploy_notification" in bot_content, \
        "bot.py should have send_deploy_notification function"
    print("✅ bot.py has send_deploy_notification function")

    # Check that it's called in on_ready
    assert "await send_deploy_notification()" in bot_content, \
        "bot.py should call send_deploy_notification in on_ready"
    print("✅ send_deploy_notification is called in on_ready")

    # Check that it uses DISCORD_OWNER_ID
    assert "config.DISCORD_OWNER_ID" in bot_content, \
        "bot.py should use config.DISCORD_OWNER_ID"
    print("✅ Uses config.DISCORD_OWNER_ID for notifications")

    # Check that it sends Skyblock stats
    assert "skill_analysis = skyblock_analyzer.analyze_skills" in bot_content, \
        "Deploy notification should analyze skills"
    print("✅ Analyzes and sends Skyblock stats")

    print("\n✅ DEPLOY NOTIFICATION TEST PASSED")
    return True


def test_owner_id_config():
    """Test that owner ID is in config."""
    print("\n" + "="*70)
    print("TEST: Owner ID Configuration")
    print("="*70)

    with open('config.py', 'r') as f:
        config_content = f.read()

    # Check for DISCORD_OWNER_ID
    assert "DISCORD_OWNER_ID" in config_content, \
        "config.py should have DISCORD_OWNER_ID"
    print("✅ config.py has DISCORD_OWNER_ID configuration")

    # Check that it's read from environment
    assert 'os.getenv("DISCORD_OWNER_ID"' in config_content, \
        "DISCORD_OWNER_ID should be read from environment"
    print("✅ DISCORD_OWNER_ID is read from environment variables")

    # Check .env.local has the variable
    with open('.env.local', 'r') as f:
        env_content = f.read()

    assert "DISCORD_OWNER_ID" in env_content, \
        ".env.local should have DISCORD_OWNER_ID"
    print("✅ .env.local has DISCORD_OWNER_ID variable")

    print("\n✅ OWNER ID CONFIG TEST PASSED")
    return True


def test_deploy_notification_features():
    """Test specific features of deploy notification."""
    print("\n" + "="*70)
    print("TEST: Deploy Notification Features")
    print("="*70)

    with open('bot.py', 'r') as f:
        bot_content = f.read()

    # Check that it handles no linked account
    assert "user_profiles.is_linked" in bot_content, \
        "Should check if user has linked account"
    print("✅ Checks if user has linked Minecraft account")

    # Check that it displays purse and bank
    in_deploy_func = False
    has_purse = False
    has_bank = False

    for line in bot_content.split('\n'):
        if 'async def send_deploy_notification' in line:
            in_deploy_func = True
        elif in_deploy_func and 'async def' in line and 'send_deploy_notification' not in line:
            in_deploy_func = False

        if in_deploy_func:
            if 'currencies' in line and 'coin_purse' in line:
                has_purse = True
            if 'banking' in line and 'balance' in line:
                has_bank = True

    assert has_purse, "Deploy notification should display purse"
    print("✅ Displays purse in notification")

    assert has_bank, "Deploy notification should display bank"
    print("✅ Displays bank in notification")

    # Check for error handling
    assert "except discord.Forbidden" in bot_content or "except Exception" in bot_content, \
        "Should handle DM errors gracefully"
    print("✅ Handles DM errors (Forbidden, etc.)")

    print("\n✅ DEPLOY NOTIFICATION FEATURES TEST PASSED")
    return True


def run_all_tests():
    """Run all deploy notification tests."""
    print("\n" + "="*70)
    print("DEPLOY NOTIFICATION TESTS")
    print("="*70)

    try:
        test_deploy_notification_exists()
        test_owner_id_config()
        test_deploy_notification_features()

        print("\n" + "="*70)
        print("✅ ALL DEPLOY NOTIFICATION TESTS PASSED!")
        print("="*70)
        print("\nDeploy notification features verified:")
        print("  ✅ Sends Skyblock stats on deployment")
        print("  ✅ Uses DISCORD_OWNER_ID from config")
        print("  ✅ Displays purse and bank balance")
        print("  ✅ Handles errors gracefully")
        print("\n💡 Remember to set your DISCORD_OWNER_ID in .env.local!")
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
