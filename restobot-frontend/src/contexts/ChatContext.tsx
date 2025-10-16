import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { chatService } from '../services/chatService';

// Chat message interface
export interface ChatMessage {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
  typing?: boolean;
}

// Chat state interface
interface ChatState {
  messages: ChatMessage[];
  isTyping: boolean;
  connected: boolean;
  error: string | null;
}

// Chat actions
type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_TYPING'; payload: boolean }
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'CLEAR_MESSAGES' }
  | { type: 'LOAD_HISTORY'; payload: ChatMessage[] };

// Initial state
const initialState: ChatState = {
  messages: [],
  isTyping: false,
  connected: false,
  error: null,
};

// Chat reducer
const chatReducer = (state: ChatState, action: ChatAction): ChatState => {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [...state.messages, action.payload],
        error: null,
      };
    case 'SET_TYPING':
      return {
        ...state,
        isTyping: action.payload,
      };
    case 'SET_CONNECTED':
      return {
        ...state,
        connected: action.payload,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      };
    case 'CLEAR_MESSAGES':
      return {
        ...state,
        messages: [],
        error: null,
      };
    case 'LOAD_HISTORY':
      return {
        ...state,
        messages: action.payload,
        error: null,
      };
    default:
      return state;
  }
};

// Chat context interface
interface ChatContextType extends ChatState {
  sendMessage: (message: string) => Promise<void>;
  clearMessages: () => void;
  loadHistory: () => Promise<void>;
  generateId: () => string;
}

// Create context
const ChatContext = createContext<ChatContextType | undefined>(undefined);

// Chat provider component
export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  // Generate unique message ID
  const generateId = useCallback(() => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  }, []);

  // Send message function
  const sendMessage = useCallback(async (text: string) => {
    try {
      // Add user message
      const userMessage: ChatMessage = {
        id: generateId(),
        text,
        sender: 'user',
        timestamp: new Date(),
      };
      dispatch({ type: 'ADD_MESSAGE', payload: userMessage });

      // Set typing indicator
      dispatch({ type: 'SET_TYPING', payload: true });

      // Send message to chat service
      const data = await chatService.sendMessage(text);
      
      // Add bot response
      const botMessage: ChatMessage = {
        id: generateId(),
        text: data.response || 'Xin lỗi, tôi không hiểu. Bạn có thể nói rõ hơn không?',
        sender: 'bot',
        timestamp: new Date(),
      };

      dispatch({ type: 'SET_TYPING', payload: false });
      dispatch({ type: 'ADD_MESSAGE', payload: botMessage });
      
      // Set connected status
      dispatch({ type: 'SET_CONNECTED', payload: true });
    } catch (error) {
      dispatch({ type: 'SET_TYPING', payload: false });
      dispatch({ type: 'SET_CONNECTED', payload: false });
      
      const errorMessage = error instanceof Error ? error.message : 'Đã xảy ra lỗi';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      
      // Add error message from bot
      const errorBotMessage: ChatMessage = {
        id: generateId(),
        text: 'Xin lỗi, đã xảy ra lỗi khi xử lý tin nhắn của bạn. Vui lòng thử lại sau. Hãy đảm bảo rằng server backend đang chạy.',
        sender: 'bot',
        timestamp: new Date(),
      };
      dispatch({ type: 'ADD_MESSAGE', payload: errorBotMessage });
    }
  }, [generateId]);

  // Clear messages function
  const clearMessages = useCallback(() => {
    dispatch({ type: 'CLEAR_MESSAGES' });
  }, []);

  // Load chat history
  const loadHistory = useCallback(async () => {
    try {
      // Note: Backend doesn't have a chat history endpoint yet
      // For now, we'll just clear any error
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Không thể tải lịch sử chat';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
    }
  }, []);

  const value: ChatContextType = {
    ...state,
    sendMessage,
    clearMessages,
    loadHistory,
    generateId,
  };

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};

// Hook to use chat context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};