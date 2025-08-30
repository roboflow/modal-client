# Copyright Modal Labs 2025
#!/usr/bin/env python3
"""Simple test to verify no unsafe fallback."""

import os
import sys
from unittest.mock import MagicMock

# Hide rffickle temporarily
sys.modules['rffickle'] = None

# Now try to import the deserialize function
try:
    # Add minimal mocks
    sys.modules['modal_proto'] = MagicMock()
    sys.modules['modal._runtime'] = MagicMock()
    sys.modules['modal._runtime.execution_context'] = MagicMock()
    sys.modules['modal._runtime.execution_context'].is_local = MagicMock(return_value=True)
    
    from modal._serialization import deserialize
    
    # Try to deserialize with firewall enabled
    import pickle
    data = pickle.dumps({"test": "data"})
    
    print("Testing with use_firewall=True and rffickle unavailable...")
    try:
        result = deserialize(data, None, use_firewall=True)
        print("❌ SECURITY BREACH: Deserialization succeeded without rffickle!")
        print(f"Result: {result}")
    except (ImportError, ModuleNotFoundError) as e:
        print(f"✅ Properly failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        
except Exception as e:
    print(f"Setup failed: {e}")
    import traceback
    traceback.print_exc()
