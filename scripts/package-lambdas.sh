#!/bin/bash
set -e

# Lambda Function Packaging Script

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ENVIRONMENT=${1:-dev}
STACK_NAME="chatbot-${ENVIRONMENT}"
REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Lambda Function Packaging${NC}"
echo -e "${GREEN}========================================${NC}"

# Create build directory
BUILD_DIR="build/lambda"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

###################
# Step 1: Install Dependencies
###################
echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"

pip3 install -r requirements.txt -t $BUILD_DIR --platform manylinux2014_aarch64 --only-binary=:all: --python-version 3.12 --quiet

echo -e "${GREEN}✓ Dependencies installed${NC}"

###################
# Step 2: Copy Source Code
###################
echo ""
echo -e "${YELLOW}Step 2: Copying source code...${NC}"

# Copy chatbot handler
cp src/chatbot/handler.py $BUILD_DIR/

echo -e "${GREEN}✓ Source code copied${NC}"

###################
# Step 3: Create ZIP
###################
echo ""
echo -e "${YELLOW}Step 3: Creating deployment package...${NC}"

cd $BUILD_DIR
zip -r -q ../chatbot.zip .
cd - > /dev/null

PACKAGE_SIZE=$(du -h build/chatbot.zip | cut -f1)
echo -e "${GREEN}✓ Package created (${PACKAGE_SIZE})${NC}"

###################
# Step 4: Upload to Lambda
###################
echo ""
echo -e "${YELLOW}Step 4: Updating Lambda function...${NC}"

FUNCTION_NAME="chatbot-chat-${ENVIRONMENT}"

aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://build/chatbot.zip \
    --region $REGION > /dev/null

echo -e "${GREEN}✓ Lambda function updated${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Lambda Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
