# Copyright Modal Labs 2025
#!/usr/bin/env python3
"""Direct test of the modified serialization module."""

import io
import os
import pickle
import sys
from unittest.mock import MagicMock, Mock


def test_serialization_directly():
    """Test the serialization module directly."""
    print("Testing Modal serialization modifications...")
    
    # Mock the necessary imports
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
    
    # Add cloudpickle.Pickler
    import pickle as standard_pickle
    cloudpickle_mock = MagicMock()
    cloudpickle_mock.Pickler = standard_pickle.Pickler
    sys.modules['modal._vendor.cloudpickle'] = cloudpickle_mock
    
    # Mock logger
    logger_mock = MagicMock()
    sys.modules['modal.config'].logger = logger_mock
    
    # Now import just the serialization module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "modal._serialization", 
        "/Users/yeldarb/Code/modal-client/modal/_serialization.py"
    )
    serialization = importlib.util.module_from_spec(spec)
    
    # Set up the execution context mock
    sys.modules['modal._runtime.execution_context'].is_local = MagicMock(return_value=True)
    
    # Execute the module
    spec.loader.exec_module(serialization)
    
    # Test 1: With firewall enabled
    print("\n1. Testing with firewall enabled...")
    
    # Test blocking exploit
    class Exploit:
        def __reduce__(self):
            return (os.system, ('echo "EXPLOITED"',))
    
    exploit_pickle = pickle.dumps(Exploit())
    
    try:
        result = serialization.deserialize(exploit_pickle, None, use_firewall=True)
        print("❌ Exploit was not blocked!")
        return False
    except Exception as e:
        print(f"✅ Exploit blocked with firewall: {type(e).__name__}")
    
    # Test safe data with firewall
    safe_data = {"value": 42, "list": [1, 2, 3]}
    safe_pickle = pickle.dumps(safe_data)
    
    try:
        result = serialization.deserialize(safe_pickle, None, use_firewall=True)
        if result == safe_data:
            print("✅ Safe data works with firewall enabled")
        else:
            print("❌ Safe data corrupted with firewall")
            return False
    except Exception as e:
        print(f"❌ Safe data failed: {e}")
        return False
    
    # Test 2: With firewall disabled (default)
    print("\n2. Testing without firewall (default behavior)...")
    
    try:
        result = serialization.deserialize(safe_pickle, None, use_firewall=False)
        if result == safe_data:
            print("✅ Deserialization works with firewall disabled")
        else:
            print("❌ Data corrupted with firewall disabled")
            return False
    except Exception as e:
        print(f"❌ Failed with firewall disabled: {e}")
        return False
    
    # Test 3: Server-side (should not use firewall even if enabled)
    print("\n3. Testing server-side (should not use firewall)...")
    sys.modules['modal._runtime.execution_context'].is_local = MagicMock(return_value=False)
    
    try:
        result = serialization.deserialize(safe_pickle, None, use_firewall=True)
        if result == safe_data:
            print("✅ Server-side deserialization unaffected by firewall setting")
        else:
            print("❌ Server-side data corrupted")
            return False
    except Exception as e:
        print(f"❌ Server-side failed: {e}")
        return False
    
    return True


def main():
    print("Modal Serialization Firewall Test")
    print("=" * 50)
    
    try:
        success = test_serialization_directly()
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nModal fork successfully integrated with rffickle!")
        print("Use use_firewall=True parameter on functions to enable safe deserialization.")
        return 0
    else:
        print("❌ TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
