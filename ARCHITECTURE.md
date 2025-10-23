# Personal AI Chatbot Architecture

## Overview
A modular, serverless chatbot built on AWS that starts as a simple conversational AI (Phase 1) and extends to RAG (Retrieval Augmented Generation) capabilities (Phase 2).

## Design Principles
1. **Start Simple, Scale Smart**: MVP first, then add complexity
2. **Modular**: Each component can be enabled/disabled via feature flags
3. **Cost-Effective**: Serverless pay-per-use, ~$5-15/month for MVP
4. **Secure**: End-to-end encryption with KMS
5. **Scalable**: Auto-scaling serverless components
6. **Extensible**: Easy to add new features

---

## Phase 1: Simple Chatbot (MVP)

### Architecture Diagram
```
User → API Gateway (HTTPS) → Lambda (chat-handler) → Bedrock (Claude)
                                  ↓
                             DynamoDB (conversations)
                                  ↓
                             KMS (encryption)
```

### Components

#### 1. API Gateway (HTTP API)
- **Endpoint**: `/chat` (POST)
- **Features**: CORS enabled, throttling, HTTPS only
- **Cost**: ~$0.50/month

#### 2. Lambda Function (chat-handler)
- **Runtime**: Python 3.12, ARM64
- **Memory**: 512MB, Timeout: 30s
- **Responsibilities**:
  - Receive user messages
  - Load conversation history (last 10 messages)
  - Call Bedrock for AI response
  - Save conversation to DynamoDB (encrypted)
- **Cost**: ~$1-3/month

#### 3. DynamoDB (conversations table)
- **Schema**:
  - `conversation_id` (HASH): UUID
  - `timestamp` (RANGE): ISO timestamp
  - `role`: 'user' or 'assistant'
  - `content`: Message (encrypted at application layer)
  - `ttl`: Auto-delete after 30 days
- **Features**: On-demand billing, point-in-time recovery, KMS encryption
- **Cost**: ~$1-2/month

#### 4. Amazon Bedrock
- **Model**: Claude 3.5 Sonnet v2
- **Features**: Conversational AI, context awareness
- **Cost**: ~$5-10/month (500-1000 messages)

#### 5. KMS (Encryption)
- **Key**: Customer-managed, auto-rotation enabled
- **Usage**: Encrypt/decrypt message content
- **Cost**: ~$1/month

### Data Flow (Phase 1)
```
1. User: "What's the weather?"
   ↓
2. API Gateway → Lambda
   ↓
3. Lambda:
   - Load last 10 messages from DynamoDB
   - Prepare prompt with context
   - Call Bedrock API
   - Encrypt response
   - Save to DynamoDB
   ↓
4. Return: "I don't have access to real-time weather..."
```

### Estimated Cost (Phase 1)
| Service | Monthly Cost |
|---------|-------------|
| Lambda | $1-3 |
| DynamoDB | $1-2 |
| API Gateway | $0.50 |
| Bedrock | $5-10 |
| KMS | $1 |
| **Total** | **$8.50-16.50** |

---

## Phase 2: RAG Extension

### Architecture Diagram
```
User → API Gateway → Lambda (chat-handler) → Bedrock (Claude + Context)
                          ↓                        ↑
                     DynamoDB                 Retrieved Context
                                                    |
Document → S3 → Lambda (ingestion) → Bedrock (Embeddings)
                                           ↓
                                  OpenSearch Serverless
                                           ↓
                      Lambda (retrieval) ─────┘
```

### Additional Components

#### 6. S3 Bucket (documents)
- **Purpose**: Store user documents (PDF, TXT, MD)
- **Features**: Versioning, KMS encryption, Intelligent-Tiering
- **Cost**: ~$1/month

#### 7. Lambda (ingestion-handler)
- **Trigger**: S3 upload event
- **Runtime**: Python 3.12, ARM64
- **Memory**: 1024MB, Timeout: 5min
- **Responsibilities**:
  - Download document from S3
  - Chunk into 512-token segments
  - Generate embeddings via Bedrock
  - Store vectors in OpenSearch
- **Cost**: ~$2-3/month

#### 8. Lambda (retrieval-handler)
- **Runtime**: Python 3.12, ARM64
- **Memory**: 512MB, Timeout: 30s
- **Responsibilities**:
  - Generate query embedding
  - Search OpenSearch for top-5 relevant chunks
  - Return context to chat-handler
- **Cost**: ~$1-2/month

#### 9. OpenSearch Serverless
- **Collection**: `chatbot-vectors-{env}`
- **Type**: Vector search
- **Features**: Cosine similarity, HNSW algorithm
- **Cost**: ~$10-20/month (2 OCUs minimum)

#### 10. Bedrock Embeddings
- **Model**: Titan Embeddings v2
- **Dimension**: 1024
- **Cost**: ~$2-5/month

### Data Flow (Phase 2)

#### Ingestion Flow
```
1. User uploads: "my_resume.pdf" → S3
   ↓
2. S3 Event → Lambda (ingestion)
   ↓
3. Lambda:
   - Download PDF
   - Extract text
   - Chunk into segments
   - For each chunk:
     * Generate embedding via Bedrock
     * Store in OpenSearch with metadata
   ↓
4. Document indexed and searchable
```

#### Retrieval Flow
```
1. User: "What programming languages do I know?"
   ↓
2. API Gateway → Lambda (chat)
   ↓
3. Lambda calls retrieval-handler:
   - Generate query embedding
   - Search OpenSearch
   - Return top-5 chunks from resume
   ↓
4. Lambda (chat):
   - Combine retrieved context + conversation history
   - Call Bedrock with enhanced prompt
   - Save response
   ↓
5. Return: "Based on your resume, you know Python, Java..."
```

### Estimated Cost (Phase 2)
| Service | Monthly Cost |
|---------|-------------|
| Phase 1 Total | $8.50-16.50 |
| S3 | $1 |
| Lambda (ingestion) | $2-3 |
| Lambda (retrieval) | $1-2 |
| OpenSearch | $10-20 |
| Bedrock Embeddings | $2-5 |
| **Total** | **$25-47.50** |

---

## Security Architecture

### Encryption
- **At Rest**: KMS-encrypted DynamoDB, S3, OpenSearch
- **In Transit**: HTTPS/TLS 1.3 for all API calls
- **Application Layer**: Encrypt message content before storage

### IAM Policies (Least Privilege)
```yaml
Lambda Execution Role:
  - DynamoDB: PutItem, Query on chatbot tables
  - S3: GetObject, PutObject on chatbot bucket
  - KMS: Encrypt, Decrypt with chatbot key
  - Bedrock: InvokeModel (Claude, Titan)
  - OpenSearch: Write, Search (Phase 2)
  - CloudWatch: PutLogEvents
```

### Authentication (Future)
- API Key authentication (simple)
- Cognito User Pools (multi-user)
- JWT tokens for session management

---

## Infrastructure as Code

### CloudFormation Stack Structure
```
infra/cloudformation/
├── main.yaml              # Orchestrator (nested stacks)
├── security.yaml          # KMS, IAM roles
├── storage.yaml           # DynamoDB, S3
├── compute.yaml           # Lambda, API Gateway
└── ai.yaml                # OpenSearch (conditional)
```

### Feature Flags (Parameters)
```yaml
Parameters:
  EnableRAG:
    Type: String
    Default: "false"
    AllowedValues: ["true", "false"]

  Environment:
    Type: String
    Default: "dev"
    AllowedValues: ["dev", "staging", "prod"]
```

### Conditional Resources
```yaml
Conditions:
  IsRAGEnabled: !Equals [!Ref EnableRAG, "true"]

Resources:
  OpenSearchCollection:
    Type: AWS::OpenSearchServerless::Collection
    Condition: IsRAGEnabled  # Only created if EnableRAG=true
```

---

## Application Code Structure

```
src/
├── chatbot/               # Phase 1
│   ├── handler.py         # Lambda entry point
│   ├── llm_service.py     # Bedrock integration
│   ├── conversation_service.py  # DynamoDB operations
│   └── models.py          # Pydantic data models
│
├── rag/                   # Phase 2 (optional)
│   ├── ingestion_handler.py    # Document processing
│   ├── retrieval_handler.py    # Vector search
│   ├── embedding_service.py    # Bedrock embeddings
│   └── document_processor.py   # Chunking logic
│
└── shared/
    ├── encryption.py      # KMS encrypt/decrypt
    ├── config.py          # Environment variables
    └── logger.py          # Structured logging
```

---

## Deployment Strategy

### CI/CD Pipeline (GitHub Actions)
```
Push to main → GitHub Actions
    ↓
[Validate]
 - Lint Python (ruff)
 - Type check (mypy)
 - Validate CloudFormation
    ↓
[Test]
 - Unit tests (pytest)
 - Integration tests (moto)
    ↓
[Build]
 - Package Lambda functions
 - Install dependencies (ARM64)
    ↓
[Deploy]
 - Deploy CloudFormation
 - Update Lambda code
 - Run smoke tests
```

### Deployment Scripts
```bash
scripts/
├── deploy.sh              # Deploy infrastructure
├── package-lambdas.sh     # Build and upload Lambda code
├── cleanup.sh             # Destroy stack
├── test.sh                # Run smoke tests
└── enable-rag.sh          # Enable RAG (Phase 2)
```

### Deployment Commands
```bash
# Phase 1: Deploy simple chatbot
./scripts/deploy.sh dev

# Package and deploy Lambda code
./scripts/package-lambdas.sh dev

# Test deployment
./scripts/test.sh dev

# Phase 2: Enable RAG
./scripts/enable-rag.sh dev
```

---

## Modularity & Scalability

### How to Enable RAG
```bash
# Option 1: CLI
aws cloudformation update-stack \
  --stack-name chatbot-dev \
  --parameters ParameterKey=EnableRAG,ParameterValue=true

# Option 2: Script
./scripts/enable-rag.sh dev

# Option 3: Update parameter in GitHub Actions
# Edit .github/workflows/deploy.yaml
# Change: EnableRAG: "true"
```

### Scaling Considerations

#### Current (Single User)
- No authentication
- Simple conversation management
- Direct Lambda invocation

#### Future (Multi-User)
**Changes Needed**:
1. Add Cognito User Pools
2. Update DynamoDB schema:
   ```
   HASH: user_id
   RANGE: conversation_id#timestamp
   ```
3. Add API authorization
4. Implement per-user rate limiting
5. Isolate user data (S3 prefixes, DynamoDB filters)

---

## Monitoring & Observability

### CloudWatch Dashboards
```
- Lambda invocations, errors, duration
- DynamoDB read/write capacity
- API Gateway 4xx/5xx errors
- Bedrock token usage
- OpenSearch query performance
```

### Alarms
```yaml
HighErrorRate:
  Metric: Lambda Errors
  Threshold: > 5%
  Action: Email notification

HighLatency:
  Metric: API Gateway Latency
  Threshold: > 2 seconds
  Action: Email notification

HighCost:
  Metric: Estimated Charges
  Threshold: > $50
  Action: Email notification
```

### Logging Strategy
```python
# Structured JSON logs
{
  "timestamp": "2025-10-22T10:30:00Z",
  "level": "INFO",
  "conversation_id": "uuid-1234",
  "event": "message_sent",
  "duration_ms": 1250,
  "bedrock_tokens": 450
}
```

---

## Testing Strategy

### Unit Tests
```python
tests/
├── test_llm_service.py
├── test_conversation_service.py
├── test_encryption.py
└── test_rag_retrieval.py
```

### Integration Tests (moto)
```python
# Mock AWS services
@mock_dynamodb
@mock_s3
@mock_bedrock
def test_end_to_end_chat():
    # Test complete chat flow
    pass
```

### Smoke Tests
```bash
# Test deployed endpoints
curl -X POST https://api.example.com/chat \
  -H "Content-Type: application/json" \
  -d '{"conversation_id": "test", "message": "Hello"}'
```

---

## Migration Path: Phase 1 → Phase 2

### Step-by-Step
1. **Deploy Phase 1** (simple chatbot)
   ```bash
   ./scripts/deploy.sh dev
   ```

2. **Test and validate** MVP functionality
   ```bash
   ./scripts/test.sh dev
   ```

3. **Enable RAG** when ready
   ```bash
   ./scripts/enable-rag.sh dev
   ```

4. **Upload documents**
   ```bash
   aws s3 cp my_docs/ s3://chatbot-docs-dev/ --recursive
   ```

5. **Test RAG** functionality
   ```bash
   curl -X POST https://api.example.com/chat \
     -d '{"message": "What documents do I have?"}'
   ```

### Zero Downtime
- CloudFormation updates are rolling
- Lambda versions ensure no disruption
- DynamoDB is always available

---

## Future Enhancements

### Short Term
- [ ] Streaming responses (Server-Sent Events)
- [ ] Conversation export (JSON/PDF)
- [ ] Multi-turn context management
- [ ] Rate limiting per IP

### Medium Term
- [ ] Web UI (React + S3 + CloudFront)
- [ ] API key management
- [ ] Usage analytics dashboard
- [ ] Document format support (DOCX, images)

### Long Term
- [ ] Multi-user with Cognito
- [ ] Voice interface (Transcribe + Polly)
- [ ] Multi-modal support (images, video)
- [ ] Fine-tuned models
- [ ] GraphRAG implementation

---

## Repository Structure

```
/
├── .github/
│   └── workflows/
│       └── deploy.yaml          # CI/CD pipeline
├── infra/
│   └── cloudformation/
│       ├── main.yaml            # Stack orchestrator
│       ├── security.yaml        # KMS, IAM
│       ├── storage.yaml         # DynamoDB, S3
│       ├── compute.yaml         # Lambda, API Gateway
│       └── ai.yaml              # OpenSearch (conditional)
├── src/
│   ├── chatbot/
│   │   ├── handler.py           # Chat Lambda
│   │   ├── llm_service.py       # Bedrock integration
│   │   ├── conversation_service.py
│   │   └── models.py
│   ├── rag/
│   │   ├── ingestion_handler.py
│   │   ├── retrieval_handler.py
│   │   ├── embedding_service.py
│   │   └── document_processor.py
│   └── shared/
│       ├── encryption.py
│       ├── config.py
│       └── logger.py
├── scripts/
│   ├── deploy.sh
│   ├── package-lambdas.sh
│   ├── cleanup.sh
│   ├── test.sh
│   └── enable-rag.sh
├── tests/
│   ├── unit/
│   └── integration/
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── ARCHITECTURE.md
├── DEPLOYMENT.md
└── .gitignore
```

---

## Conclusion

This architecture provides:
✅ **Simple start**: Deploy a working chatbot in < 15 minutes
✅ **Easy extension**: Enable RAG with one command
✅ **Cost-effective**: ~$10/month for MVP, ~$30/month with RAG
✅ **Secure**: End-to-end encryption, least-privilege IAM
✅ **Scalable**: Serverless auto-scaling
✅ **Production-ready**: CI/CD, monitoring, testing included

Perfect for a personal AI chatbot that grows with your needs.
