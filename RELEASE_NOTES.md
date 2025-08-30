# Roboflow Modal Client Fork v1.2.0

## Summary
This is a Roboflow fork of the Modal client that adds support for `rffickle` - a secure deserialization library for untrusted pickle files.

## Changes Made

### Version Update
- Bumped version from 1.1.4.dev23 to 1.2.0

### CI/CD Fixes
1. **Copyright headers**: Added `# Copyright Modal Labs 2025` to all test files
2. **Import ordering**: Fixed import order to follow standard (stdlib → third-party → local)
3. **Type annotations**: Fixed type checking issues by properly threading `use_firewall` parameter through invocation classes

### Feature Implementation
- Added `use_firewall` parameter to `@app.function()` and `@app.cls()` decorators
- Integrated `rffickle` for safe deserialization of untrusted pickled data
- Modified `_Invocation` and `_InputPlaneInvocation` classes to support firewall flag
- Updated `_process_result` to use firewall when enabled

## How to Deploy to PyPI

1. Build the package:
```bash
python -m build
```

2. Upload to PyPI:
```bash
python -m twine upload dist/*
```

## Testing
The test files demonstrate various aspects of the firewall functionality:
- `test_firewall.py` - Main firewall blocking tests
- `test_per_function_firewall.py` - Per-function configuration
- `test_no_fallback.py` - Ensures no unsafe fallback when rffickle unavailable
- `test_from_name_firewall.py` - Tests Cls.from_name() with firewall

## Security Note
When `use_firewall=True` is set, the client will use rffickle to safely deserialize pickled data, protecting against arbitrary code execution during deserialization.
