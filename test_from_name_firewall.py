# Copyright Modal Labs 2025
#!/usr/bin/env python3
"""Test that Cls.from_name() with use_firewall=True works correctly."""

import os
import sys
from unittest.mock import MagicMock, Mock


def test_cls_from_name_with_firewall():
    """Test that Cls.from_name with use_firewall=True properly sets up firewall protection."""
    print("Testing Cls.from_name() with use_firewall parameter...")
    
    # Mock the necessary Modal imports
    sys.modules['modal_proto'] = MagicMock()
    sys.modules['modal_proto'].api_pb2 = MagicMock()
    
    # Now we can import modal.cls
    from modal.cls import _Cls
    from modal._functions import _Function
    
    # Create a mock class service function
    mock_class_service_function = Mock(spec=_Function)
    mock_class_service_function._use_firewall = False  # Initially false
    
    # Test 1: from_name without use_firewall (default)
    print("\n1. Testing Cls.from_name without use_firewall...")
    
    # Mock the _from_name method to return our mock function
    original_from_name = _Function._from_name
    _Function._from_name = Mock(return_value=mock_class_service_function)
    
    # Call from_name without use_firewall
    cls = _Cls.from_name("test-app", "TestClass")
    
    # Check that the class service function doesn't have firewall enabled
    assert cls._class_service_function._use_firewall == False
    print("✅ Default behavior: use_firewall is False")
    
    # Test 2: from_name with use_firewall=True
    print("\n2. Testing Cls.from_name with use_firewall=True...")
    
    # Reset the mock
    mock_class_service_function._use_firewall = False
    
    # Call from_name with use_firewall=True
    cls_with_firewall = _Cls.from_name("test-app", "TestClass", use_firewall=True)
    
    # Check that the class service function has firewall enabled
    assert cls_with_firewall._class_service_function._use_firewall == True
    print("✅ With use_firewall=True: firewall is enabled on class service function")
    
    # Restore original method
    _Function._from_name = original_from_name
    
    return True


def test_function_from_name_with_firewall():
    """Test that Function.from_name with use_firewall=True properly sets up firewall protection."""
    print("\n3. Testing Function.from_name() with use_firewall parameter...")
    
    from modal._functions import _Function
    
    # Create a mock function
    mock_function = Mock(spec=_Function)
    mock_function._use_firewall = False
    
    # Mock the _from_name method
    original_from_name = _Function._from_name
    _Function._from_name = Mock(return_value=mock_function)
    
    # Test without use_firewall
    func = _Function.from_name("test-app", "test_function")
    assert func._use_firewall == False
    print("✅ Default behavior: use_firewall is False")
    
    # Test with use_firewall=True
    func_with_firewall = _Function.from_name("test-app", "test_function", use_firewall=True)
    assert func_with_firewall._use_firewall == True
    print("✅ With use_firewall=True: firewall is enabled on function")
    
    # Restore original method
    _Function._from_name = original_from_name
    
    return True


def test_usage_example():
    """Show how to use the feature with Cls.from_name."""
    print("\n" + "=" * 50)
    print("EXAMPLE USAGE:")
    print("=" * 50)
    
    example = '''
# When looking up a deployed class that runs untrusted code:

import modal

# Look up the class with firewall protection enabled
CustomBlockExecutor = modal.Cls.from_name(
    "inference-custom-blocks", 
    "CustomBlockExecutor",
    use_firewall=True  # Enable safe deserialization
)

# Now when you call methods on this class, results will be
# deserialized using rffickle to prevent pickle-based attacks
executor = CustomBlockExecutor()
result = executor.run_user_code.remote(untrusted_code)

# For functions:
untrusted_func = modal.Function.from_name(
    "untrusted-app",
    "process_user_input", 
    use_firewall=True
)
result = untrusted_func.remote(user_data)
'''
    
    print(example)
    return True


def main():
    print("Cls.from_name Firewall Test")
    print("=" * 50)
    
    try:
        # Run tests
        success = (
            test_cls_from_name_with_firewall() and
            test_function_from_name_with_firewall() and
            test_usage_example()
        )
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ALL TESTS PASSED")
        print("\nCls.from_name() and Function.from_name() now support use_firewall parameter!")
        print("This allows safe deserialization when looking up remote functions/classes.")
        return 0
    else:
        print("❌ TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
