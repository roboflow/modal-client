# Roboflow Modal Client Fork v1.2.6

## Summary
This release fixes a critical security vulnerability where the firewall flag was not properly propagated to lazy-loaded (non-hydrated) class methods, allowing pickle deserialization exploits to succeed on the first execution after server startup.

## Critical Security Fix

### Firewall Flag Propagation for Non-Hydrated Class Methods
- **Issue**: When using `modal.Cls.from_name(..., use_firewall=True)`, the firewall flag was not being propagated to methods accessed on non-hydrated class instances (typical state on first access)
- **Security Impact**: This allowed pickle deserialization exploits to bypass the firewall on the FIRST execution after server startup
- **Fix**: Modified `_Obj.__getattr__` in `modal/cls.py` to properly copy the `_use_firewall` flag to lazy-loaded method functions

## Technical Details

The fix ensures that even when accessing methods on non-hydrated class instances (common with `Cls.from_name()`), the firewall protection is active:

```python
# This now properly protects against exploits even on first execution:
cls = modal.Cls.from_name("app-name", "ClassName", use_firewall=True)
instance = cls(workspace_id="workspace")
result = instance.execute_block.remote(...)  # Firewall active from first call
```

### Root Cause
- When a class is loaded via `Cls.from_name()`, it starts in a non-hydrated state
- Method access through `__getattr__` creates lazy-loaded functions
- Previously, these lazy-loaded functions didn't inherit the `_use_firewall` flag
- This meant the first execution (before hydration) was vulnerable

### The Fix
Modified the lazy loader creation in `_Obj.__getattr__` to copy the firewall flag from the class service function to the method function, ensuring protection is active even before hydration.

## Files Changed
- `modal/cls.py` - Modified `_Obj.__getattr__` to propagate `_use_firewall` flag to lazy-loaded methods

## How to Deploy to PyPI

1. Build the package:
```bash
./build_for_pypi.sh
```

2. Upload to PyPI:
```bash
python -m twine upload dist/*
```

## Testing
Critical tests to verify the fix:
- Test with `modal.Cls.from_name()` using `use_firewall=True` 
- Verify firewall blocks exploits on FIRST execution after server startup
- Confirm no regression for hydrated class instances
- Test with both parameterized and non-parameterized classes

## Version History
- v1.2.6 - Fixed critical firewall bypass for non-hydrated class methods (first execution vulnerability)
- v1.2.5 - Fixed firewall flag propagation for parameterized classes
- v1.2.4 - Fixed import issues
- v1.2.3 - Fixed grpclib/grpcio incompatibility
- v1.2.2 - Added grpcio dependency
- v1.2.1 - Fixed PyPI package build
