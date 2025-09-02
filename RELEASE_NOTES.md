# Roboflow Modal Client Fork v1.2.5

## Summary
This release fixes a critical bug in the firewall flag propagation for parameterized Modal classes, ensuring secure deserialization works correctly when using `modal.Cls.from_name()` with the `use_firewall=True` parameter.

## Bug Fix

### Firewall Flag Propagation for Parameterized Classes
- **Issue**: When using `modal.Cls.from_name(..., use_firewall=True)` with parameterized classes, the firewall flag was not being propagated to instance methods
- **Impact**: This prevented proper secure deserialization with `rffickle` when executing untrusted code in Modal sandboxes
- **Fix**: Added firewall flag propagation in `_bind_instance_method` function in `modal/cls.py`

## Technical Details

The fix ensures that when you use the following pattern:
```python
cls = modal.Cls.from_name("app-name", "ClassName", use_firewall=True)
instance = cls(param1="value1", param2="value2")
result = instance.some_method.remote(...)  # Now correctly uses firewall
```

The `use_firewall` flag is properly inherited by the method, ensuring secure deserialization throughout the execution chain.

## Files Changed
- `modal/cls.py` - Added `_use_firewall` flag propagation in `_bind_instance_method`

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
Ensure that parameterized classes with firewall enabled properly block pickle-based attacks:
- Test with `modal.Cls.from_name()` using `use_firewall=True`
- Verify that instance methods inherit the firewall setting
- Confirm that pickle deserialization attacks are blocked

## Version History
- v1.2.5 - Fixed firewall flag propagation for parameterized classes
- v1.2.4 - Fixed import issues
- v1.2.3 - Fixed grpclib/grpcio incompatibility
- v1.2.2 - Added grpcio dependency
- v1.2.1 - Fixed PyPI package build
- v1.2.0 - Initial Roboflow fork with rffickle integration
