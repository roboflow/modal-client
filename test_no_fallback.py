# Copyright Modal Labs 2025
#!/usr/bin/env python3
"""Test that firewall properly fails when rffickle is not available."""

import pickle
import sys
from unittest.mock import MagicMock, patch


def test_no_fallback():
    """Test that there's no unsafe fallback when rffickle is unavailable."""
    print("Testing no unsafe fallback behavior...")
    
    # Mock all the Modal dependencies
    sys.modules['modal_proto'] = MagicMock()
    sys.modules['modal_proto'].api_pb2 = MagicMock()
    sys.modules['modal._utils'] = MagicMock()
    sys.modules['modal._utils.async_utils'] = MagicMock()
    sys.modules['modal._object'] = MagicMock()
    sys.modules['modal._type_manager'] = MagicMock()
    sys.modules['modal._vendor'] = MagicMock()
    sys.modules['modal._vendor.cloudpickle'] = MagicMock()
    sys.modules['modal.config'] = MagicMock()
    sys.modules['modal.exception'] = MagicMock()
    sys.modules['modal.object'] = MagicMock()
    sys.modules['modal._runtime'] = MagicMock()
    sys.modules['modal._runtime.execution_context'] = MagicMock()
    
    # Mock cloudpickle.Pickler
    import pickle as standard_pickle
    cloudpickle_mock = MagicMock()
    cloudpickle_mock.Pickler = standard_pickle.Pickler
    sys.modules['modal._vendor.cloudpickle'] = cloudpickle_mock
    
    # Import the serialization module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "modal._serialization", 
        "/Users/yeldarb/Code/modal-client/modal/_serialization.py"
    )
    serialization = importlib.util.module_from_spec(spec)
    sys.modules['modal._runtime.execution_context'].is_local = MagicMock(return_value=True)
    spec.loader.exec_module(serialization)
    
    # Test with firewall requested but rffickle unavailable
    print("\nTesting with use_firewall=True but rffickle unavailable...")
    
    safe_data = {"test": "data"}
    safe_pickle = pickle.dumps(safe_data)
    
    # Temporarily hide rffickle to simulate it not being installed
    import builtins
    original_import = builtins.__import__
    
    def mock_import(name, globals=None, locals=None, fromlist=(), level=0):
        if 'rffickle' in name:
            raise ModuleNotFoundError(f"No module named '{name}'")
        return original_import(name, globals, locals, fromlist, level)
    
    builtins.__import__ = mock_import
    
    try:
        result = serialization.deserialize(safe_pickle, None, use_firewall=True)
        print("❌ SECURITY BREACH: Unsafe fallback occurred!")
        print(f"Result: {result}")
        return False
    except (ImportError, ModuleNotFoundError) as e:
        if "rffickle" in str(e):
            print(f"✅ Properly failed with ImportError: {e}")
            return True
        else:
            print(f"❌ Unexpected ImportError: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return False
    finally:
        # Restore original import
        builtins.__import__ = original_import


def main():
    print("No Unsafe Fallback Test")
    print("=" * 50)
    
    try:
        success = test_no_fallback()
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ TEST PASSED")
        print("\nSecurity is maintained: No unsafe fallback when firewall is unavailable.")
        return 0
    else:
        print("❌ TEST FAILED")
        print("\nSecurity vulnerability: Unsafe fallback detected!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
