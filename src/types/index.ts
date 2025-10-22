export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
}

export interface ConversationSession {
  sessionId: string;
  messages: Message[];
  timestamp: number;
  ttl?: number;
}

export interface KnowledgeItem {
  id: string;
  category: string;
  content: string;
  embedding: number[];
  metadata: Record<string, any>;
  timestamp: number;
}

export interface VectorSearchRequest {
  query: string;
  topK?: number;
  category?: string;
  threshold?: number;
}

export interface VectorSearchResult {
  items: Array<{
    item: KnowledgeItem;
    similarity: number;
  }>;
}

export interface ChatRequest {
  sessionId: string;
  message: string;
  useKnowledgeBase?: boolean;
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  timestamp: number;
}

export interface MemoryRequest {
  action: 'store' | 'retrieve' | 'search';
  sessionId?: string;
  content?: string;
  category?: string;
  query?: string;
}
