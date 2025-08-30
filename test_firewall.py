# Copyright Modal Labs 2025
#!/usr/bin/env python3
"""Test script to verify rffickle integration with modal-client."""

import os
import pickle
import sys
from unittest.mock import Mock, patch


def test_firewall_blocks_exploit():
    """Test that pickle exploits are blocked when firewall is enabled."""
    print("Testing pickle exploit prevention with MODAL_USE_FIREWALL=true...")
    
    # Set environment variable to enable firewall
    os.environ["MODAL_USE_FIREWALL"] = "true"
    
    # Create an exploit that tries to execute code
    class Exploit:
        def __reduce__(self):
            return (os.system, ('echo "EXPLOITED"',))
    
    # Test with our Modal integration
    from modal._serialization import deserialize
    
    # Mock client
    mock_client = Mock()
    
    # Create malicious pickle
    exploit_pickle = pickle.dumps({"result": Exploit()})
    
    # Mock as if we're on client side (local)
    with patch('modal._runtime.execution_context.is_local', return_value=True):
        try:
            result = deserialize(exploit_pickle, mock_client)
            print("❌ SECURITY BREACH: Exploit was not blocked!")
            print(f"Result: {result}")
            return False
        except Exception as e:
            print(f"✅ Exploit blocked successfully: {type(e).__name__}: {e}")
            return True


def test_safe_data_works():
    """Test that safe data still deserializes correctly."""
    print("\nTesting safe data deserialization with firewall...")
    
    # Set environment variable to enable firewall
    os.environ["MODAL_USE_FIREWALL"] = "true"
    
    from modal._serialization import deserialize
    
    # Mock client
    mock_client = Mock()
    
    # Create safe data
    safe_data = {
        "result": {
            "value": 42,
            "list": [1, 2, 3],
            "nested": {"deep": {"data": "works"}},
            "text": "Hello, World!"
        }
    }
    
    safe_pickle = pickle.dumps(safe_data)
    
    # Mock as if we're on client side (local)
    with patch('modal._runtime.execution_context.is_local', return_value=True):
        try:
            result = deserialize(safe_pickle, mock_client)
            if result == safe_data:
                print("✅ Safe data deserialization works correctly")
                print(f"Data: {result}")
                return True
            else:
                print("❌ Safe data was corrupted")
                print(f"Expected: {safe_data}")
                print(f"Got: {result}")
                return False
        except Exception as e:
            print(f"❌ Safe data failed to deserialize: {e}")
            return False


def test_firewall_disabled():
    """Test that deserialization works normally when firewall is disabled."""
    print("\nTesting with firewall disabled (MODAL_USE_FIREWALL=false)...")
    
    # Disable firewall
    os.environ["MODAL_USE_FIREWALL"] = "false"
    
    from modal._serialization import deserialize
    
    # Mock client
    mock_client = Mock()
    
    # Create normal data
    data = {"message": "This should work normally"}
    data_pickle = pickle.dumps(data)
    
    # Mock as if we're on client side (local)
    with patch('modal._runtime.execution_context.is_local', return_value=True):
        try:
            result = deserialize(data_pickle, mock_client)
            if result == data:
                print("✅ Normal deserialization works with firewall disabled")
                return True
            else:
                print("❌ Data was corrupted")
                return False
        except Exception as e:
            print(f"❌ Failed to deserialize: {e}")
            return False


def test_server_side_unaffected():
    """Test that server-side (remote) deserialization is unaffected."""
    print("\nTesting server-side deserialization (should not use firewall)...")
    
    # Enable firewall (but it shouldn't matter for server-side)
    os.environ["MODAL_USE_FIREWALL"] = "true"
    
    from modal._serialization import deserialize
    
    # Mock client
    mock_client = Mock()
    
    # Create data
    data = {"server": "data", "test": True}
    data_pickle = pickle.dumps(data)
    
    # Mock as if we're on server side (remote)
    with patch('modal._runtime.execution_context.is_local', return_value=False):
        try:
            result = deserialize(data_pickle, mock_client)
            if result == data:
                print("✅ Server-side deserialization works normally")
                return True
            else:
                print("❌ Server-side data was corrupted")
                return False
        except Exception as e:
            print(f"❌ Server-side deserialization failed: {e}")
            return False


def main():
    print("Modal Firewall Integration Tests")
    print("=" * 50)
    
    tests = [
        test_firewall_blocks_exploit,
        test_safe_data_works,
        test_firewall_disabled,
        test_server_side_unaffected
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("\nYour Modal fork is successfully integrated with rffickle!")
        print("Set MODAL_USE_FIREWALL=true to enable safe deserialization.")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("\nPlease review the failures above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
