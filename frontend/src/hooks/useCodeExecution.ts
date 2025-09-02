import { useCallback, useState, useRef } from 'react';
import { useApi } from './useApi';
import { 
  CodeExecutionService, 
  CodeExecutionRequest, 
  CodeValidationRequest 
} from '../services/codeExecutionService';
import { useToast } from '../contexts/ToastContext';

// Hook for code execution
export function useCodeExecution() {
  const [executionHistory, setExecutionHistory] = useState<any[]>([]);
  const { showSuccess, showError } = useToast();

  const api = useApi(
    (request: CodeExecutionRequest) => CodeExecutionService.executeCode(request),
    {
      immediate: false,
      showErrorToast: false, // Handle errors manually
      onSuccess: (result) => {
        setExecutionHistory(prev => [...prev, {
          ...result,
          timestamp: new Date(),
          request: arguments[0]
        }]);
      }
    }
  );

  const executeCode = useCallback(async (request: CodeExecutionRequest) => {
    try {
      const result = await api.execute(request);
      
      if (result?.error) {
        showError('Execution Error', result.error);
      } else {
        showSuccess('Code Executed', 'Your code ran successfully!');
      }
      
      return result;
    } catch (error) {
      showError('Execution Failed', 'Failed to execute code. Please try again.');
      throw error;
    }
  }, [api, showSuccess, showError]);

  const clearHistory = useCallback(() => {
    setExecutionHistory([]);
  }, []);

  return {
    ...api,
    executeCode,
    executionHistory,
    clearHistory
  };
}

// Hook for code validation
export function useCodeValidation() {
  const [validationHistory, setValidationHistory] = useState<any[]>([]);
  const { showSuccess, showError } = useToast();

  const api = useApi(
    (request: CodeValidationRequest) => CodeExecutionService.validateCode(request),
    {
      immediate: false,
      showErrorToast: false,
      onSuccess: (result) => {
        setValidationHistory(prev => [...prev, {
          ...result,
          timestamp: new Date(),
          request: arguments[0]
        }]);

        if (result.isCorrect) {
          showSuccess(
            'All Tests Passed!', 
            `Great job! You earned ${result.xpAwarded} XP.`
          );
        } else {
          showError(
            'Some Tests Failed', 
            `${result.passedTests}/${result.totalTests} tests passed.`
          );
        }
      }
    }
  );

  const validateCode = useCallback(async (request: CodeValidationRequest) => {
    return api.execute(request);
  }, [api]);

  const clearHistory = useCallback(() => {
    setValidationHistory([]);
  }, []);

  return {
    ...api,
    validateCode,
    validationHistory,
    clearHistory
  };
}

// Hook for code templates
export function useCodeTemplates() {
  return useApi(
    (language: 'python' | 'cpp', questionType: string) => 
      CodeExecutionService.getCodeTemplate(language, questionType),
    {
      immediate: false,
      showErrorToast: true
    }
  );
}

// Hook for submission history
export function useSubmissionHistory(questionId?: number) {
  return useApi(
    () => CodeExecutionService.getSubmissionHistory(questionId),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for best solution
export function useBestSolution(questionId: number) {
  return useApi(
    () => CodeExecutionService.getBestSolution(questionId),
    {
      immediate: !!questionId,
      showErrorToast: true
    }
  );
}

// Combined hook for code editor with execution and validation
export function useCodeEditor(questionId?: number) {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState<'python' | 'cpp'>('python');
  const [isModified, setIsModified] = useState(false);
  const originalCodeRef = useRef('');

  const execution = useCodeExecution();
  const validation = useCodeValidation();
  const templates = useCodeTemplates();
  const bestSolution = useBestSolution(questionId || 0);

  const updateCode = useCallback((newCode: string) => {
    setCode(newCode);
    setIsModified(newCode !== originalCodeRef.current);
  }, []);

  const loadTemplate = useCallback(async (questionType: string) => {
    const template = await templates.execute(language, questionType);
    if (template) {
      setCode(template.template);
      originalCodeRef.current = template.template;
      setIsModified(false);
    }
  }, [language, templates]);

  const loadBestSolution = useCallback(() => {
    if (bestSolution.data) {
      setCode(bestSolution.data.code);
      setLanguage(bestSolution.data.language as 'python' | 'cpp');
      originalCodeRef.current = bestSolution.data.code;
      setIsModified(false);
    }
  }, [bestSolution.data]);

  const runCode = useCallback(async (input?: string) => {
    return execution.executeCode({
      code,
      language,
      input,
      questionId
    });
  }, [code, language, questionId, execution]);

  const submitCode = useCallback(async () => {
    if (!questionId) {
      throw new Error('Question ID is required for submission');
    }

    return validation.validateCode({
      code,
      language,
      questionId
    });
  }, [code, language, questionId, validation]);

  const resetCode = useCallback(() => {
    setCode(originalCodeRef.current);
    setIsModified(false);
  }, []);

  const clearCode = useCallback(() => {
    setCode('');
    originalCodeRef.current = '';
    setIsModified(false);
  }, []);

  return {
    // Code state
    code,
    language,
    isModified,
    updateCode,
    setLanguage,
    
    // Template and solution loading
    loadTemplate,
    loadBestSolution,
    templateLoading: templates.loading,
    bestSolution: bestSolution.data,
    
    // Code execution
    runCode,
    executionResult: execution.data,
    executionLoading: execution.loading,
    executionHistory: execution.executionHistory,
    
    // Code validation
    submitCode,
    validationResult: validation.data,
    validationLoading: validation.loading,
    validationHistory: validation.validationHistory,
    
    // Utilities
    resetCode,
    clearCode,
    
    // Loading states
    loading: execution.loading || validation.loading || templates.loading,
    error: execution.error || validation.error || templates.error
  };
}