import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { VectorSearch } from '../lib/vector-search';
import { VectorSearchRequest } from '../types';

const vectorSearch = new VectorSearch();

/**
 * Vector search handler - performs semantic search on knowledge base
 */
export async function handler(event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> {
  try {
    if (!event.body) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing request body' }),
      };
    }

    const request: VectorSearchRequest = JSON.parse(event.body);

    // Validate request
    if (!request.query) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Query is required' }),
      };
    }

    // Perform vector search
    const results = await vectorSearch.search(request);

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: request.query,
        results: results.items.map(item => ({
          id: item.item.id,
          category: item.item.category,
          content: item.item.content,
          metadata: item.item.metadata,
          similarity: item.similarity,
          timestamp: item.item.timestamp,
        })),
        count: results.items.length,
        parameters: {
          topK: request.topK || 5,
          threshold: request.threshold || 0.5,
          category: request.category,
        },
      }),
    };
  } catch (error) {
    console.error('Error processing vector search request:', error);
    return {
      statusCode: 500,
      body: JSON.stringify({
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      }),
    };
  }
}
