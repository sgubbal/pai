#!/bin/bash

set -e

echo "==================================="
echo "Packaging Lambda Functions"
echo "==================================="

# Create package directory
mkdir -p dist/packages

# Function to package a Lambda function
package_function() {
    local FUNCTION_NAME=$1
    local HANDLER_FILE=$2

    echo "Packaging ${FUNCTION_NAME}..."

    # Create temporary directory
    local TEMP_DIR="dist/temp/${FUNCTION_NAME}"
    mkdir -p "${TEMP_DIR}"

    # Copy compiled code
    cp -r dist/lambda/*.js dist/lambda/*.js.map "${TEMP_DIR}/" 2>/dev/null || true
    cp -r dist/lib "${TEMP_DIR}/" 2>/dev/null || true
    cp -r dist/types "${TEMP_DIR}/" 2>/dev/null || true

    # Copy production dependencies
    cp -r node_modules "${TEMP_DIR}/"
    cp package.json "${TEMP_DIR}/"

    # Create deployment package
    cd "${TEMP_DIR}"
    zip -r "../../packages/${FUNCTION_NAME}.zip" . -q
    cd - > /dev/null

    echo "✓ ${FUNCTION_NAME}.zip created ($(du -h "dist/packages/${FUNCTION_NAME}.zip" | cut -f1))"
}

# Package each Lambda function
package_function "chat" "lambda/chat.js"
package_function "memory" "lambda/memory.js"
package_function "vector-search" "lambda/vector-search.js"

# Clean up temporary files
rm -rf dist/temp

echo "==================================="
echo "Lambda packaging complete!"
echo "==================================="
ls -lh dist/packages/
