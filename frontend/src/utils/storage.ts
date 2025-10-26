/**
 * Local storage utilities for persisting app state
 */

import { Conversation, Theme } from '../types';

const STORAGE_KEYS = {
  CONVERSATIONS: 'pai_conversations',
  CURRENT_CONVERSATION: 'pai_current_conversation',
  THEME: 'pai_theme',
  USER_ID: 'pai_user_id',
} as const;

export const storage = {
  // Conversations
  getConversations(): Conversation[] {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.CONVERSATIONS);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load conversations:', error);
      return [];
    }
  },

  saveConversations(conversations: Conversation[]): void {
    try {
      localStorage.setItem(STORAGE_KEYS.CONVERSATIONS, JSON.stringify(conversations));
    } catch (error) {
      console.error('Failed to save conversations:', error);
    }
  },

  getCurrentConversationId(): string | null {
    return localStorage.getItem(STORAGE_KEYS.CURRENT_CONVERSATION);
  },

  setCurrentConversationId(id: string): void {
    localStorage.setItem(STORAGE_KEYS.CURRENT_CONVERSATION, id);
  },

  clearCurrentConversation(): void {
    localStorage.removeItem(STORAGE_KEYS.CURRENT_CONVERSATION);
  },

  // Theme
  getTheme(): Theme {
    const theme = localStorage.getItem(STORAGE_KEYS.THEME);
    return (theme === 'dark' || theme === 'light') ? theme : 'light';
  },

  setTheme(theme: Theme): void {
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
  },

  // User ID
  getUserId(): string {
    let userId = localStorage.getItem(STORAGE_KEYS.USER_ID);
    if (!userId) {
      // Generate a unique user ID
      userId = `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
    }
    return userId;
  },

  setUserId(userId: string): void {
    localStorage.setItem(STORAGE_KEYS.USER_ID, userId);
  },

  // Clear all data
  clearAll(): void {
    Object.values(STORAGE_KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
  },
};
