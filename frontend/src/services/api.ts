/**
 * API client for communicating with PAI backend
 */

import { config } from '../config';
import {
  ChatRequest,
  ChatResponse,
  ConversationsResponse,
  Message,
} from '../types';

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class APIClient {
  private baseUrl: string;
  private apiKey: string;
  private retryAttempts = 3;
  private retryDelay = 1000; // ms

  constructor() {
    this.baseUrl = config.apiUrl;
    this.apiKey = config.apiKey;
  }

  /**
   * Send a chat message
   */
  async sendMessage(
    message: string,
    conversationId?: string,
    userId?: string
  ): Promise<ChatResponse> {
    const payload: ChatRequest = {
      message,
      conversation_id: conversationId,
      user_id: userId || config.defaultUserId,
    };

    return this.request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Get all conversations for a user
   */
  async getConversations(userId?: string): Promise<ConversationsResponse> {
    const payload = {
      user_id: userId || config.defaultUserId,
    };

    return this.request<ConversationsResponse>('/conversations', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Get a specific conversation
   */
  async getConversation(conversationId: string): Promise<{
    conversation_id: string;
    messages: Message[];
    created_at: number;
    updated_at: number;
  }> {
    const payload = {
      conversation_id: conversationId,
    };

    return this.request('/conversations', {
      method: 'GET',
      body: JSON.stringify(payload),
    });
  }

  /**
   * Make an API request with retry logic
   */
  private async request<T>(
    endpoint: string,
    options: RequestInit,
    attempt = 1
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.apiKey}`,
      ...(options.headers || {}),
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle non-OK responses
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // Retry on server errors (5xx) or rate limiting (429)
        if (
          (response.status >= 500 || response.status === 429) &&
          attempt < this.retryAttempts
        ) {
          await this.delay(this.retryDelay * attempt);
          return this.request<T>(endpoint, options, attempt + 1);
        }

        throw new APIError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          errorData
        );
      }

      // Parse JSON response
      const data = await response.json();
      return data as T;
    } catch (error) {
      // Retry on network errors
      if (
        error instanceof TypeError &&
        error.message.includes('fetch') &&
        attempt < this.retryAttempts
      ) {
        await this.delay(this.retryDelay * attempt);
        return this.request<T>(endpoint, options, attempt + 1);
      }

      // Re-throw APIError
      if (error instanceof APIError) {
        throw error;
      }

      // Wrap other errors
      throw new APIError(
        error instanceof Error ? error.message : 'Network request failed'
      );
    }
  }

  /**
   * Delay helper for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Update API configuration
   */
  updateConfig(apiUrl?: string, apiKey?: string): void {
    if (apiUrl) this.baseUrl = apiUrl;
    if (apiKey) this.apiKey = apiKey;
  }

  /**
   * Test API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      // Try to get conversations as a connection test
      await this.getConversations();
      return true;
    } catch (error) {
      console.error('API connection test failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient();
