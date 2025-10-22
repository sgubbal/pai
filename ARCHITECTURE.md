# PAI Agent Architecture

Technical architecture documentation for the Personal AI Agent.

## System Overview

PAI is a serverless personal AI agent built on AWS, designed for cost-effectiveness, security, and scalability.

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│                  (Future: Web/Mobile App)                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTPS
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                   API Gateway (HTTP API)                     │
│                    - /chat (POST)                            │
│                    - /search (POST)                          │
│                    - /memory/* (GET)                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Invoke
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    Lambda Functions                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │   Agent    │  │   Memory   │  │   Search   │            │
│  │  Handler   │  │  Handler   │  │  Handler   │            │
│  └──────┬─────┘  └──────┬─────┘  └──────┬─────┘            │
│         │                │                │                  │
└─────────┼────────────────┼────────────────┼──────────────────┘
          │                │                │
          │                │                │
    ┌─────▼────────────────▼────────────────▼─────┐
    │                                              │
    │           Service Layer                      │
    │  ┌──────────────┐  ┌──────────────┐         │
    │  │  AI Service  │  │Memory Service│         │
    │  │  (Bedrock)   │  │(DynamoDB/S3) │         │
    │  └──────────────┘  └──────────────┘         │
    │  ┌──────────────┐  ┌──────────────┐         │
    │  │Vector Service│  │  Encryption  │         │
    │  │ (OpenSearch) │  │(KMS Service) │         │
    │  └──────────────┘  └──────────────┘         │
    │                                              │
    └─────────┬────────────────┬───────────────────┘
              │                │
    ┌─────────▼────────┐  ┌───▼──────────────┐
    │                  │  │                   │
    │  AWS Services    │  │  Storage Layer    │
    │                  │  │                   │
    │  ┌────────────┐  │  │  ┌────────────┐  │
    │  │  Bedrock   │  │  │  │ DynamoDB   │  │
    │  │  Claude 3  │  │  │  │ (Tables)   │  │
    │  │  Titan     │  │  │  └────────────┘  │
    │  └────────────┘  │  │  ┌────────────┐  │
    │  ┌────────────┐  │  │  │     S3     │  │
    │  │ OpenSearch │  │  │  │  (Bucket)  │  │
    │  │ Serverless │  │  │  └────────────┘  │
    │  └────────────┘  │  │  ┌────────────┐  │
    │  ┌────────────┐  │  │  │    KMS     │  │
    │  │    KMS     │  │  │  │   (Keys)   │  │
    │  └────────────┘  │  │  └────────────┘  │
    │                  │  │                   │
    └──────────────────┘  └───────────────────┘
```

## Components

### 1. API Gateway (HTTP API)

**Purpose**: Entry point for all client requests

**Features**:
- HTTP API (cheaper than REST API)
- CORS enabled for future web frontend
- Throttling configured (10 req/s, 20 burst)
- Direct Lambda proxy integration

**Endpoints**:
- `POST /chat`: Send messages to AI agent
- `POST /search`: Semantic search across memories
- `GET /memory/{id}`: Retrieve conversation history

### 2. Lambda Functions

#### Agent Lambda (`pai-agent-{env}`)

**Purpose**: Main AI agent orchestrator

**Responsibilities**:
- Receive user messages
- Manage conversation context
- Query relevant memories
- Call Bedrock for AI responses
- Save conversation history
- Store important exchanges in long-term memory

**Configuration**:
- Runtime: Python 3.11
- Architecture: ARM64 (cost optimization)
- Memory: 512 MB
- Timeout: 60 seconds

**Environment Variables**:
- `CONVERSATIONS_TABLE`
- `MEMORIES_TABLE`
- `MEMORY_BUCKET`
- `VECTOR_SEARCH_ENDPOINT`
- `KMS_KEY_ID`
- `AI_MODEL_ID`
- `EMBEDDING_MODEL_ID`

#### Memory Lambda (`pai-memory-{env}`)

**Purpose**: Memory management operations

**Responsibilities**:
- Retrieve conversation history
- List memories by category
- Manage memory metadata

**Configuration**:
- Runtime: Python 3.11
- Architecture: ARM64
- Memory: 256 MB
- Timeout: 30 seconds

#### Search Lambda (`pai-search-{env}`)

**Purpose**: Semantic search

**Responsibilities**:
- Generate query embeddings
- Search vector database
- Return ranked results

**Configuration**:
- Runtime: Python 3.11
- Architecture: ARM64
- Memory: 512 MB
- Timeout: 30 seconds

### 3. Storage Layer

#### DynamoDB Tables

**Conversations Table** (`pai-conversations-{env}`):
- **Purpose**: Short-term conversation memory
- **Schema**:
  - `conversation_id` (HASH): Unique conversation identifier
  - `timestamp` (RANGE): Message timestamp
  - `message_id`: Unique message identifier
  - `role`: 'user' or 'assistant'
  - `content`: Message content (encrypted)
  - `ttl`: Auto-deletion timestamp (7 days default)
- **Features**:
  - Point-in-time recovery enabled
  - KMS encryption
  - TTL enabled for automatic cleanup

**Memories Table** (`pai-memories-{env}`):
- **Purpose**: Long-term memory metadata
- **Schema**:
  - `memory_id` (HASH): Unique memory identifier
  - `content`: Memory summary
  - `category`: Memory category
  - `created_at`: Creation timestamp
  - `s3_key`: S3 key for full content
  - `ttl`: Auto-deletion timestamp (365 days default)
- **GSI**: `category-created_at-index`
- **Features**:
  - Point-in-time recovery enabled
  - KMS encryption
  - TTL enabled

#### S3 Bucket

**Long-term Memory Bucket** (`pai-long-term-memory-{account}-{env}`):
- **Purpose**: Persistent storage for full memory content
- **Features**:
  - Versioning enabled
  - KMS encryption
  - Intelligent-Tiering lifecycle policy
  - Public access blocked
- **Structure**:
  ```
  s3://pai-long-term-memory-{account}-{env}/
  └── memories/
      ├── mem-{uuid}.json
      └── mem-{uuid}.json
  ```

### 4. AI Services

#### Amazon Bedrock

**Models Used**:
1. **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - Purpose: Conversational AI
   - Max tokens: 2048 (configurable)
   - Context window: Up to 20 messages

2. **Titan Embeddings V2** (`amazon.titan-embed-text-v2:0`)
   - Purpose: Generate vector embeddings
   - Dimension: 1024
   - Use: Semantic search, memory indexing

**Integration**:
- Direct SDK integration (boto3)
- No API keys required (IAM role-based)
- Regional endpoints

#### OpenSearch Serverless

**Collection**: `pai-vectors-{env}`

**Purpose**: Vector database for semantic search

**Configuration**:
- Type: VECTORSEARCH
- Vector dimension: 1024
- Algorithm: HNSW (Hierarchical Navigable Small World)
- Similarity: Cosine similarity

**Index Schema**:
```json
{
  "memory_id": "keyword",
  "content": "text",
  "category": "keyword",
  "created_at": "long",
  "metadata": "object",
  "embedding": {
    "type": "knn_vector",
    "dimension": 1024,
    "method": {
      "name": "hnsw",
      "space_type": "cosinesimil",
      "engine": "nmslib"
    }
  }
}
```

### 5. Security

#### KMS Encryption

**Key**: `pai-encryption-{env}`

**Purpose**: End-to-end encryption of sensitive data

**Usage**:
- Encrypt message content before DynamoDB storage
- Encrypt memory content before S3 storage
- Encrypt/decrypt operations via service layer

**Features**:
- Automatic key rotation enabled
- AWS-owned CMK (Customer Master Key)
- Regional key

#### IAM Roles

**Lambda Execution Role** (`pai-lambda-execution-role-{env}`):

**Permissions**:
- DynamoDB: Read/Write to PAI tables
- S3: Read/Write to PAI buckets
- KMS: Encrypt/Decrypt operations
- Bedrock: InvokeModel for AI operations
- OpenSearch: APIAccessAll for vector search
- CloudWatch Logs: Write logs

**Trust Policy**: Lambda service

### 6. Service Layer (Python)

#### AIService (`src/services/ai_service.py`)

**Responsibilities**:
- Interface with Bedrock models
- Generate chat responses
- Create vector embeddings

**Key Methods**:
- `chat()`: Send messages and get AI responses
- `generate_embedding()`: Create vector embeddings
- `batch_generate_embeddings()`: Bulk embedding generation

#### MemoryService (`src/services/memory_service.py`)

**Responsibilities**:
- Manage conversations in DynamoDB
- Store/retrieve memories from S3
- Handle encryption/decryption

**Key Methods**:
- `save_message()`: Store message in short-term memory
- `get_conversation()`: Retrieve conversation history
- `save_memory()`: Store memory in long-term storage
- `get_memory()`: Retrieve specific memory
- `list_memories()`: List memories by category

#### VectorService (`src/services/vector_service.py`)

**Responsibilities**:
- Manage OpenSearch index
- Index memory vectors
- Perform semantic search

**Key Methods**:
- `create_index()`: Initialize vector index
- `index_memory()`: Add memory to vector database
- `search()`: Semantic search for similar memories
- `delete_memory()`: Remove memory from index

#### EncryptionService (`src/services/encryption.py`)

**Responsibilities**:
- Encrypt/decrypt data using KMS
- Manage encryption keys

**Key Methods**:
- `encrypt()`: Encrypt plaintext
- `decrypt()`: Decrypt ciphertext
- `generate_data_key()`: Create data encryption keys

## Data Flow

### 1. Chat Request Flow

```
1. User sends message → API Gateway
2. API Gateway → Agent Lambda
3. Agent Lambda:
   a. Save user message to Conversations table (encrypted)
   b. Retrieve conversation history from DynamoDB
   c. Generate query embedding via Bedrock
   d. Search for relevant memories in OpenSearch
   e. Construct context with history + memories
   f. Call Bedrock for AI response
   g. Save AI response to Conversations table
   h. Create memory of exchange
   i. Generate embedding for memory
   j. Save memory to S3 + DynamoDB
   k. Index memory in OpenSearch
4. Return response to user
```

### 2. Search Request Flow

```
1. User sends search query → API Gateway
2. API Gateway → Search Lambda
3. Search Lambda:
   a. Generate query embedding via Bedrock
   b. Query OpenSearch vector database
   c. Retrieve matching memories
   d. Rank by similarity score
4. Return ranked results to user
```

### 3. Memory Retrieval Flow

```
1. User requests conversation → API Gateway
2. API Gateway → Memory Lambda
3. Memory Lambda:
   a. Query Conversations table by ID
   b. Decrypt message content
   c. Sort by timestamp
4. Return conversation history to user
```

## Scalability Considerations

### Current Design (Single User)

- No authentication required
- Simple conversation ID system
- Direct Lambda invocation

### Future Multi-User Support

**Required Changes**:
1. Add Amazon Cognito for authentication
2. Add user_id to all table partition keys
3. Implement API authorization
4. Add per-user rate limiting
5. Implement user-specific memory isolation

**Schema Changes**:
```python
# Conversations table
HASH: user_id
RANGE: conversation_id#timestamp

# Memories table
HASH: user_id
RANGE: memory_id
```

## Performance Optimization

### Lambda Cold Start Mitigation

- Use ARM64 architecture (faster cold starts)
- Optimize package size
- Use Lambda layers for common dependencies
- Consider provisioned concurrency for production

### DynamoDB Optimization

- Use on-demand billing (no capacity planning)
- Enable DAX (DynamoDB Accelerator) if needed
- Implement batch operations where possible
- Use projections in GSI to reduce read costs

### S3 Optimization

- Enable Intelligent-Tiering
- Use multipart upload for large objects
- Implement lifecycle policies
- Enable transfer acceleration if needed

### Vector Search Optimization

- Use appropriate k value for search
- Filter by category to reduce search space
- Use ef_search parameter tuning
- Consider index optimization for large datasets

## Monitoring and Observability

### CloudWatch Metrics

**Lambda**:
- Invocations
- Duration
- Errors
- Throttles

**DynamoDB**:
- Read/Write capacity units
- Throttled requests
- User errors

**API Gateway**:
- Request count
- Latency
- 4xx/5xx errors

### Logging Strategy

**Log Levels**:
- ERROR: System errors, exceptions
- INFO: Important events (message saved, search performed)
- DEBUG: Detailed execution information

**Structured Logging**:
- JSON format for easy parsing
- Include conversation_id, user_id, timestamp
- Centralize with CloudWatch Logs Insights

### Tracing

**X-Ray Integration** (Future):
- End-to-end request tracing
- Performance bottleneck identification
- Service map visualization

## Disaster Recovery

### Backup Strategy

**DynamoDB**:
- Point-in-time recovery enabled
- Daily automated backups (AWS Backup)
- 35-day retention

**S3**:
- Versioning enabled
- Cross-region replication (optional)
- Lifecycle policies for cost optimization

### Recovery Procedures

**Complete Stack Failure**:
1. Redeploy CloudFormation stack
2. Restore DynamoDB from backup
3. S3 data persists (versioned)
4. Rebuild OpenSearch index from S3

**Data Corruption**:
1. Use DynamoDB point-in-time recovery
2. Restore specific S3 object versions
3. Regenerate vector embeddings if needed

## Cost Analysis

### Monthly Cost Breakdown (Low Usage)

| Service | Usage | Cost |
|---------|-------|------|
| Lambda | 10K invocations, 512MB, 10s avg | $1-2 |
| DynamoDB | 1M reads, 100K writes | $1-2 |
| S3 | 1GB storage, 10K requests | $0.50 |
| OpenSearch | Serverless OCU | $5-10 |
| Bedrock | 1M tokens (~500 conversations) | $5-15 |
| KMS | 10K requests | $0.03 |
| API Gateway | 10K requests | $0.01 |
| **Total** | | **~$15-30/month** |

### Cost Optimization Strategies

1. **Use ARM64 Lambda**: 20% cost reduction
2. **Optimize token usage**: Reduce context window when possible
3. **TTL for old data**: Automatic cleanup reduces storage costs
4. **Batch operations**: Reduce API calls
5. **On-demand pricing**: Pay only for what you use

## Security Best Practices

### Data Protection

- All data encrypted at rest (KMS)
- All data encrypted in transit (HTTPS)
- Encryption keys rotated automatically
- S3 bucket policies enforce encryption

### Access Control

- IAM roles follow least-privilege principle
- No hardcoded credentials
- Service-to-service authentication via IAM
- API throttling to prevent abuse

### Network Security

- OpenSearch network policy (public for MVP, VPC optional)
- S3 public access blocked
- API Gateway behind HTTPS

### Compliance

- GDPR-ready (user data deletion supported)
- SOC 2 compliant AWS services
- Audit trail via CloudTrail
- Data residency control via regions

## Deployment Architecture

### CI/CD Pipeline

```
Developer → Git Push → GitHub Actions
                           ↓
                    [Test Stage]
                     - Lint code
                     - Run tests
                     - Validate CFN
                           ↓
                   [Build Stage]
                    - Package Lambdas
                    - Create artifacts
                           ↓
                  [Deploy Stage]
                   - Deploy CFN
                   - Update Lambdas
                   - Run smoke tests
                           ↓
                    AWS Environment
```

### Infrastructure as Code

**CloudFormation Stacks**:
1. **Security Stack**: KMS keys, IAM roles
2. **Storage Stack**: DynamoDB tables, S3 buckets
3. **AI Stack**: OpenSearch Serverless collection
4. **Compute Stack**: Lambda functions, API Gateway

**Benefits**:
- Reproducible deployments
- Version controlled infrastructure
- Easy rollback
- Multi-environment support

## Future Enhancements

### Planned Features

1. **Frontend Application**
   - React/Next.js web app
   - Mobile app (React Native)
   - Real-time updates via WebSocket

2. **Multi-User Support**
   - Cognito authentication
   - User-specific memories
   - Sharing and collaboration

3. **Enhanced AI Capabilities**
   - Multiple AI model support
   - Custom model fine-tuning
   - Function calling/tool use

4. **Advanced Memory System**
   - Automatic memory categorization
   - Memory importance scoring
   - Smart memory consolidation

5. **Integration APIs**
   - Calendar integration
   - Email integration
   - Third-party app connections

### Scalability Roadmap

**Phase 1** (Current): Single user, basic features
**Phase 2**: Multi-user support, authentication
**Phase 3**: Enterprise features, SSO, teams
**Phase 4**: Platform features, developer API

---

This architecture provides a solid foundation for a cost-effective, secure, and scalable personal AI agent while maintaining simplicity and ease of deployment.
