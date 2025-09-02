import { useState, useEffect, useCallback, useRef } from 'react';
import ApiClient from '../utils/api';
import { useToast } from '../contexts/ToastContext';
import { getErrorMessage } from '../utils/errorHandler';

export interface UseApiOptions {
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  showErrorToast?: boolean;
  showSuccessToast?: boolean;
  successMessage?: string;
  retryable?: boolean;
}

export interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastFetch: Date | null;
}

export interface UseApiReturn<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<T | null>;
  refresh: () => Promise<T | null>;
  reset: () => void;
  setData: (data: T | null) => void;
}

export function useApi<T = any>(
  apiFunction: (...args: any[]) => Promise<T>,
  options: UseApiOptions = {}
): UseApiReturn<T> {
  const {
    immediate = false,
    onSuccess,
    onError,
    showErrorToast = true,
    showSuccessToast = false,
    successMessage,
    retryable = true
  } = options;

  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
    lastFetch: null
  });

  const { showError, showSuccess } = useToast();
  const lastArgsRef = useRef<any[]>([]);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async (...args: any[]): Promise<T | null> => {
    if (!mountedRef.current) return null;

    lastArgsRef.current = args;
    
    setState(prev => ({
      ...prev,
      loading: true,
      error: null
    }));

    try {
      const result = await apiFunction(...args);
      
      if (!mountedRef.current) return null;

      setState(prev => ({
        ...prev,
        data: result,
        loading: false,
        error: null,
        lastFetch: new Date()
      }));

      if (showSuccessToast && successMessage) {
        showSuccess('Success', successMessage);
      }

      onSuccess?.(result);
      return result;
    } catch (error) {
      if (!mountedRef.current) return null;

      const errorMessage = getErrorMessage(error);
      
      setState(prev => ({
        ...prev,
        loading: false,
        error: errorMessage
      }));

      if (showErrorToast) {
        showError('Error', errorMessage);
      }

      onError?.(error);
      return null;
    }
  }, [apiFunction, onSuccess, onError, showErrorToast, showSuccessToast, successMessage, showError, showSuccess]);

  const refresh = useCallback(() => {
    return execute(...lastArgsRef.current);
  }, [execute]);

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
      lastFetch: null
    });
  }, []);

  const setData = useCallback((data: T | null) => {
    setState(prev => ({
      ...prev,
      data
    }));
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    ...state,
    execute,
    refresh,
    reset,
    setData
  };
}

// Specialized hook for paginated data
export interface UsePaginatedApiOptions extends UseApiOptions {
  pageSize?: number;
  initialPage?: number;
}

export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}

export interface UsePaginatedApiReturn<T> extends Omit<UseApiReturn<PaginatedData<T>>, 'execute'> {
  loadMore: () => Promise<void>;
  loadPage: (page: number) => Promise<void>;
  hasMore: boolean;
  currentPage: number;
  totalPages: number;
}

export function usePaginatedApi<T = any>(
  apiFunction: (page: number, pageSize: number, ...args: any[]) => Promise<PaginatedData<T>>,
  options: UsePaginatedApiOptions = {}
): UsePaginatedApiReturn<T> {
  const { pageSize = 20, initialPage = 1, ...apiOptions } = options;
  const [currentPage, setCurrentPage] = useState(initialPage);
  const additionalArgsRef = useRef<any[]>([]);

  const api = useApi(
    (page: number, size: number, ...args: any[]) => apiFunction(page, size, ...args),
    apiOptions
  );

  const loadPage = useCallback(async (page: number) => {
    setCurrentPage(page);
    return api.execute(page, pageSize, ...additionalArgsRef.current);
  }, [api, pageSize]);

  const loadMore = useCallback(async () => {
    if (!api.data?.hasMore) return;
    
    const nextPage = currentPage + 1;
    const result = await api.execute(nextPage, pageSize, ...additionalArgsRef.current);
    
    if (result && api.data) {
      // Append new items to existing data
      api.setData({
        ...result,
        items: [...api.data.items, ...result.items]
      });
      setCurrentPage(nextPage);
    }
  }, [api, currentPage, pageSize]);

  const hasMore = api.data?.hasMore ?? false;
  const totalPages = api.data ? Math.ceil(api.data.total / pageSize) : 0;

  return {
    ...api,
    loadMore,
    loadPage,
    hasMore,
    currentPage,
    totalPages
  };
}