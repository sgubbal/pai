# Personal AI Agent (PAI)

A serverless, cost-effective personal AI agent running on AWS with end-to-end encryption.

## Architecture

- **Infrastructure**: AWS CloudFormation (serverless)
- **Compute**: AWS Lambda
- **API**: API Gateway (HTTP API for lower cost)
- **Short-term Memory**: DynamoDB
- **Long-term Memory**: DynamoDB with vector search extension
- **Storage**: S3 with encryption
- **Security**: KMS encryption, client-side E2E encryption
- **CI/CD**: GitHub Actions

## Project Structure

```
pai/
├── infrastructure/          # CloudFormation templates
│   ├── templates/
│   └── parameters/
├── src/                    # Application code
│   ├── lambda/            # Lambda function handlers
│   ├── lib/               # Shared libraries
│   └── types/             # TypeScript types
├── scripts/               # Deployment and utility scripts
├── .github/               # GitHub Actions workflows
└── tests/                 # Test files
```

## Features

- ✅ Serverless architecture (zero cost when idle)
- ✅ End-to-end encryption
- ✅ Short-term memory (conversation context)
- ✅ Long-term memory (knowledge base with vector search)
- ✅ Single-user mode (no authentication required)
- ✅ CI/CD with GitHub Actions
- ✅ Monorepo structure

## Project Status

**MVP Status**: ✅ 100% Complete - Production Ready!

This project is a fully functional, production-ready personal AI agent with:
- ✅ Complete infrastructure as code (CloudFormation)
- ✅ End-to-end encryption implementation
- ✅ Short-term and long-term memory systems
- ✅ Vector search capabilities
- ✅ CI/CD pipeline (GitHub Actions)
- ✅ Deployment automation scripts
- ✅ LLM integration (AWS Bedrock - Claude 3.5 Sonnet)
- ✅ Real embeddings (AWS Bedrock - Titan Embeddings V2)

## Quick Start

```bash
# 1. Enable AWS Bedrock models (one-time setup)
# See BEDROCK_SETUP.md for detailed instructions

# 2. Setup project dependencies
./scripts/setup.sh

# 3. Deploy infrastructure
./scripts/deploy.sh dev

# 4. Build and deploy functions
npm run build
./scripts/package-functions.sh
./scripts/deploy-functions.sh dev

# 5. Test deployment
./scripts/smoke-test.sh dev
```

For detailed instructions:
- **First time?** See [BEDROCK_SETUP.md](./BEDROCK_SETUP.md) to enable AWS Bedrock
- **Quick deployment**: See [QUICKSTART.md](./QUICKSTART.md)
- **Comprehensive guide**: See [DEPLOYMENT.md](./DEPLOYMENT.md)

## Documentation

- **[BEDROCK_SETUP.md](./BEDROCK_SETUP.md)** - 🔥 Start here! Enable AWS Bedrock models
- **[QUICKSTART.md](./QUICKSTART.md)** - Get started in 10 minutes
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Comprehensive deployment guide
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Technical architecture details
- **[API.md](./API.md)** - API documentation

## Getting Started

### Prerequisites

- AWS CLI configured
- Node.js 20+
- AWS account

### Deployment

```bash
# Setup (first time only)
./scripts/setup.sh

# Deploy infrastructure
./scripts/deploy.sh dev

# Build and deploy functions
npm run build
./scripts/package-functions.sh
./scripts/deploy-functions.sh dev
```

## Cost Optimization

- HTTP API Gateway (cheaper than REST API)
- Lambda ARM64 architecture
- DynamoDB on-demand pricing
- S3 Intelligent-Tiering
- No NAT Gateway or VPC (public Lambda)
