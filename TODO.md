# TODO: Next Steps for PAI MVP

## Immediate Priorities

### 1. LLM Integration (CRITICAL)

The chat functionality currently returns placeholder responses. Integrate with an LLM service:

#### Option A: OpenAI
```typescript
// In src/lambda/chat.ts, replace generateResponse function
import OpenAI from 'openai';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

async function generateResponse(history, context, userMessage) {
  const messages = [
    { role: 'system', content: 'You are a helpful personal AI assistant.' },
    ...history.map(h => ({ role: h.role, content: h.content })),
    { role: 'user', content: userMessage + context }
  ];

  const completion = await openai.chat.completions.create({
    model: 'gpt-4-turbo-preview',
    messages,
  });

  return completion.choices[0].message.content;
}
```

**Steps**:
1. Get OpenAI API key from https://platform.openai.com
2. Store in AWS Systems Manager Parameter Store:
   ```bash
   aws ssm put-parameter \
     --name /pai/dev/openai-api-key \
     --value "sk-xxxxx" \
     --type SecureString
   ```
3. Update Lambda to fetch from Parameter Store
4. Add `openai` npm package
5. Redeploy

#### Option B: AWS Bedrock (Recommended for AWS-native)
```typescript
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';

const bedrock = new BedrockRuntimeClient({ region: 'us-east-1' });

async function generateResponse(history, context, userMessage) {
  const prompt = `Human: ${userMessage}\n\nContext: ${context}\n\nAssistant:`;

  const response = await bedrock.send(new InvokeModelCommand({
    modelId: 'anthropic.claude-3-sonnet-20240229-v1:0',
    body: JSON.stringify({
      anthropic_version: 'bedrock-2023-05-31',
      max_tokens: 1024,
      messages: history.map(h => ({ role: h.role, content: h.content }))
    }),
  }));

  return JSON.parse(new TextDecoder().decode(response.body)).content[0].text;
}
```

**Steps**:
1. Enable Bedrock in AWS Console
2. Request access to Claude model
3. Update Lambda IAM role with Bedrock permissions
4. Add Bedrock SDK
5. Redeploy

### 2. Improve Vector Embeddings

Current implementation uses a basic hash-based embedding. Replace with real embeddings:

#### Using OpenAI Embeddings
```typescript
async generateEmbedding(text: string): Promise<number[]> {
  const response = await openai.embeddings.create({
    model: 'text-embedding-3-small',
    input: text,
  });
  return response.data[0].embedding;
}
```

#### Using AWS Bedrock Titan Embeddings
```typescript
async generateEmbedding(text: string): Promise<number[]> {
  const response = await bedrock.send(new InvokeModelCommand({
    modelId: 'amazon.titan-embed-text-v1',
    body: JSON.stringify({ inputText: text }),
  }));
  return JSON.parse(new TextDecoder().decode(response.body)).embedding;
}
```

### 3. GitHub Actions OIDC Setup

Set up OIDC authentication for GitHub Actions (more secure than access keys):

```bash
# Create IAM OIDC provider
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# Create IAM role for GitHub Actions
# See: https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
```

## Phase 2: Production Readiness

### Security Enhancements
- [ ] Add API authentication (API keys or JWT)
- [ ] Implement rate limiting
- [ ] Add AWS WAF rules
- [ ] Enable CloudTrail for audit logging
- [ ] Move to VPC deployment (optional)
- [ ] Use AWS Secrets Manager for API keys

### Monitoring
- [ ] Set up CloudWatch dashboards
- [ ] Create CloudWatch alarms:
  - Lambda error rate > 5%
  - API Gateway 5XX errors
  - DynamoDB throttling
  - High cost anomalies
- [ ] Enable X-Ray tracing
- [ ] Set up SNS notifications for alerts

### Performance
- [ ] Add Redis/ElastiCache for caching
- [ ] Implement connection pooling for DynamoDB
- [ ] Optimize Lambda cold starts
- [ ] Add CloudFront CDN
- [ ] Enable Lambda SnapStart

### Database
- [ ] Consider OpenSearch Serverless for better vector search (at scale)
- [ ] Implement DynamoDB Streams for async processing
- [ ] Add backup automation
- [ ] Set up cross-region replication (DR)

## Phase 3: Features

### Advanced Memory
- [ ] Automatic memory summarization
- [ ] Memory importance scoring
- [ ] Memory decay/aging
- [ ] Category auto-tagging
- [ ] Semantic clustering

### Multi-modal Support
- [ ] Image understanding (GPT-4V/Claude 3)
- [ ] Audio transcription (Whisper)
- [ ] Document parsing (PDF, DOCX)
- [ ] Web scraping integration

### Integrations
- [ ] Calendar integration
- [ ] Email integration
- [ ] Notion/Obsidian sync
- [ ] GitHub integration
- [ ] Slack/Discord bot

### Advanced Features
- [ ] Streaming responses (WebSocket)
- [ ] Voice interface
- [ ] Scheduled tasks/reminders
- [ ] Proactive suggestions
- [ ] Multi-agent orchestration

## Phase 4: Frontend

### Web App
- [ ] React/Next.js frontend
- [ ] Real-time chat interface
- [ ] Knowledge base manager
- [ ] Memory explorer
- [ ] Settings panel
- [ ] Deploy to Vercel/Amplify

### Mobile App
- [ ] React Native app
- [ ] iOS/Android support
- [ ] Push notifications
- [ ] Offline mode
- [ ] Voice input

### Browser Extension
- [ ] Chrome extension
- [ ] Context menu integration
- [ ] Page summarization
- [ ] Quick chat popup

### CLI Tool
- [ ] Node.js CLI
- [ ] Interactive chat mode
- [ ] Knowledge management commands
- [ ] Deployment helpers

## Phase 5: Scale & Optimize

### Cost Optimization
- [ ] Analyze CloudWatch costs
- [ ] Implement log aggregation
- [ ] Use Lambda reserved concurrency wisely
- [ ] Optimize DynamoDB with batch operations
- [ ] Consider Aurora Serverless v2 for complex queries

### Performance at Scale
- [ ] Load testing (Locust, k6)
- [ ] Implement caching strategy
- [ ] Database query optimization
- [ ] Consider HNSW index for vectors
- [ ] Multi-region deployment

### DevOps
- [ ] Blue/green deployments
- [ ] Canary releases
- [ ] Automated rollback
- [ ] Infrastructure testing (Terratest)
- [ ] Chaos engineering

## Quick Wins (Can do today!)

1. **Add OpenAI Integration** (~30 min)
   - Get API key
   - Update chat.ts
   - Redeploy

2. **Set up CloudWatch Dashboard** (~15 min)
   - Create dashboard in AWS Console
   - Add Lambda, API Gateway metrics

3. **Add Basic Authentication** (~1 hour)
   - API key validation in Lambda
   - Store allowed keys in Parameter Store

4. **Create Simple Web UI** (~2 hours)
   - Single HTML file with Tailwind
   - Fetch API calls
   - Deploy to S3 + CloudFront

5. **Improve Error Handling** (~30 min)
   - Better error messages
   - Retry logic
   - Graceful degradation

## Resources

- OpenAI API: https://platform.openai.com/docs
- AWS Bedrock: https://docs.aws.amazon.com/bedrock/
- Vector Search: https://www.pinecone.io/learn/vector-database/
- Serverless Patterns: https://serverlessland.com/patterns
- AWS Well-Architected: https://aws.amazon.com/architecture/well-architected/

## Notes

- Current code is production-ready except for LLM integration
- All infrastructure and security are properly configured
- Focus on LLM integration first to get a working demo
- Then iterate on features based on usage

## Estimated Time to Working MVP

| Task | Time |
|------|------|
| LLM Integration (OpenAI) | 1-2 hours |
| Better Embeddings | 1 hour |
| Basic Web UI | 2-4 hours |
| Testing & Polish | 2 hours |
| **Total** | **6-9 hours** |

After this, you'll have a fully functional personal AI agent!
