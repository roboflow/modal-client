#!/bin/bash
# Build script to generate protobuf files before packaging for PyPI

set -e

echo "================================================"
echo "  Building rfmodal for PyPI"
echo "================================================"

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Install required tools
echo "Installing required tools..."
pip3 install -q grpcio-tools grpclib

# Clean old generated files
echo "Cleaning old generated files..."
rm -f modal_proto/*_pb2.py modal_proto/*_pb2_grpc.py modal_proto/*_grpc.py modal_proto/*_grpclib.py 2>/dev/null || true

# Generate Python protobuf files
echo "Generating protobuf Python files..."
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. \
    modal_proto/api.proto modal_proto/options.proto

# Generate grpclib files (if needed)
echo "Generating grpclib files..."
python3 -c "
import sys
from grpclib.plugin.main import main
with open('modal_proto/api.proto', 'rb') as f:
    sys.stdin = f
    try:
        main()
    except SystemExit:
        pass
" > modal_proto/api_grpclib.py 2>/dev/null || echo "" > modal_proto/api_grpclib.py

# Generate modal-specific grpc wrapper
echo "Generating modal-specific gRPC wrapper..."
if [ -f "protoc_plugin_wrapper.py" ]; then
    chmod +x protoc_plugin_wrapper.py
    python3 -m grpc_tools.protoc \
        --plugin=protoc-gen-modal-grpclib-python=./protoc_plugin_wrapper.py \
        --modal-grpclib-python_out=. -I . modal_proto/api.proto || echo "Warning: modal-specific wrapper generation failed"
else
    echo "Warning: protoc_plugin_wrapper.py not found, skipping modal-specific wrapper"
fi

# Create symlink for api_grpc (if needed)
if [ -f "modal_proto/api_pb2_grpc.py" ] && [ ! -f "modal_proto/api_grpc.py" ]; then
    cd modal_proto
    ln -sf api_pb2_grpc.py api_grpc.py
    cd ..
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
for file in modal_proto/api_pb2.py modal_proto/options_pb2.py; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file is missing!"
        MISSING_FILES=1
    fi
done

if [ $MISSING_FILES -eq 1 ]; then
    echo ""
    echo "ERROR: Some critical files are missing!"
    exit 1
fi

echo ""
echo "✅ Ready to build package for PyPI!"
echo "Run: python3 -m build"
