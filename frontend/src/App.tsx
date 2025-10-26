import React, { useState, useEffect, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { Header } from './components/Header';
import { ConversationsList } from './components/ConversationsList';
import { MessageList } from './components/MessageList';
import { ChatInput } from './components/ChatInput';
import { LoadingSpinner } from './components/LoadingSpinner';
import { Conversation, Message, Theme, AppState } from './types';
import { apiClient, APIError } from './services/api';
import { storage } from './utils/storage';
import { generateConversationTitle, getErrorMessage, isMobile } from './utils/helpers';
import { config, validateConfig } from './config';

export const App: React.FC = () => {
  const [state, setState] = useState<AppState>({
    conversations: [],
    currentConversationId: null,
    theme: 'light',
    isLoading: false,
    error: null,
  });

  const [isLoadingConversations, setIsLoadingConversations] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(!isMobile());
  const [isSending, setIsSending] = useState(false);
  const [configError, setConfigError] = useState<string | null>(null);

  // Initialize app
  useEffect(() => {
    const init = async () => {
      // Validate configuration
      const configValidation = validateConfig();
      if (!configValidation.valid) {
        setConfigError(configValidation.errors.join(', '));
        setIsLoadingConversations(false);
        return;
      }

      // Load theme
      const savedTheme = storage.getTheme();
      setState((prev) => ({ ...prev, theme: savedTheme }));
      applyTheme(savedTheme);

      // Load conversations from local storage
      const savedConversations = storage.getConversations();
      const currentId = storage.getCurrentConversationId();

      setState((prev) => ({
        ...prev,
        conversations: savedConversations,
        currentConversationId: currentId,
      }));

      setIsLoadingConversations(false);

      // Optionally sync with backend
      // await syncConversationsWithBackend();
    };

    init();
  }, []);

  // Save conversations to storage whenever they change
  useEffect(() => {
    if (!isLoadingConversations) {
      storage.saveConversations(state.conversations);
    }
  }, [state.conversations, isLoadingConversations]);

  // Save current conversation ID
  useEffect(() => {
    if (state.currentConversationId) {
      storage.setCurrentConversationId(state.currentConversationId);
    }
  }, [state.currentConversationId]);

  const applyTheme = (theme: Theme) => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleToggleTheme = () => {
    const newTheme: Theme = state.theme === 'light' ? 'dark' : 'light';
    setState((prev) => ({ ...prev, theme: newTheme }));
    storage.setTheme(newTheme);
    applyTheme(newTheme);
  };

  const getCurrentConversation = (): Conversation | null => {
    if (!state.currentConversationId) return null;
    return (
      state.conversations.find((c) => c.id === state.currentConversationId) || null
    );
  };

  const handleNewConversation = () => {
    const newConversation: Conversation = {
      id: uuidv4(),
      title: 'New Conversation',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    setState((prev) => ({
      ...prev,
      conversations: [newConversation, ...prev.conversations],
      currentConversationId: newConversation.id,
      error: null,
    }));

    if (isMobile()) {
      setIsSidebarOpen(false);
    }
  };

  const handleSelectConversation = (id: string) => {
    setState((prev) => ({
      ...prev,
      currentConversationId: id,
      error: null,
    }));

    if (isMobile()) {
      setIsSidebarOpen(false);
    }
  };

  const handleDeleteConversation = (id: string) => {
    setState((prev) => {
      const newConversations = prev.conversations.filter((c) => c.id !== id);
      const newCurrentId =
        prev.currentConversationId === id
          ? newConversations[0]?.id || null
          : prev.currentConversationId;

      return {
        ...prev,
        conversations: newConversations,
        currentConversationId: newCurrentId,
      };
    });

    if (state.currentConversationId === id) {
      storage.clearCurrentConversation();
    }
  };

  const handleSendMessage = useCallback(async (content: string) => {
    // Create or get current conversation
    let conversationId = state.currentConversationId;
    let isNewConversation = false;

    if (!conversationId) {
      const newConversation: Conversation = {
        id: uuidv4(),
        title: 'New Conversation',
        messages: [],
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };

      setState((prev) => ({
        ...prev,
        conversations: [newConversation, ...prev.conversations],
        currentConversationId: newConversation.id,
      }));

      conversationId = newConversation.id;
      isNewConversation = true;
    }

    // Create user message
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: Date.now(),
    };

    // Update conversation with user message
    setState((prev) => ({
      ...prev,
      conversations: prev.conversations.map((conv) =>
        conv.id === conversationId
          ? {
              ...conv,
              messages: [...conv.messages, userMessage],
              updatedAt: Date.now(),
            }
          : conv
      ),
      error: null,
    }));

    setIsSending(true);

    try {
      // Send to backend
      const userId = storage.getUserId();
      const response = await apiClient.sendMessage(
        content,
        conversationId,
        userId
      );

      // Create assistant message
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp || Date.now(),
      };

      // Update conversation with assistant message
      setState((prev) => ({
        ...prev,
        conversations: prev.conversations.map((conv) =>
          conv.id === conversationId
            ? {
                ...conv,
                messages: [...conv.messages, assistantMessage],
                title:
                  conv.messages.length === 0
                    ? generateConversationTitle([userMessage])
                    : conv.title,
                updatedAt: Date.now(),
              }
            : conv
        ),
      }));
    } catch (error) {
      console.error('Failed to send message:', error);

      const errorMessage =
        error instanceof APIError
          ? error.message
          : getErrorMessage(error);

      setState((prev) => ({
        ...prev,
        error: `Failed to send message: ${errorMessage}`,
      }));

      // Remove user message on error (optional)
      // Or you could add a retry button
    } finally {
      setIsSending(false);
    }
  }, [state.currentConversationId]);

  const handleToggleSidebar = () => {
    setIsSidebarOpen((prev) => !prev);
  };

  if (configError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4">
        <div className="max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 dark:bg-red-900/30 rounded-full mb-4">
            <svg
              className="w-6 h-6 text-red-600 dark:text-red-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 className="text-xl font-bold text-center text-gray-900 dark:text-gray-100 mb-2">
            Configuration Error
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 text-center mb-4">
            {configError}
          </p>
          <div className="bg-gray-50 dark:bg-gray-900 rounded p-3 text-xs">
            <p className="text-gray-600 dark:text-gray-400 mb-2">
              Please set the following environment variables:
            </p>
            <ul className="list-disc list-inside text-gray-500 dark:text-gray-500">
              <li>VITE_API_URL</li>
              <li>VITE_API_KEY</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  if (isLoadingConversations) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <LoadingSpinner size="large" text="Loading..." />
      </div>
    );
  }

  const currentConversation = getCurrentConversation();

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      <Header
        theme={state.theme}
        onToggleTheme={handleToggleTheme}
        onToggleSidebar={handleToggleSidebar}
        isMobile={isMobile()}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <div
          className={`${
            isMobile()
              ? `absolute inset-y-0 left-0 z-50 w-64 transform transition-transform duration-300 ${
                  isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
                }`
              : 'w-64 flex-shrink-0'
          }`}
        >
          <ConversationsList
            conversations={state.conversations}
            currentConversationId={state.currentConversationId}
            onSelectConversation={handleSelectConversation}
            onNewConversation={handleNewConversation}
            onDeleteConversation={handleDeleteConversation}
          />
        </div>

        {/* Mobile sidebar overlay */}
        {isMobile() && isSidebarOpen && (
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={() => setIsSidebarOpen(false)}
          />
        )}

        {/* Main chat area */}
        <div className="flex flex-col flex-1 bg-white dark:bg-gray-800">
          {state.error && (
            <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 px-4 py-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <svg
                    className="w-5 h-5 text-red-600 dark:text-red-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-sm text-red-800 dark:text-red-200">
                    {state.error}
                  </p>
                </div>
                <button
                  onClick={() => setState((prev) => ({ ...prev, error: null }))}
                  className="text-red-600 dark:text-red-400 hover:text-red-800 dark:hover:text-red-200"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          )}

          <MessageList
            messages={currentConversation?.messages || []}
            isLoading={isSending}
          />

          <ChatInput
            onSend={handleSendMessage}
            disabled={isSending}
          />
        </div>
      </div>
    </div>
  );
};
