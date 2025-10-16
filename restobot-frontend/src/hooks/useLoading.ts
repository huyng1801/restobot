import { useState, useCallback } from 'react';

interface LoadingState {
  [key: string]: boolean;
}

export function useLoading(initialState: LoadingState = {}) {
  const [loadingState, setLoadingState] = useState<LoadingState>(initialState);

  const setLoading = useCallback((key: string, isLoading: boolean) => {
    setLoadingState(prev => ({
      ...prev,
      [key]: isLoading
    }));
  }, []);

  const isLoading = useCallback((key: string): boolean => {
    return loadingState[key] || false;
  }, [loadingState]);

  const isAnyLoading = useCallback((): boolean => {
    return Object.values(loadingState).some(loading => loading);
  }, [loadingState]);

  const resetLoading = useCallback(() => {
    setLoadingState({});
  }, []);

  return {
    loadingState,
    setLoading,
    isLoading,
    isAnyLoading,
    resetLoading
  };
}