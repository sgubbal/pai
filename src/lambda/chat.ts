import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { v4 as uuidv4 } from 'uuid';
import { ShortTermMemory } from '../lib/memory';
import { VectorSearch } from '../lib/vector-search';
import { ChatRequest, ChatResponse, Message } from '../types';

const shortTermMemory = new ShortTermMemory();
const vectorSearch = new VectorSearch();

/**
 * Chat handler - processes user messages and generates responses
 */
export async function handler(event: APIGatewayProxyEventV2): Promise<APIGatewayProxyResultV2> {
  try {
    if (!event.body) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Missing request body' }),
      };
    }

    const request: ChatRequest = JSON.parse(event.body);

    // Validate request
    if (!request.message) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: 'Message is required' }),
      };
    }

    // Use provided session ID or create new one
    const sessionId = request.sessionId || uuidv4();
    const timestamp = Date.now();

    // Store user message
    const userMessage: Message = {
      role: 'user',
      content: request.message,
      timestamp,
    };
    await shortTermMemory.storeMessage(sessionId, userMessage);

    // Get conversation history
    const conversationHistory = await shortTermMemory.getConversation(sessionId, 10);

    // Search knowledge base if requested
    let context = '';
    if (request.useKnowledgeBase) {
      const searchResults = await vectorSearch.search({
        query: request.message,
        topK: 3,
        threshold: 0.6,
      });

      if (searchResults.items.length > 0) {
        context = '\n\nRelevant context from knowledge base:\n';
        searchResults.items.forEach((result, idx) => {
          context += `${idx + 1}. ${result.item.content} (similarity: ${result.similarity.toFixed(2)})\n`;
        });
      }
    }

    // Generate response (TODO: Integrate with LLM API - OpenAI, Bedrock, etc.)
    const responseText = await generateResponse(conversationHistory, context, request.message);

    // Store assistant message
    const assistantMessage: Message = {
      role: 'assistant',
      content: responseText,
      timestamp: Date.now(),
    };
    await shortTermMemory.storeMessage(sessionId, assistantMessage);

    const response: ChatResponse = {
      response: responseText,
      sessionId,
      timestamp: assistantMessage.timestamp,
    };

    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(response),
    };
  } catch (error) {
    console.error('Error processing chat request:', error);
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
 * Generate AI response (placeholder - integrate with your LLM)
 */
async function generateResponse(
  history: Message[],
  context: string,
  userMessage: string
): Promise<string> {
  // TODO: Integrate with LLM API (OpenAI, Bedrock, etc.)
  // For MVP, return a simple echo response

  const historyContext = history.length > 0
    ? `\n\nConversation history:\n${history.map(m => `${m.role}: ${m.content}`).join('\n')}`
    : '';

  return `[AI Response Placeholder]

Your message: "${userMessage}"
${context}
${historyContext}

TODO: Integrate with LLM API (OpenAI GPT-4, AWS Bedrock, etc.) to generate actual responses.

For now, this is a placeholder response showing that:
1. Your message was received and encrypted
2. Conversation history is being tracked
3. Knowledge base search is working (if enabled)
4. End-to-end encryption is active

All data is encrypted at rest using KMS envelope encryption.`;
}
