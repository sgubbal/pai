#!/bin/bash

# Script to package Lambda functions and layers
set -e

echo "Packaging Lambda functions and layers..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"

# Clean build directory
echo -e "${YELLOW}Cleaning build directory...${NC}"
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/layers" "$BUILD_DIR/functions"

# Package dependencies layer
echo -e "${YELLOW}Packaging dependencies layer...${NC}"
LAYER_DIR="$BUILD_DIR/layers/python"
mkdir -p "$LAYER_DIR"

# Install dependencies
pip install -r "$PROJECT_ROOT/requirements.txt" -t "$LAYER_DIR" --quiet

# Create layer zip
cd "$BUILD_DIR/layers"
zip -r dependencies.zip python -q
rm -rf python
echo -e "${GREEN}Dependencies layer packaged${NC}"

# Package chatbot Lambda
echo -e "${YELLOW}Packaging chatbot Lambda...${NC}"
CHATBOT_DIR="$BUILD_DIR/functions/chatbot"
mkdir -p "$CHATBOT_DIR"

# Copy source code
cp -r "$PROJECT_ROOT/src" "$CHATBOT_DIR/"

# Create chatbot zip
cd "$CHATBOT_DIR"
zip -r ../chatbot.zip . -q
cd ..
rm -rf chatbot
echo -e "${GREEN}Chatbot Lambda packaged${NC}"

# Package authorizer Lambda
echo -e "${YELLOW}Packaging authorizer Lambda...${NC}"
AUTHORIZER_DIR="$BUILD_DIR/functions/authorizer"
mkdir -p "$AUTHORIZER_DIR"

# Copy source code
cp -r "$PROJECT_ROOT/src" "$AUTHORIZER_DIR/"

# Create authorizer zip
cd "$AUTHORIZER_DIR"
zip -r ../authorizer.zip . -q
cd ..
rm -rf authorizer
echo -e "${GREEN}Authorizer Lambda packaged${NC}"

echo -e "${GREEN}All Lambda packages created successfully in $BUILD_DIR${NC}"
ls -lh "$BUILD_DIR/layers/"
ls -lh "$BUILD_DIR/functions/"
