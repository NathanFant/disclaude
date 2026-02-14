# API Endpoint Tests

This directory contains tests to validate that the Hypixel and Mojang APIs are being called correctly.

## Test Files

### `test_api_simple.py` (Recommended)
Simple standalone test using Python's standard library. No dependencies required.

**What it tests:**
1. ✅ **Mojang API** - Get UUID from username (`NathanFant`)
2. ✅ **Hypixel Skyblock Profiles API** - Get profiles using UUID
3. ✅ **UUID Format Compatibility** - Test both dashed and non-dashed UUIDs

### `test_api_direct.py`
Comprehensive async tests using aiohttp (requires dependencies).

### `test_hypixel_api.py`
Pytest-based tests (requires pytest installed).

## Running Tests

### Locally (Limited - No API Key)

```bash
python test_api_simple.py
```

**Expected output:**
- ✅ Test 1 (Mojang API) will pass
- ⚠️ Tests 2-3 will skip (no HYPIXEL_API_KEY)

### On Railway (Full Tests)

1. SSH into your Railway deployment or add as a build step:

```bash
python test_api_simple.py
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
- `get_active_profile()` → Processes profiles to find most recent

If these tests pass, the bot's API integration is working correctly.
