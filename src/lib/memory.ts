import { DynamoDBClient } from '@aws-sdk/client-dynamodb';
import { DynamoDBDocumentClient, PutCommand, QueryCommand, GetCommand } from '@aws-sdk/lib-dynamodb';
import { ConversationSession, Message, KnowledgeItem } from '../types';
import { encryptObject, decryptObject } from './encryption';

const dynamoClient = new DynamoDBClient({ region: process.env.AWS_REGION || 'us-east-1' });
const docClient = DynamoDBDocumentClient.from(dynamoClient);

const SHORT_TERM_TABLE = process.env.SHORT_TERM_TABLE!;
const LONG_TERM_TABLE = process.env.LONG_TERM_TABLE!;

/**
 * Short-term memory operations (conversation context)
 */
export class ShortTermMemory {
  /**
   * Store a conversation message
   */
  async storeMessage(sessionId: string, message: Message): Promise<void> {
    const ttl = Math.floor(Date.now() / 1000) + 86400; // 24 hours

    // Encrypt the message content
    const encryptedContent = await encryptObject(message.content);

    await docClient.send(
      new PutCommand({
        TableName: SHORT_TERM_TABLE,
        Item: {
          sessionId,
          timestamp: message.timestamp,
          role: message.role,
          encryptedContent,
          ttl,
        },
      })
    );
  }

  /**
   * Retrieve conversation history for a session
   */
  async getConversation(sessionId: string, limit: number = 50): Promise<Message[]> {
    const result = await docClient.send(
      new QueryCommand({
        TableName: SHORT_TERM_TABLE,
        KeyConditionExpression: 'sessionId = :sessionId',
        ExpressionAttributeValues: {
          ':sessionId': sessionId,
        },
        ScanIndexForward: false, // Most recent first
        Limit: limit,
      })
    );

    if (!result.Items || result.Items.length === 0) {
      return [];
    }

    // Decrypt messages
    const messages: Message[] = [];
    for (const item of result.Items) {
      const content = await decryptObject<string>(item.encryptedContent);
      messages.push({
        role: item.role,
        content,
        timestamp: item.timestamp,
      });
    }

    // Reverse to get chronological order
    return messages.reverse();
  }

  /**
   * Store multiple messages (conversation batch)
   */
  async storeConversation(session: ConversationSession): Promise<void> {
    for (const message of session.messages) {
      await this.storeMessage(session.sessionId, message);
    }
  }
}

/**
 * Long-term memory operations (knowledge base with vector embeddings)
 */
export class LongTermMemory {
  /**
   * Store a knowledge item with vector embedding
   */
  async storeKnowledge(item: KnowledgeItem): Promise<void> {
    // Encrypt the content
    const encryptedContent = await encryptObject(item.content);
    const encryptedMetadata = await encryptObject(item.metadata);

    await docClient.send(
      new PutCommand({
        TableName: LONG_TERM_TABLE,
        Item: {
          id: item.id,
          category: item.category,
          encryptedContent,
          embedding: item.embedding,
          encryptedMetadata,
          timestamp: item.timestamp,
        },
      })
    );
  }

  /**
   * Retrieve a knowledge item by ID
   */
  async getKnowledge(id: string): Promise<KnowledgeItem | null> {
    const result = await docClient.send(
      new GetCommand({
        TableName: LONG_TERM_TABLE,
        Key: { id },
      })
    );

    if (!result.Item) {
      return null;
    }

    const content = await decryptObject<string>(result.Item.encryptedContent);
    const metadata = await decryptObject<Record<string, any>>(result.Item.encryptedMetadata);

    return {
      id: result.Item.id,
      category: result.Item.category,
      content,
      embedding: result.Item.embedding,
      metadata,
      timestamp: result.Item.timestamp,
    };
  }

  /**
   * Query knowledge items by category
   */
  async queryByCategory(category: string, limit: number = 20): Promise<KnowledgeItem[]> {
    const result = await docClient.send(
      new QueryCommand({
        TableName: LONG_TERM_TABLE,
        IndexName: 'CategoryIndex',
        KeyConditionExpression: 'category = :category',
        ExpressionAttributeValues: {
          ':category': category,
        },
        ScanIndexForward: false,
        Limit: limit,
      })
    );

    if (!result.Items || result.Items.length === 0) {
      return [];
    }

    const items: KnowledgeItem[] = [];
    for (const item of result.Items) {
      const content = await decryptObject<string>(item.encryptedContent);
      const metadata = await decryptObject<Record<string, any>>(item.encryptedMetadata);

      items.push({
        id: item.id,
        category: item.category,
        content,
        embedding: item.embedding,
        metadata,
        timestamp: item.timestamp,
      });
    }

    return items;
  }
}
