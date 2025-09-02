import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Question } from '../types';
import ApiClient from '../utils/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import MonacoCodeEditor from '../components/code/MonacoCodeEditor';
import { useResponsive } from '../hooks/useResponsive';

interface TestCase {
  input: string;
  expected_output: string;
  description?: string;
}

interface CodeChallenge extends Question {
  test_cases?: TestCase[];
  starter_code?: string;
  solution?: string;
}

const CodeEditorPage: React.FC = () => {
  const { questionId } = useParams<{ questionId: string }>();
  const navigate = useNavigate();
  const { isMobile, isTablet } = useResponsive();
  const [challenge, setChallenge] = useState<CodeChallenge | null>(null);
  const [code, setCode] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [testResults, setTestResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (questionId) {
      fetchChallenge(parseInt(questionId));
    }
  }, [questionId]);

  const fetchChallenge = async (id: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await ApiClient.get(`/questions/${id}`);
      if (!response.ok) {
        throw new Error('Challenge not found');
      }

      const data = await response.json();
      setChallenge(data);
      setCode(data.starter_code || getDefaultCode(data));
    } catch (err) {
      console.error('Error fetching challenge:', err);
      setError(err instanceof Error ? err.message : 'Failed to load challenge');
    } finally {
      setLoading(false);
    }
  };

  const getDefaultCode = (challenge: CodeChallenge): string => {
    const language = getLanguageFromChallenge(challenge);
    
    if (language === 'python') {
      return '# Write your Python solution here\ndef solution():\n    pass\n\n# Test your solution\nif __name__ == "__main__":\n    result = solution()\n    print(result)';
    } else if (language === 'cpp') {
      return '#include <iostream>\n#include <vector>\n#include <string>\nusing namespace std;\n\n// Write your C++ solution here\nint main() {\n    // Your code here\n    \n    return 0;\n}';
    }
    
    return '// Write your solution here\n';
  };

  const getLanguageFromChallenge = (challenge: CodeChallenge): 'python' | 'cpp' => {
    const questionText = challenge.question_text.toLowerCase();
    if (questionText.includes('c++') || questionText.includes('cpp')) return 'cpp';
    return 'python';
  };

  const handleRunCode = async () => {
    if (!challenge || isRunning) return;
    
    setIsRunning(true);
    setExecutionResult(null);
    
    try {
      const language = getLanguageFromChallenge(challenge);
      
      const response = await fetch('/api/execute/run', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          code: code,
          language: language,
          input: '',
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

  const handleRunTests = async () => {
    if (!challenge || !challenge.test_cases || isRunning) return;
    
    setIsRunning(true);
    setTestResults([]);
    
    try {
      const language = getLanguageFromChallenge(challenge);
      const results = [];
      
      for (let i = 0; i < challenge.test_cases.length; i++) {
        const testCase = challenge.test_cases[i];
        
        const response = await fetch('/api/execute/run', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            code: code,
            language: language,
            input: testCase.input,
          }),
        });

        if (response.ok) {
          const result = await response.json();
          const passed = result.output?.trim() === testCase.expected_output.trim();
          
          results.push({
            testCase: i + 1,
            input: testCase.input,
            expected: testCase.expected_output,
            actual: result.output || '',
            passed,
            error: result.error,
            description: testCase.description,
          });
        } else {
          results.push({
            testCase: i + 1,
            input: testCase.input,
            expected: testCase.expected_output,
            actual: '',
            passed: false,
            error: 'Failed to execute test',
            description: testCase.description,
          });
        }
      }
      
      setTestResults(results);
    } catch (error) {
      console.error('Error running tests:', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = async () => {
    if (!challenge || isSubmitting) return;
    
    setIsSubmitting(true);
    
    try {
      const response = await ApiClient.post('/questions/submit', {
        question_id: challenge.id,
        user_answer: code,
      });

      if (response.ok) {
        // Navigate back or show success message
        navigate(-1);
      }
    } catch (error) {
      console.error('Error submitting solution:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !challenge) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <h3 className="text-lg font-medium text-red-900 mb-2">Challenge Not Found</h3>
          <p className="text-red-700 mb-4">{error || 'The requested challenge could not be found.'}</p>
          <button
            onClick={() => navigate(-1)}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const passedTests = testResults.filter(result => result.passed).length;
  const totalTests = testResults.length;

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="font-medium">Back</span>
          </button>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">⭐ {challenge.xp_reward} XP</span>
            {testResults.length > 0 && (
              <span className={`text-sm font-medium ${
                passedTests === totalTests ? 'text-green-600' : 'text-orange-600'
              }`}>
                {passedTests}/{totalTests} tests passed
              </span>
            )}
          </div>
        </div>

        <h1 className="text-2xl font-bold text-gray-900 mb-2">{challenge.question_text}</h1>
        {challenge.explanation && (
          <p className="text-gray-600">{challenge.explanation}</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Code Editor */}
        <div className="space-y-4">
          <MonacoCodeEditor
            language={getLanguageFromChallenge(challenge)}
            value={code}
            onChange={setCode}
            onRun={handleRunCode}
            isRunning={isRunning}
            height="500px"
            theme="vs-dark"
            showRunButton={true}
            executionResult={executionResult}
          />

          {/* Action Buttons */}
          <div className="flex space-x-3">
            {challenge.test_cases && challenge.test_cases.length > 0 && (
              <button
                onClick={handleRunTests}
                disabled={isRunning || !code.trim()}
                className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
                  isRunning || !code.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-orange-600 hover:bg-orange-700 text-white'
                }`}
              >
                {isRunning ? 'Running Tests...' : 'Run Tests'}
              </button>
            )}
            
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || !code.trim()}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-colors duration-200 ${
                isSubmitting || !code.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {isSubmitting ? 'Submitting...' : 'Submit Solution'}
            </button>
          </div>
        </div>

        {/* Test Results & Info */}
        <div className="space-y-4">
          {/* Test Cases */}
          {challenge.test_cases && challenge.test_cases.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200 p-4">
                <h3 className="text-lg font-medium text-gray-900">Test Cases</h3>
              </div>
              <div className="p-4 space-y-3">
                {challenge.test_cases.map((testCase, index) => (
                  <div key={index} className="border border-gray-200 rounded p-3">
                    <div className="text-sm">
                      <div className="font-medium text-gray-700 mb-1">
                        Test Case {index + 1}
                        {testCase.description && (
                          <span className="font-normal text-gray-600"> - {testCase.description}</span>
                        )}
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-xs">
                        <div>
                          <span className="text-gray-600">Input:</span>
                          <pre className="bg-gray-100 p-1 rounded mt-1">{testCase.input || '(empty)'}</pre>
                        </div>
                        <div>
                          <span className="text-gray-600">Expected:</span>
                          <pre className="bg-gray-100 p-1 rounded mt-1">{testCase.expected_output}</pre>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Test Results */}
          {testResults.length > 0 && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200 p-4">
                <h3 className="text-lg font-medium text-gray-900">Test Results</h3>
              </div>
              <div className="p-4 space-y-3">
                {testResults.map((result, index) => (
                  <div key={index} className={`border rounded p-3 ${
                    result.passed ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-sm">
                        Test Case {result.testCase}
                      </span>
                      <span className={`text-xs font-medium ${
                        result.passed ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {result.passed ? '✓ PASSED' : '✗ FAILED'}
                      </span>
                    </div>
                    {!result.passed && (
                      <div className="text-xs space-y-1">
                        <div>
                          <span className="text-gray-600">Expected:</span>
                          <pre className="bg-white p-1 rounded">{result.expected}</pre>
                        </div>
                        <div>
                          <span className="text-gray-600">Got:</span>
                          <pre className="bg-white p-1 rounded">{result.actual}</pre>
                        </div>
                        {result.error && (
                          <div>
                            <span className="text-red-600">Error:</span>
                            <pre className="bg-white p-1 rounded text-red-600">{result.error}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CodeEditorPage;