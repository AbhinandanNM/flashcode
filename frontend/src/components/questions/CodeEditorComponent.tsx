import React, { useState, useEffect } from 'react';
import { Question } from '../../types';
import MonacoCodeEditor from '../code/MonacoCodeEditor';

interface CodeEditorComponentProps {
  question: Question;
  userAnswer?: string;
  onAnswerSubmit: (answer: string) => void;
  onAnswerChange?: (answer: string) => void;
  showFeedback?: boolean;
  isCorrect?: boolean;
  explanation?: string;
  disabled?: boolean;
}

interface ExecutionResult {
  output?: string;
  error?: string;
  status?: string;
  execution_time?: number;
}

const CodeEditorComponent: React.FC<CodeEditorComponentProps> = ({
  question,
  userAnswer = '',
  onAnswerSubmit,
  onAnswerChange,
  showFeedback = false,
  isCorrect,
  disabled = false,
}) => {
  const [code, setCode] = useState(userAnswer || getDefaultCode());
  const [isRunning, setIsRunning] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [hasSubmitted, setHasSubmitted] = useState(showFeedback);

  function getDefaultCode(): string {
    const language = getLanguageFromQuestion();
    
    if (language === 'python') {
      return '# Write your Python code here\n\n';
    } else if (language === 'cpp') {
      return '#include <iostream>\nusing namespace std;\n\nint main() {\n    // Write your C++ code here\n    \n    return 0;\n}';
    }
    
    return '// Write your code here\n';
  }

  const handleCodeChange = (value: string) => {
    if (disabled || hasSubmitted) return;
    
    setCode(value);
    if (onAnswerChange) {
      onAnswerChange(value);
    }
  };

  const handleRunCode = async () => {
    if (isRunning || disabled) return;
    
    setIsRunning(true);
    setExecutionResult(null);
    
    try {
      const language = getLanguageFromQuestion();
      
      const response = await fetch('/api/execute/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          code: code,
          language: language,
          input: '', // Could be extended to support input
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to execute code');
      }

      const result = await response.json();
      setExecutionResult({
        ...result,
        status: result.error ? 'error' : 'success'
      });
    } catch (error) {
      setExecutionResult({
        error: error instanceof Error ? error.message : 'Failed to execute code',
        status: 'error'
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = () => {
    if (!code.trim() || disabled || hasSubmitted) return;
    
    setHasSubmitted(true);
    onAnswerSubmit(code);
  };

  const getLanguageFromQuestion = (): 'python' | 'cpp' => {
    const questionText = question.question_text.toLowerCase();
    if (questionText.includes('c++') || questionText.includes('cpp')) return 'cpp';
    return 'python'; // default
  };

  return (
    <div className="space-y-4">
      {/* Monaco Code Editor */}
      <MonacoCodeEditor
        language={getLanguageFromQuestion()}
        value={code}
        onChange={handleCodeChange}
        onRun={handleRunCode}
        isRunning={isRunning}
        disabled={disabled || hasSubmitted}
        height="400px"
        theme="vs-dark"
        showRunButton={true}
        executionResult={executionResult}
      />

      {/* Instructions */}
      {!hasSubmitted && (
        <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
          <p>💡 Write your code in the editor above and click "Run" to test it. Use Ctrl+Enter as a shortcut. When you're satisfied with your solution, click "Submit Code".</p>
        </div>
      )}

      {/* Expected Output Hint */}
      {question.correct_answer && !hasSubmitted && (
        <div className="text-sm text-gray-600 bg-yellow-50 border border-yellow-200 p-3 rounded-lg">
          <p className="font-medium mb-1">Expected Output:</p>
          <pre className="text-xs font-mono bg-yellow-100 p-2 rounded">{question.correct_answer}</pre>
        </div>
      )}

      {/* Submit Button */}
      {!showFeedback && !hasSubmitted && (
        <div className="pt-2">
          <button
            onClick={handleSubmit}
            disabled={!code.trim() || disabled}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200 ${
              code.trim() && !disabled
                ? 'bg-blue-600 hover:bg-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Submit Code
          </button>
        </div>
      )}

      {/* Results Summary */}
      {showFeedback && hasSubmitted && (
        <div className="pt-4 border-t border-gray-200 space-y-3">
          <div className="text-sm">
            <p className="font-medium text-gray-700 mb-2">Submission Summary:</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-600 mb-1">Your Output:</p>
                <div className="bg-gray-100 p-2 rounded text-xs font-mono max-h-20 overflow-y-auto">
                  {executionResult?.output || '(No output)'}
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-600 mb-1">Expected Output:</p>
                <div className="bg-green-50 p-2 rounded text-xs font-mono max-h-20 overflow-y-auto">
                  {question.correct_answer || '(Not specified)'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CodeEditorComponent;