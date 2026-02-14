# Contributing Guidelines

This document outlines best practices for contributing to this project.

## File Structure

### Organization Principles

1. **Keep root directory clean** - Only essential files in project root
2. **Group by purpose** - Related files go in subdirectories
3. **No scattered test files** - All tests in `tests/` directory
4. **Documentation at root** - User-facing docs stay in root for visibility

### Current Structure

```
disclaude/
├── bot.py                          # Main bot entry point
├── config.py                       # Configuration management
├── database.py                     # Database models and setup
├── hypixel_client.py              # Hypixel API client
├── skyblock_analyzer.py           # Skyblock stats analysis
├── user_profiles.py               # User profile management
├── personality.py                 # Personality tracking system
├── scheduler.py                   # Reminder scheduling
├── time_parser.py                 # Natural language time parsing
├── requirements.txt               # Python dependencies
├── .env.local                     # Local secrets (gitignored)
├── .gitignore                     # Git ignore rules
│
├── README.md                      # Main project documentation
├── DEPLOYMENT.md                  # Deployment guide
├── DATABASE_SETUP.md              # Database setup (general)
├── RAILWAY_DATABASE_SETUP.md      # Railway-specific DB setup
├── PERSONALITY.md                 # Personality system docs
├── SKYBLOCK.md                    # Skyblock integration docs
├── REMINDERS.md                   # Reminder system docs
│
├── tests/                         # All test files
│   ├── README.md                  # Test documentation
│   ├── test_api_simple.py         # Main API tests
│   ├── test_api_direct.py         # Async API tests
│   ├── test_hypixel_api.py        # Pytest suite
│   ├── test_config.py             # Config tests
│   ├── test_bot_utils.py          # Utility tests
│   └── diagnostics/               # Diagnostic/debug tests
│       └── ...
│
└── check_database.py              # Database diagnostic tool
```

## File Naming Conventions

### Python Files

- **Modules**: `snake_case.py` (e.g., `hypixel_client.py`)
- **Tests**: `test_*.py` (e.g., `test_api_simple.py`)
- **Utilities**: `check_*.py` or descriptive name (e.g., `check_database.py`)

### Documentation

- **User guides**: `UPPERCASE.md` (e.g., `DATABASE_SETUP.md`)
- **Code docs**: `README.md` in subdirectories
- **Contributing**: `CONTRIBUTING.md` (this file)

### Configuration

- **Environment**: `.env.local` (local), `.env` (template)
- **Ignore**: `.gitignore`
- **Dependencies**: `requirements.txt`

## Git Workflow

### Before Committing

1. **Check status**
   ```bash
   git status
   ```

2. **Review changes**
   ```bash
   git diff
   ```

3. **Stage specific files** (avoid `git add .` or `git add -A`)
   ```bash
   git add file1.py file2.py
   ```

### Commit Message Format

```
Short summary (50 chars or less)

Longer description explaining:
- What changed
- Why it changed
- Any notable technical details

Files affected:
- file1.py: Brief description of changes
- file2.py: Brief description of changes

Results/Impact:
✅ What works now
✅ What's improved
⚠️ Known issues (if any)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
```

**Example:**
```bash
git commit -m "$(cat <<'EOF'
Reorganize test files into proper structure

Moved all test files from project root to tests/ directory for better
organization and maintainability.

Files moved:
- test_api_simple.py → tests/test_api_simple.py
- test_api_direct.py → tests/test_api_direct.py
- Diagnostic tests → tests/diagnostics/

Benefits:
✅ Cleaner project root
✅ Tests logically organized
✅ Easier to find and run tests

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

### Pushing Changes

1. **Always verify before pushing**
   ```bash
   git log -1  # Check last commit
   git diff origin/main  # Check what will be pushed
   ```

2. **Push**
   ```bash
   git push
   ```

3. **Verify on GitHub** - Check that changes appear correctly

## Creating New Files

### Checklist

- [ ] File is in the correct directory
- [ ] File follows naming conventions
- [ ] File includes docstring/header comment
- [ ] File is added to `.gitignore` if it contains secrets/data
- [ ] Related documentation updated
- [ ] README updated if user-facing

### Code File Template

```python
"""Brief description of what this module does.

Detailed explanation if needed.
"""
import os
import sys

# Your code here


if __name__ == "__main__":
    # Entry point if applicable
    pass
```

### Test File Template

```python
"""Tests for [module_name].

Description of what is being tested.
"""
import pytest  # or standard library
from module_name import function_to_test


def test_something():
    """Test that something works correctly."""
    result = function_to_test()
    assert result == expected_value


if __name__ == "__main__":
    # Run tests directly
    test_something()
    print("✅ All tests passed")
```

### Documentation Template

```markdown
# Title

Brief introduction (1-2 sentences).

## Quick Start

Most common use case with minimal steps.

## Detailed Guide

Step-by-step instructions.

## Troubleshooting

Common issues and solutions.

---

**Related:** Link to related docs
```

## Code Organization

### Module Structure

1. **Imports** - Group by: stdlib, third-party, local
2. **Constants** - UPPERCASE_WITH_UNDERSCORES
3. **Classes** - PascalCase
4. **Functions** - snake_case
5. **Main execution** - `if __name__ == "__main__":`

### Example

```python
"""Module docstring."""
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import discord
from sqlalchemy import create_engine

# Local
from config import DISCORD_TOKEN
from database import SessionLocal

# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Classes
class MyClass:
    """Class docstring."""

    def __init__(self):
        """Initialize."""
        pass

# Functions
def my_function():
    """Function docstring."""
    pass

# Main execution
if __name__ == "__main__":
    my_function()
```

## Documentation Standards

### When to Create Documentation

- **New major feature** → Create `FEATURE_NAME.md`
- **Setup/deployment change** → Update existing deployment docs
- **API change** → Update code comments and relevant docs
- **Bug fix** → Add to troubleshooting section if notable

### Documentation Locations

| Type | Location | Example |
|------|----------|---------|
| Setup guides | Root | `DEPLOYMENT.md` |
| Feature docs | Root | `SKYBLOCK.md` |
| Test docs | `tests/README.md` | Test instructions |
| Code docs | Inline docstrings | Function/class docs |
| API docs | Inline comments | Complex logic |

## Testing Standards

### Test Organization

```
tests/
├── test_api_*.py           # API integration tests
├── test_[module].py        # Unit tests for modules
├── diagnostics/            # Debugging/investigative tests
└── README.md               # Test documentation
```

### Test File Requirements

- [ ] Descriptive name (`test_*.py`)
- [ ] Docstring explaining what's tested
- [ ] Can run standalone (no pytest required for main tests)
- [ ] Loads `.env.local` if needed
- [ ] Provides clear pass/fail output
- [ ] Documented in `tests/README.md`

### Running Tests

Tests should be runnable from project root:
```bash
python tests/test_api_simple.py
```

## Security Best Practices

### Environment Variables

- **Never commit** `.env` or `.env.local`
- **Always use** `os.getenv()` for secrets
- **Validate** required env vars in `config.py`
- **Document** all required env vars in setup docs

### .gitignore

Keep updated with:
```
# Environment variables
.env
.env.local

# User data
*.db
user_profiles.json

# Python
__pycache__/
*.pyc

# IDE
.vscode/
.idea/

# Claude
.claude/
```

## Pull Request Checklist

Before creating a PR (or pushing to main):

- [ ] Code follows project structure
- [ ] Files in correct directories
- [ ] Tests pass (if applicable)
- [ ] Documentation updated
- [ ] Commit message is descriptive
- [ ] No secrets or credentials committed
- [ ] `.gitignore` updated if needed
- [ ] README.md updated if user-facing changes

## Common Commands

### Project Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Development Workflow
```bash
# Check what changed
git status
git diff

# Stage changes
git add file1.py file2.py

# Commit with message
git commit -m "Descriptive message"

# Push to GitHub
git push

# Run tests
python tests/test_api_simple.py
```

### File Management
```bash
# Move file (preserve git history)
git mv old_location new_location

# Remove file
git rm filename

# Check file structure
tree .  # or
find . -type f | sort
```

## Notes

- **Consistency matters** - Follow existing patterns
- **Clean commits** - Each commit should be logical and complete
- **Test before pushing** - Verify changes work
- **Document as you go** - Update docs with code changes
- **Ask before major refactors** - Discuss significant changes

---

**Last Updated:** 2026-02-14

**Questions?** Check existing files for examples or ask!
