#!/bin/bash

set -e

echo "==================================="
echo "Building PAI Locally"
echo "==================================="

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Run linter
echo "Running linter..."
npm run lint || {
    echo "Linting failed. Fix errors before proceeding."
    exit 1
}

# Build TypeScript
echo "Building TypeScript..."
npm run build

# Run tests
echo "Running tests..."
npm test

echo "==================================="
echo "Local build complete!"
echo "==================================="
