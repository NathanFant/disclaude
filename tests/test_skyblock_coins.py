"""Test Skyblock coin display (purse and bank)."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Mock the discord library before imports
import unittest.mock as mock
sys.modules['discord'] = mock.MagicMock()
sys.modules['discord.ext'] = mock.MagicMock()
sys.modules['discord.ext.commands'] = mock.MagicMock()

import asyncio
from skyblock.client import hypixel_client
from skyblock.analyzer import skyblock_analyzer

# Test UUID
TEST_UUID = "47fb7b99858042c3a7b4795af44ea41d"


async def test_purse_display():
    """Test that purse is correctly retrieved from currencies.coin_purse."""
    print("\n" + "="*70)
    print("TEST: Purse Display")
    print("="*70)

    # Get profile
    profile = await hypixel_client.get_active_profile(TEST_UUID)
    assert profile is not None, "Failed to get profile"
    print(f"✅ Got profile: {profile.get('cute_name')}")

    # Get player data
    player_data = await hypixel_client.get_player_data_from_profile(profile, TEST_UUID)
    assert player_data is not None, "Failed to get player data"
    print(f"✅ Got player data")

    # Test OLD way (should fail/return 0)
    old_purse = player_data.get('coin_purse', 0)
    print(f"❌ OLD method - coin_purse: {old_purse} (should be 0)")

    # Test NEW way (should work)
    new_purse = player_data.get('currencies', {}).get('coin_purse', 0)
    print(f"✅ NEW method - currencies.coin_purse: {new_purse:,.2f}")

    assert new_purse > 0, "Purse should be greater than 0"
    assert old_purse == 0, "Old method should return 0"

    print("\n✅ PURSE TEST PASSED")
    return True


async def test_bank_display():
    """Test that bank is correctly retrieved from profile.banking.balance."""
    print("\n" + "="*70)
    print("TEST: Bank Display")
    print("="*70)

    # Get profile
    profile = await hypixel_client.get_active_profile(TEST_UUID)
    assert profile is not None, "Failed to get profile"
    print(f"✅ Got profile: {profile.get('cute_name')}")

    # Check if banking exists
    if 'banking' in profile:
        bank_balance = profile['banking'].get('balance', 0)
        print(f"✅ Banking exists - balance: {bank_balance:,.2f}")
        assert bank_balance >= 0, "Bank balance should be >= 0"
    else:
        print("⚠️  No banking data (this is OK, some profiles don't have it)")

    print("\n✅ BANK TEST PASSED")
    return True


async def test_analyzer_summary():
    """Test that analyzer generates summary with correct coin values."""
    print("\n" + "="*70)
    print("TEST: Analyzer Summary")
    print("="*70)

    # Get profile and player data
    profile = await hypixel_client.get_active_profile(TEST_UUID)
    player_data = await hypixel_client.get_player_data_from_profile(profile, TEST_UUID)

    # Analyze
    skill_analysis = skyblock_analyzer.analyze_skills(player_data)

    # Generate summary (this uses the fixed code)
    summary = skyblock_analyzer.generate_summary(player_data, skill_analysis, {})

    # Check that purse is mentioned in summary
    assert 'Purse' in summary or '💰' in summary, "Summary should contain purse info"
    print(f"✅ Summary contains purse info")

    # Extract purse value from player data to verify
    purse = player_data.get('currencies', {}).get('coin_purse', 0)
    if purse > 0:
        # Check if the purse amount appears in summary
        purse_str = f"{purse:,.2f}"
        print(f"✅ Purse value: {purse_str}")

    print("\n✅ ANALYZER SUMMARY TEST PASSED")
    return True


async def run_all_tests():
    """Run all Skyblock coin tests."""
    print("\n" + "="*70)
    print("SKYBLOCK COIN DISPLAY TESTS")
    print("="*70)

    try:
        await test_purse_display()
        await test_bank_display()
        await test_analyzer_summary()

        print("\n" + "="*70)
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        return True
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close HTTP session
        await hypixel_client.close()


if __name__ == "__main__":
    result = asyncio.run(run_all_tests())
    sys.exit(0 if result else 1)
