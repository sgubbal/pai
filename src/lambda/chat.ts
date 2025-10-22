import { APIGatewayProxyEventV2, APIGatewayProxyResultV2 } from 'aws-lambda';
import { BedrockRuntimeClient, InvokeModelCommand } from '@aws-sdk/client-bedrock-runtime';
import { v4 as uuidv4 } from 'uuid';
import { ShortTermMemory } from '../lib/memory';
import { VectorSearch } from '../lib/vector-search';
import { ChatRequest, ChatResponse, Message } from '../types';

const bedrockClient = new BedrockRuntimeClient({
  region: process.env.AWS_REGION || 'us-east-1'
});

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
 * Generate AI response using AWS Bedrock (Claude 3.5 Sonnet)
 */
async function generateResponse(
  history: Message[],
  context: string,
  userMessage: string
): Promise<string> {
  try {
    // Build system prompt
    const systemPrompt = `You are a helpful personal AI assistant. You have access to the user's knowledge base and conversation history.${context ? '\n\n' + context : ''}`;

    // Convert history to Claude messages format
    const messages = history
      .filter(m => m.role !== 'system')
      .map(m => ({
        role: m.role === 'user' ? 'user' : 'assistant',
        content: m.content,
      }));

    // Add current user message
    messages.push({
      role: 'user',
      content: userMessage,
    });

    // Prepare Bedrock request
    const requestBody = {
      anthropic_version: 'bedrock-2023-05-31',
      max_tokens: 4096,
      system: systemPrompt,
      messages: messages,
      temperature: 0.7,
      top_p: 0.9,
    };

    // Invoke Claude via Bedrock
    const command = new InvokeModelCommand({
      modelId: 'anthropic.claude-3-5-sonnet-20240620-v1:0',
      contentType: 'application/json',
      accept: 'application/json',
      body: JSON.stringify(requestBody),
    });

    const response = await bedrockClient.send(command);
    const responseBody = JSON.parse(new TextDecoder().decode(response.body));

    // Extract response text
    if (responseBody.content && responseBody.content.length > 0) {
      return responseBody.content[0].text;
    }

    return 'I apologize, but I was unable to generate a response. Please try again.';
  } catch (error) {
    console.error('Error calling Bedrock:', error);

    // Fallback response if Bedrock fails
    return `I encountered an error while processing your request. This might be because:
1. AWS Bedrock is not enabled in your region
2. Claude 3.5 Sonnet model access needs to be requested
3. There's a temporary service issue

Please check your AWS Bedrock settings and try again. Error: ${error instanceof Error ? error.message : 'Unknown error'}`;
  }
}
