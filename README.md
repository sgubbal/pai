# PAI - Personal AI Chatbot

A serverless, cost-effective, and secure personal AI chatbot built on AWS with end-to-end encryption. Built with a modular architecture that can scale from a simple chatbot to a RAG (Retrieval-Augmented Generation) based LLM system.

## Features

- **Serverless Architecture**: 100% serverless using AWS Lambda, API Gateway, and DynamoDB
- **Cost-Effective**: Pay-per-use pricing with auto-scaling
- **End-to-End Encryption**: KMS-based encryption for conversation data
- **Modular Design**: Easy to extend and scale
- **CI/CD Ready**: GitHub Actions for automated deployments
- **Multi-Environment**: Separate dev and prod environments
- **API Key Authentication**: Simple and secure API access
- **Conversation History**: Persistent conversation storage with TTL
- **RAG-Ready**: Architecture designed to easily extend to RAG capabilities

## Architecture

### Current Architecture (Phase 1: Basic Chatbot)

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTPS + API Key
       │
┌──────▼──────────────────────────────────────────────┐
│            API Gateway (REST API)                    │
│  ┌────────────────────────────────────────────┐    │
│  │        Lambda Authorizer                   │    │
│  │  (API Key Validation via Secrets Manager)  │    │
│  └────────────────────────────────────────────┘    │
└──────┬──────────────────────────────────────────────┘
       │
       │
┌──────▼──────────────────────────────────────────────┐
│         Chatbot Lambda Function                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  • Request Parsing                          │   │
│  │  • Conversation Management                  │   │
│  │  • Bedrock Integration                      │   │
│  │  • Response Formatting                      │   │
│  └─────────────────────────────────────────────┘   │
└───┬─────────────────┬──────────────────┬───────────┘
    │                 │                  │
    │                 │                  │
┌───▼──────┐   ┌─────▼────────┐   ┌────▼──────────┐
│   KMS    │   │   DynamoDB   │   │    Bedrock    │
│ (Encrypt)│   │(Conversations)│   │ (Claude 3.5)  │
└──────────┘   └──────────────┘   └───────────────┘
```

### Future Architecture (Phase 2: RAG Extension)

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
┌──────▼──────────────────────────────────────────────┐
│            API Gateway (REST API)                    │
│   /chat  |  /upload  |  /conversations              │
└──────┬────────────┬─────────────────────────────────┘
       │            │
       │            │
┌──────▼─────┐  ┌──▼────────────────┐
│  Chatbot   │  │  Document Ingestion│
│  Lambda    │  │  Lambda            │
└───┬────┬───┘  └──┬────────────────┘
    │    │         │
    │    │         │
┌───▼────▼─────────▼─────────────────────┐
│        Aurora Serverless v2             │
│         (PostgreSQL + pgvector)         │
│  • Document Embeddings                  │
│  • Vector Similarity Search             │
└─────────────────────────────────────────┘
```

## Technology Stack

### Compute
- **AWS Lambda**: Serverless compute (Python 3.12)
- **Amazon Bedrock**: LLM service (Claude 3.5 Sonnet)

### Storage
- **DynamoDB**: Conversation history storage
- **S3**: Lambda deployment packages and future document storage
- **Aurora Serverless v2** (Future): Vector database with pgvector

### Security
- **AWS KMS**: End-to-end encryption
- **AWS Secrets Manager**: API key management
- **IAM**: Fine-grained access control
- **API Gateway Authorizer**: Request authentication

### Infrastructure
- **CloudFormation**: Infrastructure as Code
- **GitHub Actions**: CI/CD pipeline

## Project Structure

```
pai/
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions CI/CD
├── infrastructure/
│   ├── templates/
│   │   ├── main.yaml           # Master stack
│   │   ├── security.yaml       # KMS, Secrets, IAM
│   │   ├── storage.yaml        # DynamoDB, S3
│   │   ├── compute.yaml        # Lambda functions
│   │   └── api.yaml           # API Gateway
│   └── parameters/
│       ├── dev.json           # Dev environment params
│       └── prod.json          # Prod environment params
├── scripts/
│   ├── deploy.sh              # Main deployment script
│   ├── package-lambdas.sh     # Lambda packaging script
│   ├── setup-apigateway-logging.sh  # Enable API Gateway CloudWatch logging
│   └── cleanup.sh             # Stack cleanup script
├── src/
│   ├── chatbot/
│   │   ├── handler.py         # Main Lambda handler
│   │   ├── bedrock_client.py  # Bedrock integration
│   │   └── conversation_manager.py  # DynamoDB operations
│   ├── authorizer/
│   │   └── handler.py         # API key authorizer
│   └── shared/
│       ├── constants.py       # Application constants
│       ├── utils.py          # Helper functions
│       └── encryption.py     # KMS encryption utilities
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── requirements.txt          # Python dependencies
├── requirements-dev.txt      # Dev dependencies
└── README.md                # This file
```

## Prerequisites

1. **AWS Account** with sufficient permissions
2. **AWS CLI** configured with credentials
3. **Python 3.12+** installed
4. **jq** for JSON processing
5. **Git** for version control

## Quick Start

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd pai

# Generate a secure API key
API_KEY=$(openssl rand -base64 32)
echo "Save this API key: $API_KEY"

# Update parameter file
cd infrastructure/parameters
cp dev.json dev.json.backup

# Edit dev.json with your values
vim dev.json  # or your preferred editor
```

Update `dev.json`:
```json
[
  {
    "ParameterKey": "Environment",
    "ParameterValue": "dev"
  },
  {
    "ParameterKey": "ApiKeyValue",
    "ParameterValue": "your-generated-api-key-here"
  },
  {
    "ParameterKey": "S3BucketName",
    "ParameterValue": "pai-deployment-your-account-id"
  }
]
```

### 2. Deploy

```bash
# Deploy to dev environment
./scripts/deploy.sh dev

# Or deploy to prod
./scripts/deploy.sh prod
```

### 3. Test Your Chatbot

```bash
# Get your API endpoint from deployment output
API_ENDPOINT="<your-api-endpoint>"
API_KEY="<your-api-key>"

# Test chat endpoint
curl -X POST $API_ENDPOINT/chat \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me understand AWS Lambda?"
  }'

# Test with conversation continuation
curl -X POST $API_ENDPOINT/chat \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "your-conversation-id",
    "message": "Tell me more about that"
  }'

# Retrieve conversation history
curl -X GET $API_ENDPOINT/conversations/{conversation_id} \
  -H "Authorization: Bearer $API_KEY"
```

## API Reference

### POST /chat

Send a message to the chatbot.

**Request:**
```json
{
  "message": "Your message here",
  "conversation_id": "optional-conversation-id",
  "user_id": "optional-user-id",
  "system_prompt": "optional-system-prompt"
}
```

**Response:**
```json
{
  "conversation_id": "uuid-v4",
  "message": "Assistant response",
  "usage": {
    "input_tokens": 100,
    "output_tokens": 150
  },
  "model": "anthropic.claude-3-5-sonnet-20241022-v2:0"
}
```

### POST /conversations

Create a new conversation.

**Request:**
```json
{
  "user_id": "optional-user-id",
  "initial_message": "optional-initial-message"
}
```

**Response:**
```json
{
  "conversation_id": "uuid-v4",
  "message": "Conversation created successfully"
}
```

### GET /conversations/{conversation_id}

Retrieve conversation history.

**Response:**
```json
{
  "conversation_id": "uuid-v4",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T00:00:00.000Z"
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "timestamp": "2024-01-01T00:00:01.000Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00.000Z",
  "updated_at": "2024-01-01T00:00:01.000Z"
}
```

## CI/CD with GitHub Actions

### Setup GitHub Secrets

Configure these secrets in your GitHub repository:

```
AWS_ACCESS_KEY_ID       # AWS access key
AWS_SECRET_ACCESS_KEY   # AWS secret key
API_KEY                 # Your API key for the chatbot
S3_BUCKET_NAME         # S3 bucket for deployments
```

### Automatic Deployments

- **Push to `develop`**: Deploys to dev environment
- **Push to `main`**: Deploys to prod environment
- **Manual trigger**: Choose environment via GitHub UI

## Cost Optimization

This architecture is designed for minimal cost:

### Estimated Monthly Costs (Low Usage)

| Service | Usage | Cost |
|---------|-------|------|
| API Gateway | 1M requests | $3.50 |
| Lambda | 1M requests, 512MB, 5s avg | $2.08 |
| DynamoDB | On-demand, 1M reads/writes | $1.25 |
| Bedrock | 1M input tokens, 500K output | ~$15 |
| KMS | 10K requests | $0.03 |
| Secrets Manager | 1 secret | $0.40 |
| **Total** | | **~$22.26/month** |

### Cost Saving Tips

1. Adjust Lambda memory based on actual usage
2. Use DynamoDB on-demand pricing for unpredictable traffic
3. Enable TTL on DynamoDB to auto-delete old conversations
4. Set up CloudWatch alarms for cost monitoring
5. Use shorter conversation history limits

## Monitoring and Logging

### CloudWatch Logs

View Lambda logs:
```bash
# Chatbot logs
aws logs tail /aws/lambda/pai-chatbot-dev --follow

# Authorizer logs
aws logs tail /aws/lambda/pai-authorizer-dev --follow

# API Gateway logs
aws logs tail /aws/apigateway/pai-dev --follow
```

### Metrics

Monitor key metrics in CloudWatch:
- API Gateway: Request count, latency, 4xx/5xx errors
- Lambda: Invocations, duration, errors, throttles
- DynamoDB: Read/write capacity, throttled requests
- Bedrock: Model invocations, token usage

## Extending to RAG

To extend this chatbot with RAG capabilities:

### 1. Add Aurora Serverless v2

Create `infrastructure/templates/rag.yaml`:
```yaml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for Aurora Serverless
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  AuroraCluster:
    Type: AWS::RDS::DBCluster
    Properties:
      Engine: aurora-postgresql
      EngineVersion: '15.4'
      DatabaseName: pai_rag
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      ServerlessV2ScalingConfiguration:
        MinCapacity: 0.5
        MaxCapacity: 2
```

### 2. Create Document Ingestion Lambda

```python
# src/rag/ingestion_handler.py
def lambda_handler(event, context):
    # 1. Download document from S3
    # 2. Extract text and chunk
    # 3. Generate embeddings using Bedrock
    # 4. Store in Aurora with pgvector
    pass
```

### 3. Update Chatbot to Use RAG

```python
# src/chatbot/rag_client.py
def retrieve_relevant_docs(query, top_k=5):
    # 1. Generate query embedding
    # 2. Vector similarity search in Aurora
    # 3. Return relevant document chunks
    pass
```

### 4. Deploy RAG Stack

```bash
# Add RAG stack to main.yaml
# Deploy with RAG enabled
./scripts/deploy.sh dev --enable-rag
```

## Security Best Practices

1. **API Keys**: Rotate regularly, use strong random keys
2. **IAM Roles**: Follow principle of least privilege
3. **Encryption**: All data encrypted at rest and in transit
4. **Secrets**: Never commit secrets to Git
5. **VPC**: Consider deploying Lambda in VPC for production
6. **Rate Limiting**: Configure API Gateway throttling
7. **Monitoring**: Set up CloudWatch alarms for anomalies

## Troubleshooting

### Common Issues

**1. Deployment fails with "S3 bucket not found"**
- Ensure the S3 bucket name in parameters file is correct
- The script will create the bucket if it doesn't exist

**2. "Rate limit exceeded" errors**
- Check Bedrock service quotas in your region
- Request quota increase if needed

**3. "Unauthorized" when calling API**
- Verify API key is correct
- Check Authorization header format: `Bearer YOUR_API_KEY`

**4. Lambda timeout errors**
- Increase Lambda timeout in `compute.yaml`
- Optimize Bedrock request/response size

**5. DynamoDB throttling**
- DynamoDB is on-demand, no throttling expected
- Check for provisioned throughput if you switched modes

**6. "CloudWatch Logs role ARN must be set" error**
- API Gateway logging is currently disabled to avoid this error
- To enable logging, run: `./scripts/setup-apigateway-logging.sh`
- Then uncomment `LoggingLevel: INFO` in `infrastructure/templates/api.yaml`
- Redeploy the stack to enable API Gateway logs

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run unit tests
pytest tests/unit -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run linting
flake8 src/ --max-line-length=127
```

### Local Testing

```bash
# Set environment variables
export CONVERSATIONS_TABLE=PAI-Conversations-dev
export KMS_KEY_ID=your-kms-key-id

# Test locally with moto
pytest tests/integration
```

## Cleanup

To delete all resources:

```bash
# Delete dev environment
./scripts/cleanup.sh dev

# Delete prod environment
./scripts/cleanup.sh prod
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file

## Support

For issues and questions:
- GitHub Issues: Create an issue in the repository
- Documentation: Check this README and CloudFormation templates

## Roadmap

- [x] Phase 1: Basic chatbot with Bedrock
- [ ] Phase 2: RAG implementation with Aurora Serverless
- [ ] Phase 3: Multi-modal support (images, audio)
- [ ] Phase 4: Fine-tuning capabilities
- [ ] Phase 5: Agent-based workflows

## Acknowledgments

Built with AWS serverless services and Anthropic Claude via Amazon Bedrock.
