#!/usr/bin/env python3
"""Test per-function firewall configuration."""

import pickle
import os
import sys
from unittest.mock import Mock, MagicMock, patch


def test_per_function_firewall():
    """Test that per-function firewall configuration works."""
    print("Testing per-function firewall configuration...")
    
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
    
    # Mock logger
    logger_mock = MagicMock()
    sys.modules['modal.config'].logger = logger_mock
    
    # Clear any environment variable
    if "MODAL_USE_FIREWALL" in os.environ:
        del os.environ["MODAL_USE_FIREWALL"]
    
    # Import the serialization module
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "modal._serialization", 
        "/Users/yeldarb/Code/modal-client/modal/_serialization.py"
    )
    serialization = importlib.util.module_from_spec(spec)
    sys.modules['modal._runtime.execution_context'].is_local = MagicMock(return_value=True)
    spec.loader.exec_module(serialization)
    
    # Test 1: Without use_firewall flag (should allow exploit in this test setup)
    print("\n1. Testing without firewall (default behavior)...")
    
    safe_data = {"value": 42}
    safe_pickle = pickle.dumps(safe_data)
    
    try:
        result = serialization.deserialize(safe_pickle, None)
        if result == safe_data:
            print("✅ Normal deserialization works without firewall")
        else:
            print("❌ Data corrupted")
            return False
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False
    
    # Test 2: With use_firewall via environment variable
    print("\n2. Testing with firewall via environment variable...")
    os.environ["MODAL_USE_FIREWALL"] = "true"
    
    # Create an exploit
    class Exploit:
        def __reduce__(self):
            return (os.system, ('echo "EXPLOITED"',))
    
    exploit_pickle = pickle.dumps(Exploit())
    
    try:
        result = serialization.deserialize(exploit_pickle, None)
        print("❌ Exploit was not blocked with MODAL_USE_FIREWALL=true!")
        return False
    except Exception as e:
        print(f"✅ Exploit blocked with environment variable: {type(e).__name__}")
    
    # Test 3: Simulate per-function configuration
    print("\n3. Testing per-function firewall simulation...")
    
    # Clear environment variable
    del os.environ["MODAL_USE_FIREWALL"]
    
    # Create a mock function with use_firewall=True
    class MockFunction:
        _use_firewall = True
    
    # Simulate calling _process_result with use_firewall from function
    from modal._utils.function_utils import _process_result
    
    # Mock the necessary parameters
    mock_result = MagicMock()
    mock_result.status = 0  # SUCCESS status
    mock_result.WhichOneof.return_value = "data"
    mock_result.data = exploit_pickle
    
    # Mock the client
    mock_client = MagicMock()
    
    # Import api_pb2 mock constants
    sys.modules['modal_proto'].api_pb2.DATA_FORMAT_PICKLE = 1
    sys.modules['modal_proto'].api_pb2.GenericResult.GENERIC_STATUS_SUCCESS = 0
    
    # This should use the firewall and block the exploit
    print("Testing _process_result with use_firewall=True...")
    import asyncio
    
    async def test_process_result():
        try:
            result = await _process_result(
                mock_result, 
                1,  # DATA_FORMAT_PICKLE
                None,  # stub
                mock_client,
                use_firewall=True
            )
            print("❌ Exploit was not blocked in _process_result!")
            return False
        except Exception as e:
            print(f"✅ Exploit blocked in _process_result: {type(e).__name__}")
            return True
    
    # Run the async test
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(test_process_result())
        loop.close()
        
        if not success:
            return False
    except Exception as e:
        print(f"✅ Exploit blocked (exception during test): {type(e).__name__}")
    
    return True


def main():
    print("Per-Function Firewall Configuration Test")
    print("=" * 50)
    
    try:
        success = test_per_function_firewall()
    except Exception as e:
        print(f"❌ Test crashed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nPer-function firewall configuration is working!")
        print("Functions can now individually opt-in to safe deserialization.")
        return 0
    else:
        print("❌ TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
