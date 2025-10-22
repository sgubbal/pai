# Personal AI Agent (PAI)

An end-to-end encrypted, cost-effective serverless AI agent built on AWS with short-term and long-term memory capabilities.

## Overview

PAI is a personal AI agent designed for single-user use, leveraging AWS serverless services for cost-effectiveness and scalability. The system includes:

- **End-to-end encryption** using AWS KMS
- **Short-term memory** via DynamoDB for fast access
- **Long-term memory** with S3 and vector search capabilities
- **Serverless architecture** using AWS Lambda, DynamoDB, S3, and Bedrock
- **Modular Python codebase** for easy scaling and maintenance
- **Infrastructure as Code** using CloudFormation

## Architecture

```
┌─────────────────┐
│   API Gateway   │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Lambda  │
    │ (Agent) │
    └────┬────┘
         │
    ┌────┴────────────────────┐
    │                         │
┌───▼────────┐        ┌──────▼──────┐
│  DynamoDB  │        │  Bedrock    │
│ (Short-term│        │  (AI Model) │
│  Memory)   │        └─────────────┘
└────────────┘
         │
    ┌────▼────────────────────┐
    │                         │
┌───▼────────┐        ┌──────▼──────┐
│     S3     │        │ OpenSearch  │
│ (Long-term │        │ Serverless  │
│  Memory)   │        │  (Vectors)  │
└────────────┘        └─────────────┘
```

## Project Structure

```
pai/
├── infra/                      # Infrastructure as Code
│   └── cloudformation/         # CloudFormation templates
│       ├── main.yaml          # Main stack
│       ├── storage.yaml       # DynamoDB, S3
│       ├── compute.yaml       # Lambda functions
│       ├── ai.yaml            # Bedrock, OpenSearch
│       └── security.yaml      # KMS, IAM
├── src/                       # Application code
│   ├── lambdas/              # Lambda function handlers
│   │   ├── agent/            # Main agent handler
│   │   ├── memory/           # Memory management
│   │   └── search/           # Vector search
│   ├── services/             # Business logic
│   │   ├── ai_service.py     # AI interactions
│   │   ├── memory_service.py # Memory management
│   │   ├── vector_service.py # Vector operations
│   │   └── encryption.py     # Encryption utilities
│   ├── models/               # Data models
│   │   ├── message.py
│   │   └── memory.py
│   └── utils/                # Shared utilities
│       ├── logger.py
│       ├── config.py
│       └── helpers.py
├── tests/                    # Unit tests
│   ├── unit/
│   └── integration/
├── scripts/                  # Deployment scripts
│   ├── deploy.sh
│   ├── test.sh
│   ├── cleanup.sh
│   └── package-lambdas.sh
├── .github/
│   └── workflows/           # CI/CD pipelines
│       ├── deploy.yaml
│       └── test.yaml
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
└── .env.example            # Environment template
```

## Features

### 1. End-to-End Encryption
- All data encrypted at rest using AWS KMS
- Conversation data encrypted before storage
- Secure key management

### 2. Memory System
- **Short-term Memory**: DynamoDB for recent conversations and context
- **Long-term Memory**: S3 for persistent storage
- **Vector Search**: OpenSearch Serverless for semantic search across memories

### 3. Cost-Effective
- Pay-per-use Lambda functions (ARM64 for cost savings)
- On-demand DynamoDB billing
- S3 Intelligent-Tiering for cost optimization
- OpenSearch Serverless for vector search

### 4. Modular & Scalable
- Clean separation of concerns
- Easy to add new capabilities
- CloudFormation for reproducible infrastructure

## Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.11+
- GitHub account (for Actions)

### Quick Start

1. **Clone and setup**:
```bash
git clone <your-repo>
cd pai
cp .env.example .env
# Edit .env with your AWS settings
```

2. **Install dependencies**:
```bash
pip install -r requirements-dev.txt
```

3. **Deploy infrastructure**:
```bash
./scripts/deploy.sh
```

4. **Test the deployment**:
```bash
./scripts/test.sh
```

### Configuration

Create a `.env` file with:
```bash
AWS_REGION=us-east-1
STACK_NAME=pai-agent
KMS_KEY_ALIAS=pai-encryption-key
AI_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
```

## Development

### Running Tests
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# All tests with coverage
pytest --cov=src tests/
```

### Local Development
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
pylint src/

# Format code
black src/
```

## Deployment

### Manual Deployment
```bash
# Package Lambda functions
./scripts/package-lambdas.sh

# Deploy CloudFormation stack
./scripts/deploy.sh
```

### CI/CD with GitHub Actions
- Push to `main` branch triggers automatic deployment
- Pull requests trigger tests and validation
- See `.github/workflows/` for pipeline details

## API Usage

### Send a Message
```bash
curl -X POST https://your-api-gateway-url/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "conversation_id": "optional-conversation-id"
  }'
```

### Search Memory
```bash
curl -X POST https://your-api-gateway-url/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did we discuss about Python?",
    "limit": 10
  }'
```

## Security

- Single-user design (no authentication required for MVP)
- All data encrypted with customer-managed KMS keys
- IAM roles follow least-privilege principle
- Private VPC endpoints available (optional configuration)

## Cost Estimation

For typical single-user usage (assuming ~1000 messages/month):
- **Lambda**: ~$1-3/month (ARM64 pricing)
- **DynamoDB**: ~$1-2/month (on-demand)
- **S3**: ~$0.50-1/month
- **OpenSearch Serverless**: ~$5-10/month (vector search)
- **Bedrock**: ~$5-15/month (pay per token)

**Total estimated cost**: **$10-30/month** depending on usage

## Technology Stack

- **Language**: Python 3.11
- **Compute**: AWS Lambda (ARM64)
- **API**: API Gateway (HTTP API)
- **Storage**: DynamoDB, S3
- **AI**: Amazon Bedrock (Claude 3 Sonnet)
- **Vector DB**: OpenSearch Serverless
- **Encryption**: AWS KMS
- **IaC**: CloudFormation
- **CI/CD**: GitHub Actions

## Future Enhancements

- [ ] Frontend web interface (React/Next.js)
- [ ] Multi-user support with Cognito
- [ ] Voice interface support
- [ ] Mobile app (React Native)
- [ ] Additional AI model integrations
- [ ] RAG (Retrieval Augmented Generation) capabilities
- [ ] Scheduled tasks and reminders

## Troubleshooting

### Common Issues

1. **Bedrock Model Access**
   - Ensure you've requested access to Bedrock models in AWS Console
   - Check your AWS region supports Bedrock

2. **Deployment Failures**
   - Verify AWS credentials are configured
   - Check CloudFormation stack events for specific errors
   - Ensure sufficient IAM permissions

3. **High Costs**
   - Review OpenSearch Serverless usage
   - Check Bedrock token consumption
   - Consider reducing memory retention period

## Contributing

This is a personal project, but suggestions and issues are welcome!

## License

MIT License

## Support

For issues or questions:
- Check the documentation in `/docs`
- Review CloudFormation stack events
- Check Lambda function logs in CloudWatch

---

Built with ❤️ using AWS Serverless and Python
