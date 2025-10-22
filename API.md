# PAI API Documentation

## Base URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/{environment}
```

Get your endpoint:
```bash
aws cloudformation describe-stacks \
  --stack-name pai-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
  --output text
```

## Authentication

Currently: **None** (single-user MVP)

For production, add API key header:
```
X-API-Key: your-api-key
```

## Endpoints

### 1. Chat

Send a message to the AI agent and get a response.

**Endpoint**: `POST /chat`

**Request Body**:
```json
{
  "message": "string (required)",
  "sessionId": "string (optional)",
  "useKnowledgeBase": "boolean (optional, default: true)"
}
```

**Response**:
```json
{
  "response": "string",
  "sessionId": "string",
  "timestamp": "number"
}
```

**Example**:
```bash
curl -X POST https://YOUR_ENDPOINT/dev/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is my favorite color?",
    "useKnowledgeBase": true
  }'
```

**Response**:
```json
{
  "response": "Based on what I know, your favorite color is blue.",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1640000000000
}
```

**Notes**:
- If `sessionId` is not provided, a new session is created
- `useKnowledgeBase` enables semantic search of your knowledge base
- Conversation history is maintained per session for 24 hours

---

### 2. Memory - Store

Store information in your long-term knowledge base.

**Endpoint**: `POST /memory`

**Request Body**:
```json
{
  "action": "store",
  "content": "string (required)",
  "category": "string (optional, default: 'general')"
}
```

**Response**:
```json
{
  "success": true,
  "id": "string",
  "message": "Content stored in long-term memory"
}
```

**Example**:
```bash
curl -X POST https://YOUR_ENDPOINT/dev/memory \
  -H "Content-Type: application/json" \
  -d '{
    "action": "store",
    "content": "My birthday is January 15th",
    "category": "personal"
  }'
```

**Response**:
```json
{
  "success": true,
  "id": "abc123-def456-789",
  "message": "Content stored in long-term memory"
}
```

---

### 3. Memory - Retrieve Conversation

Retrieve conversation history for a session.

**Endpoint**: `POST /memory`

**Request Body**:
```json
{
  "action": "retrieve",
  "sessionId": "string (required)"
}
```

**Response**:
```json
{
  "sessionId": "string",
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "string",
      "timestamp": "number"
    }
  ],
  "count": "number"
}
```

**Example**:
```bash
curl -X POST https://YOUR_ENDPOINT/dev/memory \
  -H "Content-Type: application/json" \
  -d '{
    "action": "retrieve",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

### 4. Memory - Retrieve by Category

Retrieve knowledge items by category.

**Endpoint**: `POST /memory`

**Request Body**:
```json
{
  "action": "retrieve",
  "category": "string (required)"
}
```

**Response**:
```json
{
  "category": "string",
  "items": [
    {
      "id": "string",
      "category": "string",
      "content": "string",
      "embedding": "number[]",
      "metadata": "object",
      "timestamp": "number"
    }
  ],
  "count": "number"
}
```

**Example**:
```bash
curl -X POST https://YOUR_ENDPOINT/dev/memory \
  -H "Content-Type: application/json" \
  -d '{
    "action": "retrieve",
    "category": "personal"
  }'
```

---

### 5. Memory - Search

Search knowledge base using semantic similarity.

**Endpoint**: `POST /memory`

**Request Body**:
```json
{
  "action": "search",
  "query": "string (required)",
  "category": "string (optional)"
}
```

**Response**:
```json
{
  "query": "string",
  "results": [
    {
      "item": {
        "id": "string",
        "category": "string",
        "content": "string",
        "metadata": "object",
        "timestamp": "number"
      },
      "similarity": "number"
    }
  ],
  "count": "number"
}
```

**Example**:
```bash
curl -X POST https://YOUR_ENDPOINT/dev/memory \
  -H "Content-Type: application/json" \
  -d '{
    "action": "search",
    "query": "when is my birthday",
    "category": "personal"
  }'
```

---

### 6. Vector Search

Advanced semantic search with customizable parameters.

**Endpoint**: `POST /search`

**Request Body**:
```json
{
  "query": "string (required)",
  "topK": "number (optional, default: 5)",
  "category": "string (optional)",
  "threshold": "number (optional, default: 0.5, range: 0-1)"
}
```

**Response**:
```json
{
  "query": "string",
  "results": [
    {
      "id": "string",
      "category": "string",
      "content": "string",
      "metadata": "object",
      "similarity": "number",
      "timestamp": "number"
    }
  ],
  "count": "number",
  "parameters": {
    "topK": "number",
    "threshold": "number",
    "category": "string|null"
  }
}
```

**Example**:
```bash
curl -X POST https://YOUR_ENDPOINT/dev/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "important dates and events",
    "topK": 10,
    "threshold": 0.6
  }'
```

**Response**:
```json
{
  "query": "important dates and events",
  "results": [
    {
      "id": "abc123",
      "category": "personal",
      "content": "My birthday is January 15th",
      "metadata": {
        "source": "manual",
        "createdAt": "2024-01-01T00:00:00.000Z"
      },
      "similarity": 0.87,
      "timestamp": 1640000000000
    }
  ],
  "count": 1,
  "parameters": {
    "topK": 10,
    "threshold": 0.6,
    "category": null
  }
}
```

---

## Error Responses

All endpoints return standard HTTP status codes.

### 400 Bad Request

```json
{
  "error": "Missing request body"
}
```

### 500 Internal Server Error

```json
{
  "error": "Internal server error",
  "message": "Detailed error message"
}
```

---

## Data Types

### Message
```typescript
{
  role: 'user' | 'assistant' | 'system',
  content: string,
  timestamp: number  // Unix timestamp in milliseconds
}
```

### KnowledgeItem
```typescript
{
  id: string,            // UUID
  category: string,      // User-defined category
  content: string,       // The actual text content
  embedding: number[],   // 384-dimensional vector
  metadata: {
    [key: string]: any   // Custom metadata
  },
  timestamp: number      // Unix timestamp in milliseconds
}
```

---

## Rate Limits

**Current**: No rate limiting (single-user)

**Recommended for Production**:
- 100 requests/minute per user
- 1000 requests/day per user

---

## Usage Examples

### Example 1: Complete Chat Flow

```typescript
// Start conversation
const chat1 = await fetch(`${API_ENDPOINT}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'Hello! My name is Alice.',
  })
});
const response1 = await chat1.json();
const sessionId = response1.sessionId;

// Continue conversation
const chat2 = await fetch(`${API_ENDPOINT}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is my name?',
    sessionId: sessionId,
  })
});
const response2 = await chat2.json();
// Should remember: "Your name is Alice"
```

### Example 2: Knowledge Base Workflow

```typescript
// Store knowledge
await fetch(`${API_ENDPOINT}/memory`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'store',
    content: 'I love hiking in the mountains',
    category: 'hobbies',
  })
});

await fetch(`${API_ENDPOINT}/memory`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'store',
    content: 'My favorite food is sushi',
    category: 'preferences',
  })
});

// Search knowledge
const searchResults = await fetch(`${API_ENDPOINT}/search`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'what do I enjoy doing',
    topK: 5,
  })
});
const results = await searchResults.json();
// Returns: "I love hiking in the mountains" with high similarity
```

### Example 3: Chat with Knowledge Base

```typescript
// Store some facts
await fetch(`${API_ENDPOINT}/memory`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'store',
    content: 'My birthday is January 15th',
    category: 'personal',
  })
});

// Ask about it
const chat = await fetch(`${API_ENDPOINT}/chat`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'When is my birthday?',
    useKnowledgeBase: true,
  })
});
const response = await chat.json();
// AI will use the stored knowledge to answer
```

---

## Client Libraries

### TypeScript/JavaScript

See `examples/client.ts` for a complete client implementation.

```typescript
import { PAIClient } from './examples/client';

const client = new PAIClient(API_ENDPOINT);

// Chat
const response = await client.chat('Hello!');

// Store knowledge
await client.storeKnowledge('Important info', 'category');

// Search
const results = await client.searchKnowledge('query');

// Get history
const history = await client.getHistory();
```

### Python (Example)

```python
import requests

class PAIClient:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint.rstrip('/')
        self.session_id = None

    def chat(self, message, use_knowledge_base=True):
        response = requests.post(
            f'{self.api_endpoint}/chat',
            json={
                'message': message,
                'sessionId': self.session_id,
                'useKnowledgeBase': use_knowledge_base,
            }
        )
        data = response.json()
        self.session_id = data['sessionId']
        return data

    def store_knowledge(self, content, category='general'):
        return requests.post(
            f'{self.api_endpoint}/memory',
            json={
                'action': 'store',
                'content': content,
                'category': category,
            }
        ).json()

    def search(self, query, top_k=5):
        return requests.post(
            f'{self.api_endpoint}/search',
            json={
                'query': query,
                'topK': top_k,
            }
        ).json()
```

---

## Best Practices

1. **Session Management**
   - Store `sessionId` for conversation continuity
   - Sessions expire after 24 hours (TTL)

2. **Knowledge Organization**
   - Use meaningful categories
   - Keep content chunks focused and atomic
   - Add rich metadata for better filtering

3. **Search Optimization**
   - Be specific in queries
   - Adjust `threshold` based on needs
   - Use `topK` to control result count

4. **Error Handling**
   - Always check HTTP status codes
   - Implement retry logic for 5xx errors
   - Handle network timeouts gracefully

5. **Performance**
   - Reuse connections (keep-alive)
   - Batch operations when possible
   - Cache frequent queries client-side

---

## Versioning

**Current Version**: v1 (MVP)

Future versions will maintain backward compatibility.

---

## Support

For issues or questions:
1. Check the documentation
2. View CloudWatch logs
3. Review error messages
4. Check GitHub issues

---

## Changelog

### v1.0.0 (MVP)
- Chat endpoint with conversation history
- Memory storage and retrieval
- Vector search functionality
- End-to-end encryption
- Single-user mode
