import React, { createContext, useContext, useState } from 'react';

// Loading context interface
interface LoadingContextType {
  loading: boolean;
  loadingMessage: string;
  setLoading: (loading: boolean, message?: string) => void;
  startLoading: (message?: string) => void;
  stopLoading: () => void;
}

// Create context
const LoadingContext = createContext<LoadingContextType | undefined>(undefined);

// Loading provider component
export const LoadingProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [loading, setLoadingState] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('Đang tải...');

  const setLoading = (isLoading: boolean, message = 'Đang tải...') => {
    setLoadingState(isLoading);
    setLoadingMessage(message);
  };

  const startLoading = (message = 'Đang tải...') => {
    setLoadingState(true);
    setLoadingMessage(message);
  };

  const stopLoading = () => {
    setLoadingState(false);
  };

  const value: LoadingContextType = {
    loading,
    loadingMessage,
    setLoading,
    startLoading,
    stopLoading,
  };

  return <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>;
};

// Hook to use loading context
export const useLoading = () => {
  const context = useContext(LoadingContext);
  if (context === undefined) {
    throw new Error('useLoading must be used within a LoadingProvider');
  }
  return context;
};