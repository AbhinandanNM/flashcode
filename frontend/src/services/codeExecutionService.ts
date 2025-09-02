import ApiClient from '../utils/api';

export interface CodeExecutionRequest {
  code: string;
  language: 'python' | 'cpp';
  input?: string;
  questionId?: number;
}

export interface CodeExecutionResult {
  output: string;
  error?: string;
  executionTime: number;
  memoryUsed?: number;
  isCorrect?: boolean;
  testResults?: TestResult[];
  xpAwarded?: number;
}

export interface TestResult {
  input: string;
  expectedOutput: string;
  actualOutput: string;
  passed: boolean;
  error?: string;
}

export interface CodeValidationRequest {
  code: string;
  questionId: number;
  language: 'python' | 'cpp';
}

export interface CodeValidationResult {
  isCorrect: boolean;
  totalTests: number;
  passedTests: number;
  testResults: TestResult[];
  executionTime: number;
  xpAwarded: number;
  feedback?: string;
}

export class CodeExecutionService {
  // Execute code without validation
  static async executeCode(request: CodeExecutionRequest): Promise<CodeExecutionResult> {
    return ApiClient.post('/execute/run', request, false); // Don't retry code execution
  }

  // Validate code against test cases
  static async validateCode(request: CodeValidationRequest): Promise<CodeValidationResult> {
    return ApiClient.post('/execute/validate', request, false);
  }

  // Get execution status (for async execution)
  static async getExecutionStatus(executionId: string): Promise<{
    status: 'pending' | 'running' | 'completed' | 'failed';
    result?: CodeExecutionResult;
  }> {
    return ApiClient.get(`/execute/status/${executionId}`);
  }

  // Get supported languages
  static async getSupportedLanguages(): Promise<{
    language: string;
    version: string;
    extensions: string[];
  }[]> {
    return ApiClient.get('/execute/languages');
  }

  // Get code templates for different question types
  static async getCodeTemplate(
    language: 'python' | 'cpp',
    questionType: string
  ): Promise<{ template: string; description: string }> {
    return ApiClient.get(`/execute/template?language=${language}&type=${questionType}`);
  }

  // Submit code solution for a question
  static async submitCodeSolution(
    questionId: number,
    code: string,
    language: 'python' | 'cpp'
  ): Promise<CodeValidationResult> {
    return ApiClient.post('/execute/submit', {
      questionId,
      code,
      language
    }, false);
  }

  // Get user's code submission history
  static async getSubmissionHistory(questionId?: number): Promise<{
    id: number;
    questionId: number;
    code: string;
    language: string;
    isCorrect: boolean;
    score: number;
    submittedAt: string;
  }[]> {
    const endpoint = questionId 
      ? `/execute/submissions?question_id=${questionId}`
      : '/execute/submissions';
    return ApiClient.get(endpoint);
  }

  // Get best solution for a question
  static async getBestSolution(questionId: number): Promise<{
    code: string;
    language: string;
    score: number;
    executionTime: number;
    submittedAt: string;
  } | null> {
    return ApiClient.get(`/execute/best-solution/${questionId}`);
  }
}