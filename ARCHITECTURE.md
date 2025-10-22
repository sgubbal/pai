# PAI Architecture

## Overview

Personal AI Agent (PAI) is a serverless, cost-effective, and secure AI assistant platform built entirely on AWS infrastructure with end-to-end encryption.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  (Future: Web App, Mobile App, CLI, Browser Extension)         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API Gateway (HTTP API)                       │
│              - Cost-optimized alternative to REST                │
│              - TLS encryption in transit                         │
└───────┬─────────────────┬─────────────────┬─────────────────────┘
        │                 │                 │
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
│ Chat Lambda   │  │Memory Lambda │  │VectorSearch      │
│  (512 MB)     │  │  (1024 MB)   │  │Lambda (2048 MB)  │
│               │  │              │  │                  │
│ - ARM64       │  │ - ARM64      │  │ - ARM64          │
│ - Node 20     │  │ - Node 20    │  │ - Node 20        │
└───────┬───────┘  └───────┬──────┘  └────────┬─────────┘
        │                  │                   │
        │                  │                   │
        ▼                  ▼                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  DynamoDB        │  │  DynamoDB        │  │  S3 Bucket   │ │
│  │  Short-term      │  │  Long-term       │  │  Knowledge   │ │
│  │  Memory          │  │  Memory          │  │  Base        │ │
│  │                  │  │                  │  │              │ │
│  │ - Conversations  │  │ - Embeddings     │  │ - Files      │ │
│  │ - TTL 24h        │  │ - Vector search  │  │ - Documents  │ │
│  │ - On-demand      │  │ - On-demand      │  │ - Encrypted  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             │ Encryption
                             ▼
                    ┌────────────────┐
                    │   AWS KMS      │
                    │ Envelope       │
                    │ Encryption     │
                    └────────────────┘
```

## Components

### 1. API Gateway (HTTP API)

- **Type**: HTTP API (cheaper than REST API)
- **Cost**: ~$1 per million requests
- **Features**:
  - TLS 1.2+ encryption
  - CORS enabled for web clients
  - CloudWatch logging
  - No authentication (single-user MVP)

**Endpoints**:
- `POST /chat` - Chat with AI agent
- `POST /memory` - Manage memory (store/retrieve)
- `POST /search` - Vector similarity search

### 2. Lambda Functions

#### Chat Function
- **Memory**: 512 MB
- **Timeout**: 30 seconds
- **Purpose**: Handle chat requests, integrate with LLM
- **Architecture**: ARM64 (20% cheaper)

#### Memory Function
- **Memory**: 1024 MB
- **Timeout**: 60 seconds
- **Purpose**: Store and retrieve memories, manage embeddings
- **Architecture**: ARM64

#### Vector Search Function
- **Memory**: 2048 MB
- **Timeout**: 60 seconds
- **Purpose**: Semantic search using cosine similarity
- **Architecture**: ARM64

**Cost Optimization**:
- ARM64 architecture (20% cost reduction)
- Reserved concurrency limits prevent runaway costs
- Right-sized memory allocations
- Efficient cold starts with minimal dependencies

### 3. Storage Layer

#### Short-term Memory (DynamoDB)

**Table**: `pai-conversations-{env}`

**Schema**:
```
- sessionId (HASH)
- timestamp (RANGE)
- role (user/assistant/system)
- encryptedContent (encrypted message)
- ttl (24 hours)
```

**Features**:
- On-demand billing
- TTL for automatic cleanup
- KMS encryption at rest
- Point-in-time recovery

**Use Case**: Store recent conversation history

#### Long-term Memory (DynamoDB)

**Table**: `pai-knowledge-{env}`

**Schema**:
```
- id (HASH)
- category (GSI HASH)
- timestamp (GSI RANGE)
- encryptedContent (encrypted text)
- embedding (384-dimensional vector)
- encryptedMetadata
```

**Features**:
- On-demand billing
- Global Secondary Index for category queries
- KMS encryption at rest
- Vector embeddings for semantic search

**Use Case**: Persistent knowledge base with semantic search

#### Knowledge Base (S3)

**Bucket**: `pai-knowledge-base-{account}-{env}`

**Features**:
- Server-side encryption with KMS
- Versioning enabled
- Intelligent-Tiering storage class
- Block all public access

**Use Case**: Store documents, files, and large content

### 4. Security Layer

#### AWS KMS

**Key**: `alias/pai-{env}`

**Encryption Strategy**: Envelope Encryption
1. Generate data key from KMS
2. Encrypt data with data key (AES-256-GCM)
3. Encrypt data key with KMS master key
4. Store encrypted data + encrypted data key

**Benefits**:
- No data sent to KMS (only key encryption)
- Client-side encryption
- Audit trail via CloudTrail
- Key rotation support

#### IAM Roles

**Lambda Execution Role**:
- DynamoDB: Read/Write to tables
- S3: Read/Write to knowledge base
- KMS: Encrypt/Decrypt operations
- CloudWatch: Log writing

**Principle of Least Privilege**: Each function only has access to required resources

## Data Flow

### Chat Request Flow

1. Client sends POST to `/chat`
2. API Gateway routes to Chat Lambda
3. Chat Lambda:
   - Encrypts user message
   - Stores in short-term memory
   - Retrieves conversation history
   - Optionally searches knowledge base
   - Calls LLM API (TODO)
   - Encrypts and stores AI response
4. Returns response to client

### Memory Storage Flow

1. Client sends POST to `/memory` with action="store"
2. API Gateway routes to Memory Lambda
3. Memory Lambda:
   - Generates embedding vector
   - Encrypts content and metadata
   - Stores in long-term memory DynamoDB
4. Returns success with knowledge ID

### Vector Search Flow

1. Client sends POST to `/search`
2. API Gateway routes to Vector Search Lambda
3. Vector Search Lambda:
   - Generates query embedding
   - Scans DynamoDB for vectors
   - Calculates cosine similarity
   - Returns top K results sorted by relevance
4. Returns matching knowledge items

## Encryption Architecture

### Envelope Encryption Flow

```
Plaintext Data
     │
     ▼
┌─────────────────┐
│ Generate Data   │──────KMS──────┐
│ Key (AES-256)   │               │
└────────┬────────┘               │
         │                        │
         ▼                        ▼
┌─────────────────┐      ┌────────────────┐
│ Encrypt Data    │      │ Encrypt Data   │
│ with Data Key   │      │ Key with KMS   │
└────────┬────────┘      └────────┬───────┘
         │                        │
         ▼                        ▼
┌─────────────────────────────────────────┐
│  Store in DynamoDB/S3:                   │
│  - Ciphertext                            │
│  - Encrypted Data Key                    │
│  - IV (Initialization Vector)            │
│  - Auth Tag (for AES-GCM)                │
└──────────────────────────────────────────┘
```

**Benefits**:
- True end-to-end encryption
- No plaintext stored anywhere
- KMS never sees actual data
- Perfect forward secrecy

## Cost Analysis

### Monthly Cost Breakdown (Single User, Moderate Usage)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 100K requests, 1GB-sec avg | $0.20 |
| API Gateway | 100K requests | $0.10 |
| DynamoDB | 50K writes, 200K reads | $0.50 |
| S3 | 1 GB storage | $0.02 |
| KMS | 1 key, 1K requests | $1.00 |
| CloudWatch Logs | 1 GB | $0.50 |
| **Total** | | **~$2.32/month** |

**Free Tier Benefits** (first 12 months):
- Lambda: 1M requests/month free
- DynamoDB: 25 GB storage, 200M requests free
- S3: 5 GB storage free
- **Estimated First Year Cost**: < $1/month

### Cost Scaling

| Usage Level | Monthly Cost |
|-------------|--------------|
| Light (100K req) | $1-2 |
| Moderate (500K req) | $3-5 |
| Heavy (2M req) | $10-15 |

## Future Enhancements

### Phase 1: LLM Integration
- [ ] OpenAI GPT-4 integration
- [ ] AWS Bedrock (Claude/Titan) integration
- [ ] Streaming responses

### Phase 2: Advanced Features
- [ ] Multi-modal support (images, audio)
- [ ] Advanced vector search with HNSW
- [ ] Redis caching layer
- [ ] WebSocket support for real-time chat

### Phase 3: Production Ready
- [ ] API authentication (JWT, API keys)
- [ ] Rate limiting
- [ ] WAF integration
- [ ] CloudFront CDN
- [ ] Multi-region deployment
- [ ] VPC deployment option

### Phase 4: UI/UX
- [ ] Web frontend (React/Next.js)
- [ ] Mobile app (React Native)
- [ ] Browser extension
- [ ] CLI tool

## Monitoring and Observability

### CloudWatch Metrics
- Lambda invocations, errors, duration
- API Gateway requests, 4XX, 5XX errors
- DynamoDB read/write capacity
- S3 request counts

### CloudWatch Logs
- Lambda execution logs
- API Gateway access logs
- Custom application logs

### Alarms (Future)
- Lambda error rate > 5%
- API Gateway 5XX errors
- DynamoDB throttling events
- High cost anomalies

## Disaster Recovery

### Backup Strategy
- DynamoDB: Point-in-time recovery (PITR) enabled
- S3: Versioning enabled
- CloudFormation: Infrastructure as Code

### Recovery Procedure
1. Redeploy CloudFormation stack
2. Restore DynamoDB from PITR
3. S3 data automatically available (versioned)

**RTO**: ~10 minutes
**RPO**: ~1 minute (PITR granularity)

## Security Best Practices

✅ Implemented:
- End-to-end encryption (KMS)
- TLS in transit
- Least privilege IAM roles
- No public S3 access
- Encryption at rest
- CloudWatch logging

⚠️ TODO for Production:
- API authentication
- WAF rules
- VPC deployment
- Secrets Manager for API keys
- CloudTrail audit logging
- GuardDuty threat detection

## Compliance Considerations

- **GDPR**: Data encryption, right to deletion (destroy script)
- **HIPAA**: Encryption at rest/transit (not HIPAA-compliant without BAA)
- **SOC 2**: Audit logging, access controls
- **Data Residency**: Single region deployment

## Performance Characteristics

- **Cold Start**: ~500ms (Lambda)
- **Warm Request**: ~50-200ms (without LLM)
- **LLM Latency**: 1-5 seconds (depending on provider)
- **Vector Search**: <500ms for <10K vectors
- **Throughput**: ~1000 req/sec (API Gateway limit)

## Scalability

- **Horizontal**: Lambda auto-scales to 1000 concurrent executions
- **Vertical**: Increase Lambda memory as needed
- **Database**: DynamoDB auto-scales with on-demand mode
- **Storage**: S3 unlimited storage
- **Bottlenecks**: Vector search at >100K vectors (consider OpenSearch)

## Technology Stack

- **Infrastructure**: AWS CloudFormation
- **Compute**: AWS Lambda (Node.js 20, ARM64)
- **API**: API Gateway HTTP API
- **Database**: DynamoDB
- **Storage**: S3
- **Security**: KMS, IAM
- **Monitoring**: CloudWatch
- **CI/CD**: GitHub Actions
- **Language**: TypeScript
- **Runtime**: Node.js 20.x

## License

MIT License (or your preferred license)
