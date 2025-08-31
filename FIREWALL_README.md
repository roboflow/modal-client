# rffickle Integration for Modal Client (rfmodal)

This is a security-enhanced fork of the Modal client library that integrates `rffickle` for safe pickle deserialization.

## What's Changed

This fork adds support for using `rffickle` (Roboflow's fork of `fickle`) to safely deserialize pickled data from untrusted Modal functions. This prevents pickle-based Remote Code Execution (RCE) attacks when running untrusted user code in Modal sandboxes.

## Security Problem Addressed

When untrusted code runs in a Modal sandbox and returns malicious pickled objects, those objects can execute arbitrary code on the client machine during deserialization. This fork mitigates that risk by using `rffickle`'s firewall to block dangerous pickle operations.

## Implementation

The changes are minimal and focused on four files:

1. **modal/_serialization.py**: Modified `deserialize()` function to optionally use `rffickle.DefaultFirewall`
2. **modal/app.py**: Added `use_firewall` parameter to `@app.function()` and `@app.cls()` decorators
3. **modal/_functions.py**: Store and pass the firewall flag through function execution
4. **modal/_utils/function_utils.py**: Process results with the firewall option

### Key Design Decisions

- **No fallback to unsafe pickle**: If `use_firewall=True` is set but `rffickle` is not installed, the function will fail rather than falling back to unsafe deserialization
- **Per-function configuration**: Each function can individually opt-in to safe deserialization
- **Client-side only**: Firewall only applies to client-side (local) deserialization, not server-side
- **Backward compatible**: Existing code continues to work without changes (defaults to `use_firewall=False`)

## Usage

### Per-Function Configuration

When defining functions in your app:

```python
import modal

app = modal.App()

# Trusted function - regular pickle deserialization (default)
@app.function()
def process_internal_data(data):
    """Processes trusted internal data with full pickle support."""
    return complex_computation(data)

# Untrusted function - rffickle firewall enabled
@app.function(use_firewall=True)
def run_user_code(code: str):
    """Safely runs untrusted user code.
    
    Even if the user code returns malicious pickled objects,
    they will be blocked during deserialization on the client.
    """
    exec(code)
    return result

# For class-based functions
@app.cls(use_firewall=True)
class UntrustedExecutor:
    @modal.method()
    def execute(self, code: str):
        """Execute untrusted code in a sandboxed environment."""
        exec(code)
        return result
```

### Looking Up Remote Functions/Classes

When using `Cls.from_name()` or `Function.from_name()` to look up deployed functions:

```python
import modal

# Look up a class with firewall protection enabled
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
```

**Important**: When using `from_name()`, you must explicitly set `use_firewall=True` because the client doesn't know if the deployed function was originally configured with firewall protection.

## Installation

```bash
# Install the modified modal client (includes rffickle automatically)
pip install -e /path/to/modal-client

# Or if published to PyPI:
pip install rfmodal
```

The `rffickle` dependency is automatically installed with `rfmodal`.

## Testing

Run the test suite to verify the implementation:
```bash
python test_implementation.py  # Verifies all code changes are in place
python test_firewall_direct.py  # Tests the serialization module directly
```

## Status

✅ **Implementation Complete**: All necessary changes have been made to support per-function firewall configuration.

### What's Working:
- Per-function `use_firewall` parameter on decorators
- Firewall flag properly passed through function execution pipeline
- Safe deserialization using `rffickle` when enabled
- No performance impact on functions that don't use the firewall
- Proper error handling (no unsafe fallback)

### Next Steps for Production:
1. Deploy `rfmodal` package to PyPI
2. Update Inference codebase to use `use_firewall=True` for custom Python blocks
3. Add monitoring/logging for blocked pickle operations
4. Consider adding validation that `rffickle` is installed when `use_firewall=True` is used
