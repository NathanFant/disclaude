# API Tests

Comprehensive test suite for validating Hypixel and Mojang API integration.

## Quick Start

```bash
# Run from project root
python tests/test_api_simple.py
```

## Test Structure

```
tests/
├── README.md                    # This file
├── test_api_simple.py          # ⭐ Main test suite (no dependencies)
├── test_api_direct.py          # Async tests (requires aiohttp)
├── test_hypixel_api.py         # Pytest suite (requires pytest)
├── test_config.py              # Config validation tests
├── test_bot_utils.py           # Bot utility tests
└── diagnostics/                # Diagnostic tests (archived)
    ├── test_profile_structure.py
    ├── test_profile_timestamps.py
    ├── test_profile_selection.py
    └── test_active_profile_fix.py
```

## Main Tests

### `test_api_simple.py` ⭐ **Recommended**
Standalone test using Python's standard library. No dependencies required.

**What it tests:**
1. ✅ **Mojang API** - Get UUID from username
2. ✅ **Hypixel Skyblock Profiles API** - Get profiles using UUID
3. ✅ **UUID Format Compatibility** - Test both dashed and non-dashed UUIDs

**Features:**
- Loads secrets from `.env.local` if available
- Falls back to dummy tokens for local testing
- Validates 200 responses for all endpoints

### `test_api_direct.py`
Comprehensive async tests using aiohttp (requires `pip install aiohttp`).

### `test_hypixel_api.py`
Pytest-based tests (requires `pip install pytest aiohttp`).

### `test_config.py` & `test_bot_utils.py`
Unit tests for bot configuration and utilities.

## Diagnostic Tests

The `diagnostics/` folder contains tests used to investigate and fix the active profile detection issue. These are archived for reference but not needed for regular testing.

## Running Tests

### Locally (Limited - No API Key)

```bash
# From project root
python tests/test_api_simple.py
```

**Expected output:**
- ✅ Test 1 (Mojang API) will pass
- ⚠️ Tests 2-3 will skip (no HYPIXEL_API_KEY)

### With API Key (.env.local)

1. Create `.env.local` in project root with your API keys
2. Run tests:

```bash
python tests/test_api_simple.py
```

### On Railway (Full Tests)

SSH into your Railway deployment:

```bash
python tests/test_api_simple.py
```

**Expected output:**
- ✅ All tests should pass with 200 status
- If "No Skyblock profiles found" - player hasn't played Skyblock (expected)
- If 403 error - API key is invalid
- If 429 error - Rate limited

## Test Cases

### Username Test Case
- **Username**: `NathanFant`
- **Expected UUID**: `47fb7b99858042c3a7b4795af44ea41d`

### UUID Test Case
- **UUID (no dashes)**: `47fb7b99858042c3a7b4795af44ea41d`
- **UUID (with dashes)**: `47fb7b99-8580-42c3-a7b4-795af44ea41d`

Both formats should work with Hypixel API.

## What Each Test Validates

### Test 1: Mojang API
```
GET https://api.mojang.com/users/profiles/minecraft/NathanFant
```
**Validates:**
- ✅ 200 response
- ✅ Correct UUID returned
- ✅ Username matches

### Test 2: Hypixel Skyblock Profiles
```
GET https://api.hypixel.net/v2/skyblock/profiles?key={API_KEY}&uuid={UUID}
```
**Validates:**
- ✅ 200 response
- ✅ `success: true` in response
- ✅ Profile structure is correct
- ✅ Player UUID found in profile members

### Test 3: UUID Format Compatibility
Tests the same endpoint with both UUID formats:
- `47fb7b99858042c3a7b4795af44ea41d` (no dashes)
- `47fb7b99-8580-42c3-a7b4-795af44ea41d` (with dashes)

**Validates:**
- ✅ Both formats return 200
- ✅ Both formats return `success: true`

## Common Issues

### 403 Forbidden
```
❌ HTTP ERROR: 403 - Forbidden
   API key is invalid or doesn't have permissions
```
**Solution:** Check `HYPIXEL_API_KEY` in Railway environment variables

### 429 Rate Limited
```
❌ HTTP ERROR: 429 - Too Many Requests
   Rate limited - too many requests
```
**Solution:** Wait a minute and try again

### No Profiles Found
```
⚠️ NO PROFILES FOUND
   This means the player hasn't played Hypixel Skyblock
```
**Not an error** - This is expected behavior if the player hasn't joined Hypixel Skyblock

## Expected Results for NathanFant

Based on the test run, we expect:

1. **Mojang API**: ✅ Returns UUID `47fb7b99858042c3a7b4795af44ea41d`
2. **Hypixel API**:
   - ✅ Returns 200 status
   - ✅ Returns `success: true`
   - Either finds Skyblock profiles OR correctly reports no profiles

## Integration with Bot

The bot uses these same API endpoints in `hypixel_client.py`:

- `get_uuid_from_username()` → Uses Mojang API
- `get_skyblock_profiles()` → Uses Hypixel Skyblock Profiles API
- `get_active_profile()` → Selects active profile using:
  1. Profile-level `selected` field (primary)
  2. Most recent `objectives.*.completed_at` timestamp (fallback)
  3. First available profile (last resort)

If these tests pass, the bot's API integration is working correctly.

## Test Results Summary

Based on tests with `NathanFant`:
- ✅ UUID: `47fb7b99858042c3a7b4795af44ea41d`
- ✅ 5 Skyblock profiles found
- ✅ Active profile: **Papaya** (selected: true)
- ✅ All endpoints return 200
