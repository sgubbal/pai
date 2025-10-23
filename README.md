# Personal AI Chatbot

> A modular, cost-effective serverless chatbot built on AWS that starts simple (Phase 1) and extends to RAG (Phase 2)

[![Deploy](https://github.com/yourusername/pai/workflows/Deploy%20Chatbot/badge.svg)](https://github.com/yourusername/pai/actions)

## Overview

A personal AI chatbot MVP built with:
- ✅ **Simple Start**: Deploy a working chatbot in < 15 minutes
- ✅ **Easy Extension**: Enable RAG with one parameter
- ✅ **Cost-Effective**: ~$10/month for MVP, ~$30/month with RAG
- ✅ **Secure**: End-to-end encryption with KMS
- ✅ **Serverless**: Auto-scaling, pay-per-use
- ✅ **Production-Ready**: CI/CD, monitoring, testing included

## Quick Start

### Prerequisites
- AWS Account with Bedrock access
- AWS CLI v2+ configured
- Python 3.12+
- Bash shell

### Deploy Phase 1 (Simple Chatbot)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/pai.git
cd pai

# 2. Deploy infrastructure
./scripts/deploy.sh dev

# 3. Deploy Lambda code
./scripts/package-lambdas.sh dev

# 4. Test your chatbot
./scripts/test.sh dev
```

That's it! Your chatbot is live. 🎉

### Test the API

```bash
# Get your API endpoint
export API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name chatbot-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text)

# Send a message
curl -X POST "${API_ENDPOINT}/chat" \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "my-chat", "message": "Hello! Tell me a joke."}'
```

## Architecture

### Phase 1: Simple Chatbot (MVP)

```
User → API Gateway → Lambda → Bedrock (Claude)
                       ↓
                   DynamoDB
```

**Components:**
- **API Gateway**: HTTP API with `/chat` endpoint
- **Lambda**: Chat handler (Python 3.12, ARM64)
- **DynamoDB**: Conversation history (auto-expires after 30 days)
- **Bedrock**: Claude 3.5 Sonnet v2
- **KMS**: Encryption at rest

**Monthly Cost**: ~$8-16

### Phase 2: RAG Extension

```
Documents → S3 → Lambda (Ingestion) → Bedrock (Embeddings)
                                            ↓
                                   OpenSearch Serverless
                                            ↓
User → API Gateway → Lambda (Chat) → Bedrock + Context
                       ↓
                   DynamoDB
```

**Additional Components:**
- **S3**: Document storage
- **Lambda (Ingestion)**: Process and embed documents
- **OpenSearch**: Vector search
- **Bedrock Embeddings**: Titan Embeddings v2

**Monthly Cost**: ~$25-48

## Enable RAG (Phase 2)

When you're ready to add RAG capabilities:

```bash
# Update stack with RAG enabled
./scripts/deploy.sh dev true

# Re-deploy Lambda code
./scripts/package-lambdas.sh dev

# Upload documents
aws s3 cp my_resume.pdf s3://chatbot-documents-ACCOUNT-dev/

# Ask questions about your documents
curl -X POST "${API_ENDPOINT}/chat" \
  -d '{"message": "What skills are in my resume?"}'
```

## Project Structure

```
/
├── .github/workflows/      # GitHub Actions CI/CD
│   └── deploy.yaml
├── infra/cloudformation/   # Infrastructure as Code
│   ├── main.yaml          # Orchestrator
│   ├── security.yaml      # KMS, IAM
│   ├── storage.yaml       # DynamoDB, S3
│   ├── compute.yaml       # Lambda, API Gateway
│   └── ai.yaml            # OpenSearch (Phase 2)
├── src/
│   ├── chatbot/           # Phase 1 code
│   │   └── handler.py     # Main chat handler
│   ├── rag/               # Phase 2 code (future)
│   └── shared/            # Common utilities
├── scripts/
│   ├── deploy.sh          # Deploy infrastructure
│   ├── package-lambdas.sh # Build & deploy Lambda
│   ├── cleanup.sh         # Destroy stack
│   └── test.sh            # Smoke tests
├── tests/                 # Unit & integration tests
├── requirements.txt       # Python dependencies
├── ARCHITECTURE.md        # Detailed architecture
└── README.md             # This file
```

## Features

### Phase 1 (Available Now)
- [x] Conversational AI with Claude 3.5 Sonnet
- [x] Conversation history (last 10 messages)
- [x] Auto-expiring messages (30 days TTL)
- [x] End-to-end encryption
- [x] RESTful API
- [x] CI/CD with GitHub Actions

### Phase 2 (Enable with `EnableRAG=true`)
- [ ] Document upload (PDF, TXT, MD)
- [ ] Semantic search with embeddings
- [ ] RAG: Answer questions from your documents
- [ ] Vector database (OpenSearch Serverless)

### Future Enhancements
- [ ] Streaming responses
- [ ] Web UI
- [ ] Multi-user support (Cognito)
- [ ] Voice interface
- [ ] Document format support (DOCX, images)

## Development

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run unit tests
pytest tests/unit/

# Run linting
ruff check src/

# Type checking
mypy src/
```

### Environment Variables

The Lambda functions use these environment variables (auto-configured):

```bash
ENVIRONMENT=dev                    # Deployment environment
CONVERSATIONS_TABLE=chatbot-conversations-dev
KMS_KEY_ID=xxx                     # KMS key for encryption
AI_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0
ENABLE_RAG=false                   # Enable RAG features
```

## Deployment

### Manual Deployment

```bash
# Deploy to dev
./scripts/deploy.sh dev

# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production with RAG
./scripts/deploy.sh prod true
```

### GitHub Actions

Push to `main` branch for automatic deployment:

```yaml
# .github/workflows/deploy.yaml
on:
  push:
    branches: [main]
```

Manual workflow dispatch:
1. Go to Actions → Deploy Chatbot
2. Select environment (dev/staging/prod)
3. Click "Run workflow"

### CI/CD Setup

1. Add AWS credentials to GitHub Secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION`

## Cost Breakdown

| Service | Phase 1 (Monthly) | Phase 2 (Monthly) |
|---------|-------------------|-------------------|
| Lambda | $1-3 | $4-8 |
| DynamoDB | $1-2 | $1-2 |
| API Gateway | $0.50 | $0.50 |
| Bedrock (Claude) | $5-10 | $5-10 |
| Bedrock (Embeddings) | - | $2-5 |
| S3 | - | $1 |
| OpenSearch | - | $10-20 |
| KMS | $1 | $1 |
| **Total** | **~$8.50-16.50** | **~$24.50-47.50** |

> Costs based on moderate usage. Your actual costs may vary.

## Security

- **Encryption at Rest**: All data encrypted with KMS
- **Encryption in Transit**: HTTPS/TLS 1.3
- **IAM**: Least-privilege policies
- **No Hardcoded Secrets**: All credentials via IAM roles
- **Auto Key Rotation**: KMS keys rotate annually
- **Data Retention**: Auto-expire after 30 days (configurable)

## Monitoring

### CloudWatch Logs

```bash
# View chat handler logs
aws logs tail /aws/lambda/chatbot-chat-dev --follow

# Filter errors
aws logs filter-pattern /aws/lambda/chatbot-chat-dev --filter-pattern "ERROR"
```

### Metrics

- Lambda invocations, errors, duration
- DynamoDB read/write capacity
- API Gateway 4xx/5xx errors
- Bedrock token usage

## Troubleshooting

### Common Issues

**"Unable to import module 'handler'"**
- Solution: Run `./scripts/package-lambdas.sh dev`

**"AccessDeniedException: User is not authorized to perform: bedrock:InvokeModel"**
- Solution: Request Bedrock model access in AWS Console
- Go to Bedrock → Model access → Request access

**"Stack is in ROLLBACK_COMPLETE state"**
- Solution: Delete and redeploy
  ```bash
  aws cloudformation delete-stack --stack-name chatbot-dev
  aws cloudformation wait stack-delete-complete --stack-name chatbot-dev
  ./scripts/deploy.sh dev
  ```

## Cleanup

Remove all resources:

```bash
./scripts/cleanup.sh dev
```

This will:
1. Delete CloudFormation stack
2. Remove build artifacts
3. Clean up S3 buckets

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide
- [API Documentation](docs/API.md) - API reference

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file

## Support

- **Issues**: https://github.com/yourusername/pai/issues
- **Discussions**: https://github.com/yourusername/pai/discussions

## Roadmap

- [x] Phase 1: Simple chatbot (MVP)
- [ ] Phase 2: RAG capabilities
- [ ] Web UI (React + CloudFront)
- [ ] Streaming responses
- [ ] Multi-user support
- [ ] Voice interface
- [ ] Mobile app

---

**Built with ❤️ using AWS Serverless**

Start simple. Scale smart. 🚀
