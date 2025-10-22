import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { v4 as uuidv4 } from 'uuid';
import { ShortTermMemory, LongTermMemory } from '../lib/memory';
import { VectorSearch } from '../lib/vector-search';
import { MemoryRequest } from '../types';

const shortTermMemory = new ShortTermMemory();
const longTermMemory = new LongTermMemory();
const vectorSearch = new VectorSearch();

/**
 * Memory manager - handles storage and retrieval of memories
 */
export async function handler(event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> {
  try {
    if (!event.body) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing request body' }),
      };
    }

    const request: MemoryRequest = JSON.parse(event.body);

    switch (request.action) {
      case 'store':
        return await handleStore(request);
      case 'retrieve':
        return await handleRetrieve(request);
      case 'search':
        return await handleSearch(request);
      default:
        return {
          statusCode: 400,
          body: JSON.stringify({ error: 'Invalid action' }),
        };
    }
  } catch (error) {
    console.error('Error processing memory request:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      }),
    };
  }
}

/**
 * Store content in long-term memory with vector embedding
 */
async function handleStore(request: MemoryRequest): Promise<APIGatewayProxyResultV2> {
  if (!request.content) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Content is required for store action' }),
    };
  }

  const category = request.category || 'general';
  const id = uuidv4();

  // Generate knowledge item with embedding
  const knowledgeItem = await vectorSearch.storeWithEmbedding(
    id,
    category,
    request.content,
    { source: 'manual', createdAt: new Date().toISOString() }
  );

  // Store in long-term memory
  await longTermMemory.storeKnowledge(knowledgeItem);

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      success: true,
      id,
      message: 'Content stored in long-term memory',
    }),
  };
}

/**
 * Retrieve conversation or knowledge item
 */
async function handleRetrieve(request: MemoryRequest): Promise<APIGatewayProxyResultV2> {
  if (request.sessionId) {
    // Retrieve conversation history
    const messages = await shortTermMemory.getConversation(request.sessionId);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sessionId: request.sessionId,
        messages,
        count: messages.length,
      }),
    };
  } else if (request.category) {
    // Retrieve knowledge by category
    const items = await longTermMemory.queryByCategory(request.category);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        category: request.category,
        items,
        count: items.length,
      }),
    };
  } else {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Either sessionId or category is required' }),
    };
  }
}

/**
 * Search knowledge base using vector similarity
 */
async function handleSearch(request: MemoryRequest): Promise<APIGatewayProxyResultV2> {
  if (!request.query) {
    return {
      statusCode: 400,
      body: JSON.stringify({ error: 'Query is required for search action' }),
    };
  }

  const searchResults = await vectorSearch.search({
    query: request.query,
    topK: 10,
    category: request.category,
    threshold: 0.5,
  });

  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: request.query,
      results: searchResults.items,
      count: searchResults.items.length,
    }),
  };
}
