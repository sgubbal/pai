/**
 * Example client for interacting with PAI API
 *
 * Usage:
 *   ts-node examples/client.ts
 */

interface ChatResponse {
  response: string;
  sessionId: string;
  timestamp: number;
}

interface MemoryResponse {
  success?: boolean;
  id?: string;
  messages?: any[];
  items?: any[];
}

class PAIClient {
  private apiEndpoint: string;
  private sessionId?: string;

  constructor(apiEndpoint: string) {
    this.apiEndpoint = apiEndpoint.replace(/\/$/, ''); // Remove trailing slash
  }

  /**
   * Send a chat message
   */
  async chat(message: string, useKnowledgeBase = true): Promise<ChatResponse> {
    const response = await fetch(`${this.apiEndpoint}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        sessionId: this.sessionId,
        useKnowledgeBase,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    const data = await response.json() as ChatResponse;
    this.sessionId = data.sessionId; // Store session ID for continuity
    return data;
  }

  /**
   * Store information in knowledge base
   */
  async storeKnowledge(content: string, category = 'general'): Promise<MemoryResponse> {
    const response = await fetch(`${this.apiEndpoint}/memory`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'store',
        content,
        category,
      }),
    });

    if (!response.ok) {
      throw new Error(`Store request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Search knowledge base
   */
  async searchKnowledge(query: string, topK = 5): Promise<any> {
    const response = await fetch(`${this.apiEndpoint}/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        topK,
      }),
    });

    if (!response.ok) {
      throw new Error(`Search request failed: ${response.statusText}`);
    }

    return await response.json();
  }

  /**
   * Get conversation history
   */
  async getHistory(): Promise<MemoryResponse> {
    if (!this.sessionId) {
      throw new Error('No active session');
    }

    const response = await fetch(`${this.apiEndpoint}/memory`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'retrieve',
        sessionId: this.sessionId,
      }),
    });

    if (!response.ok) {
      throw new Error(`Retrieve request failed: ${response.statusText}`);
    }

    return await response.json();
  }
}

// Example usage
async function main() {
  // Replace with your actual API endpoint
  const API_ENDPOINT = process.env.API_ENDPOINT || 'https://xxxxx.execute-api.us-east-1.amazonaws.com/dev';

  const client = new PAIClient(API_ENDPOINT);

  try {
    console.log('🤖 PAI Client Example\n');

    // 1. Store some knowledge
    console.log('📝 Storing knowledge...');
    await client.storeKnowledge('My favorite color is blue', 'personal');
    await client.storeKnowledge('I am a software engineer', 'personal');
    await client.storeKnowledge('I enjoy hiking and photography', 'hobbies');
    console.log('✓ Knowledge stored\n');

    // 2. Chat with AI
    console.log('💬 Chatting with AI...');
    const response1 = await client.chat('Hello! What do you know about me?');
    console.log('AI:', response1.response);
    console.log('Session ID:', response1.sessionId, '\n');

    // 3. Follow-up message
    const response2 = await client.chat('What are my hobbies?');
    console.log('AI:', response2.response, '\n');

    // 4. Search knowledge
    console.log('🔍 Searching knowledge...');
    const searchResults = await client.searchKnowledge('favorite color');
    console.log('Search results:', JSON.stringify(searchResults, null, 2), '\n');

    // 5. Get conversation history
    console.log('📜 Getting conversation history...');
    const history = await client.getHistory();
    console.log(`Found ${history.messages?.length || 0} messages in conversation\n`);

    console.log('✨ Example completed successfully!');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

export { PAIClient };
