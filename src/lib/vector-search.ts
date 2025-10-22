import { DynamoDBClient, ScanCommand } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient } from '@aws-sdk/lib-dynamodb';
import { KnowledgeItem, VectorSearchRequest, VectorSearchResult } from '../types';
import { decryptObject } from './encryption';

const dynamoClient = new DynamoDBClient({ region: process.env.AWS_REGION || 'us-east-1' });
const docClient = DynamoDBDocumentClient.from(dynamoClient);

const LONG_TERM_TABLE = process.env.LONG_TERM_TABLE!;

/**
 * Calculate cosine similarity between two vectors
 */
function cosineSimilarity(vecA: number[], vecB: number[]): number {
  if (vecA.length !== vecB.length) {
    throw new Error('Vectors must have the same length');
  }

  let dotProduct = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < vecA.length; i++) {
    dotProduct += vecA[i] * vecB[i];
    normA += vecA[i] * vecA[i];
    normB += vecB[i] * vecB[i];
  }

  const denominator = Math.sqrt(normA) * Math.sqrt(normB);
  if (denominator === 0) {
    return 0;
  }

  return dotProduct / denominator;
}

/**
 * Vector search engine for knowledge base
 * Uses cosine similarity for semantic search
 */
export class VectorSearch {
  /**
   * Generate embedding for text (placeholder - integrate with your embedding service)
   * In production, use OpenAI embeddings, Bedrock Titan, or similar
   */
  async generateEmbedding(text: string): Promise<number[]> {
    // TODO: Integrate with embedding service (OpenAI, Bedrock, etc.)
    // For MVP, return a simple hash-based embedding
    const embedding = new Array(384).fill(0);

    // Simple hash-based embedding (NOT for production)
    for (let i = 0; i < text.length; i++) {
      const charCode = text.charCodeAt(i);
      embedding[i % 384] += charCode / 1000;
    }

    // Normalize
    const norm = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
    return embedding.map(val => val / norm);
  }

  /**
   * Perform vector similarity search
   */
  async search(request: VectorSearchRequest): Promise<VectorSearchResult> {
    const topK = request.topK || 5;
    const threshold = request.threshold || 0.5;

    // Generate query embedding
    const queryEmbedding = await this.generateEmbedding(request.query);

    // Scan table (for MVP - use vector database for production scale)
    const scanParams: any = {
      TableName: LONG_TERM_TABLE,
    };

    // Filter by category if provided
    if (request.category) {
      scanParams.FilterExpression = 'category = :category';
      scanParams.ExpressionAttributeValues = {
        ':category': { S: request.category },
      };
    }

    const result = await dynamoClient.send(new ScanCommand(scanParams));

    if (!result.Items || result.Items.length === 0) {
      return { items: [] };
    }

    // Calculate similarities and decrypt
    const similarities: Array<{ item: KnowledgeItem; similarity: number }> = [];

    for (const dbItem of result.Items) {
      const embedding = dbItem.embedding.L?.map(val => Number(val.N)) || [];
      const similarity = cosineSimilarity(queryEmbedding, embedding);

      if (similarity >= threshold) {
        const content = await decryptObject<string>(
          JSON.parse(dbItem.encryptedContent.S || '{}')
        );
        const metadata = await decryptObject<Record<string, any>>(
          JSON.parse(dbItem.encryptedMetadata.S || '{}')
        );

        const item: KnowledgeItem = {
          id: dbItem.id.S || '',
          category: dbItem.category.S || '',
          content,
          embedding,
          metadata,
          timestamp: Number(dbItem.timestamp.N || 0),
        };

        similarities.push({ item, similarity });
      }
    }

    // Sort by similarity and return top K
    similarities.sort((a, b) => b.similarity - a.similarity);

    return {
      items: similarities.slice(0, topK),
    };
  }

  /**
   * Store text with automatic embedding generation
   */
  async storeWithEmbedding(
    id: string,
    category: string,
    content: string,
    metadata: Record<string, any> = {}
  ): Promise<KnowledgeItem> {
    const embedding = await this.generateEmbedding(content);

    return {
      id,
      category,
      content,
      embedding,
      metadata,
      timestamp: Date.now(),
    };
  }
}
