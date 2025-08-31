#!/bin/bash
# Build script to generate protobuf files before packaging for PyPI
# Fixed to use grpclib instead of grpcio

set -e

echo "================================================"
echo "  Building rfmodal for PyPI (grpclib version)"
echo "================================================"

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Install required tools
echo "Installing required tools..."
pip3 install -q protobuf grpclib

# Clean old generated files
echo "Cleaning old generated files..."
rm -f modal_proto/*_pb2.py modal_proto/*_pb2_grpc.py modal_proto/*_grpc.py modal_proto/*_grpclib.py 2>/dev/null || true

# Generate Python protobuf files (messages only)
echo "Generating protobuf Python message files..."
protoc -I. --python_out=. modal_proto/api.proto modal_proto/options.proto

# Create grpclib plugin wrapper if it doesn't exist
if [ ! -f "grpclib_plugin.py" ]; then
    echo "Creating grpclib plugin wrapper..."
    cat > grpclib_plugin.py << 'EOF'
#!/usr/bin/env python3
import sys
from grpclib.plugin.main import main

if __name__ == '__main__':
    main()
EOF
    chmod +x grpclib_plugin.py
fi

# Generate grpclib service stubs
echo "Generating grpclib service stubs..."
protoc --plugin=protoc-gen-grpclib_python=./grpclib_plugin.py \
       --grpclib_python_out=. -I. modal_proto/api.proto

# Generate modal-specific grpc wrapper if available
echo "Generating modal-specific gRPC wrapper..."
if [ -f "protoc_plugin_wrapper.py" ]; then
    chmod +x protoc_plugin_wrapper.py
    protoc --plugin=protoc-gen-modal-grpclib-python=./protoc_plugin_wrapper.py \
        --modal-grpclib-python_out=. -I . modal_proto/api.proto || echo "Warning: modal-specific wrapper generation failed"
else
    echo "Warning: protoc_plugin_wrapper.py not found, skipping modal-specific wrapper"
fi

echo "================================================"
echo "Protobuf generation complete!"
echo "================================================"

# List generated files
echo "Generated files in modal_proto:"
ls -la modal_proto/*.py 2>/dev/null | grep -v __pycache__ || echo "No .py files found"

# Verify critical files exist
echo ""
echo "Verifying critical files..."
MISSING_FILES=0
for file in modal_proto/api_pb2.py modal_proto/options_pb2.py modal_proto/api_grpc.py; do
    if [ -f "$file" ]; then
        size=$(wc -c < "$file")
        if [ $size -gt 0 ]; then
            echo "✓ $file exists ($(wc -l < $file) lines)"
        else
            echo "✗ $file is empty!"
            MISSING_FILES=1
        fi
    else
        echo "✗ $file is missing!"
        MISSING_FILES=1
    fi
done

if [ $MISSING_FILES -eq 1 ]; then
    echo ""
    echo "ERROR: Some critical files are missing or empty!"
    exit 1
fi

echo ""
echo "✅ Ready to build package for PyPI!"
echo "Run: python3 -m build"
