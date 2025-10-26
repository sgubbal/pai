export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
}

export interface APIConfig {
  apiUrl: string;
  apiKey: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  timestamp: number;
}

export interface ConversationsResponse {
  conversations: Array<{
    conversation_id: string;
    messages: Array<{
      role: string;
      content: string;
      timestamp: number;
    }>;
    created_at: number;
    updated_at: number;
  }>;
}

export interface EncryptedData {
  ciphertext: string;
  iv: string;
  tag: string;
}

export type Theme = 'light' | 'dark';

export interface AppState {
  conversations: Conversation[];
  currentConversationId: string | null;
  theme: Theme;
  isLoading: boolean;
  error: string | null;
}
