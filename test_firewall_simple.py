# Copyright Modal Labs 2025
#!/usr/bin/env python3
"""Standalone test for rffickle integration in Modal's serialization."""

import io
import os
import pickle
import sys
from unittest.mock import Mock


def test_basic_firewall():
    """Test basic firewall functionality without full Modal setup."""
    print("Testing basic rffickle integration...")
    
    # Test that rffickle is available
    try:
        from fickle import DefaultFirewall
        print("✅ rffickle is installed")
    except ImportError:
        print("❌ rffickle is not installed")
        return False
    
    # Test that firewall blocks exploits
    firewall = DefaultFirewall()
    
    class Exploit:
        def __reduce__(self):
            return (os.system, ('echo "EXPLOITED"',))
    
    exploit_pickle = pickle.dumps(Exploit())
    
    try:
        result = firewall.loads(exploit_pickle)
        print("❌ Exploit was not blocked by rffickle!")
        return False
    except Exception as e:
        print(f"✅ Exploit blocked by rffickle: {type(e).__name__}")
    
    # Test that safe data works
    safe_data = {"value": 42, "list": [1, 2, 3], "text": "Hello"}
    safe_pickle = pickle.dumps(safe_data)
    
    try:
        result = firewall.loads(safe_pickle)
        if result == safe_data:
            print("✅ Safe data deserialization works")
        else:
            print("❌ Safe data was corrupted")
            return False
    except Exception as e:
        print(f"❌ Safe data failed: {e}")
        return False
    
    return True


def test_modal_serialization_with_mock():
    """Test the Modal serialization with minimal mocking."""
    print("\nTesting Modal serialization code...")
    
    # Set the environment variable
    os.environ["MODAL_USE_FIREWALL"] = "true"
    
    # We need to mock some Modal imports
    import sys
    from unittest.mock import MagicMock
    
    # Mock modal_proto
    sys.modules['modal_proto'] = MagicMock()
    sys.modules['modal_proto'].api_pb2 = MagicMock()
    
    # Mock other Modal internal modules
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
    
    # Mock is_local to return True (client-side)
    sys.modules['modal._runtime.execution_context'].is_local = MagicMock(return_value=True)
    
    # Now import our modified serialization module
    from modal._serialization import deserialize
    
    # Test with an exploit
    class Exploit:
        def __reduce__(self):
            return (os.system, ('echo "EXPLOITED"',))
    
    exploit_pickle = pickle.dumps(Exploit())
    
    try:
        result = deserialize(exploit_pickle, None)
        print("❌ Exploit was not blocked in Modal deserialization!")
        return False
    except Exception as e:
        print(f"✅ Exploit blocked in Modal: {type(e).__name__}")
    
    # Test with safe data
    safe_data = {"result": 42}
    safe_pickle = pickle.dumps(safe_data)
    
    try:
        result = deserialize(safe_pickle, None)
        if result == safe_data:
            print("✅ Safe data works in Modal deserialization")
        else:
            print("❌ Safe data was corrupted in Modal")
            return False
    except Exception as e:
        print(f"❌ Safe data failed in Modal: {e}")
        return False
    
    # Test with firewall disabled
    os.environ["MODAL_USE_FIREWALL"] = "false"
    
    # Safe data should still work
    try:
        result = deserialize(safe_pickle, None)
        if result == safe_data:
            print("✅ Modal deserialization works with firewall disabled")
        else:
            print("❌ Data corrupted with firewall disabled")
            return False
    except Exception as e:
        print(f"❌ Failed with firewall disabled: {e}")
        return False
    
    return True


def main():
    print("rffickle Integration Test for Modal")
    print("=" * 50)
    
    tests = [
        test_basic_firewall,
        test_modal_serialization_with_mock
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("\nrffickle is successfully integrated!")
        print("Use MODAL_USE_FIREWALL=true to enable safe deserialization.")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
