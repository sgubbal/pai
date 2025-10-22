#!/bin/bash

set -e

echo "==================================="
echo "PAI Setup Script"
echo "==================================="

# Check prerequisites
echo "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "Please install Node.js 20+ from https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 20 ]; then
    echo "❌ Node.js version must be 20 or higher (found: $NODE_VERSION)"
    exit 1
fi
echo "✓ Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    exit 1
fi
echo "✓ npm $(npm --version)"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed"
    echo "Please install AWS CLI from https://aws.amazon.com/cli/"
    exit 1
fi
echo "✓ AWS CLI $(aws --version | cut -d' ' -f1 | cut -d'/' -f2)"

# Check AWS credentials
echo ""
echo "Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=$(aws configure get region || echo "not set")
    echo "✓ AWS credentials configured"
    echo "  Account ID: $ACCOUNT_ID"
    echo "  Region: $REGION"

    if [ "$REGION" == "not set" ]; then
        echo "⚠️  AWS region not set. Using us-east-1"
        export AWS_REGION=us-east-1
    fi
else
    echo "❌ AWS credentials not configured"
    echo "Please run: aws configure"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
npm install

# Build project
echo ""
echo "Building project..."
npm run build

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

echo ""
echo "==================================="
echo "✨ Setup complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Review and update .env file if needed"
echo "2. Deploy infrastructure: ./scripts/deploy.sh dev"
echo "3. Build and deploy functions: ./scripts/package-functions.sh && ./scripts/deploy-functions.sh dev"
echo "4. Run tests: ./scripts/smoke-test.sh dev"
echo ""
echo "For more information, see QUICKSTART.md"
echo "==================================="
