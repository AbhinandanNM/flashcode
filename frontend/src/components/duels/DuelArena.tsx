import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { MonacoCodeEditor } from '../code';
import { Question } from '../../types';

interface DuelParticipant {
  id: number;
  username: string;
  progress: number;
  isReady: boolean;
  submittedAt?: string;
  isCorrect?: boolean;
}

interface DuelArenaProps {
  duelId: string;
  question: Question;
  opponent: DuelParticipant;
  timeLimit: number; // in seconds
  onSubmit: (code: string) => void;
  onComplete: (result: 'win' | 'lose' | 'draw') => void;
  isActive: boolean;
}

const DuelArena: React.FC<DuelArenaProps> = ({
  duelId,
  question,
  opponent,
  timeLimit,
  onSubmit,
  onComplete,
  isActive,
}) => {
  const { state } = useAuth();
  const [code, setCode] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(timeLimit);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [myProgress, setMyProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [duelStatus, setDuelStatus] = useState<'waiting' | 'active' | 'completed'>('waiting');

  // Timer countdown
  useEffect(() => {
    if (!isActive || timeRemaining <= 0 || isSubmitted) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          // Time's up - auto submit
          if (!isSubmitted) {
            handleSubmit();
          }
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isActive, timeRemaining, isSubmitted]);

  // Update progress based on code length (simple metric)
  useEffect(() => {
    const progress = Math.min((code.length / 200) * 100, 100);
    setMyProgress(progress);
  }, [code]);

  const handleCodeChange = (newCode: string) => {
    if (!isSubmitted && isActive) {
      setCode(newCode);
    }
  };

  const handleRunCode = async () => {
    if (isRunning || !code.trim()) return;
    
    setIsRunning(true);
    setExecutionResult(null);
    
    try {
      const language = question.question_text.toLowerCase().includes('c++') ? 'cpp' : 'python';
      
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

      if (response.ok) {
        const result = await response.json();
        setExecutionResult({
          ...result,
          status: result.error ? 'error' : 'success'
        });
      }
    } catch (error) {
      setExecutionResult({
        error: 'Failed to execute code',
        status: 'error'
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSubmit = useCallback(() => {
    if (isSubmitted) return;
    
    setIsSubmitted(true);
    setDuelStatus('completed');
    onSubmit(code);
  }, [code, isSubmitted, onSubmit]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getTimeColor = () => {
    if (timeRemaining > 60) return 'text-green-600';
    if (timeRemaining > 30) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-yellow-500';
    return 'bg-blue-500';
  };

  const getLanguageFromQuestion = (): 'python' | 'cpp' => {
    return question.question_text.toLowerCase().includes('c++') ? 'cpp' : 'python';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
      {/* Duel Header */}
      <div className="bg-gradient-to-r from-red-500 to-orange-500 text-white p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">⚔️</span>
              <h2 className="text-xl font-bold">Code Duel</h2>
            </div>
            <div className={`text-2xl font-mono ${getTimeColor()} bg-white/20 px-3 py-1 rounded-lg`}>
              {formatTime(timeRemaining)}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className="text-sm opacity-90">Duel ID:</span>
            <span className="font-mono text-sm bg-white/20 px-2 py-1 rounded">
              {duelId.slice(-6).toUpperCase()}
            </span>
          </div>
        </div>
      </div>

      {/* Participants Progress */}
      <div className="bg-gray-50 p-4 border-b border-gray-200">
        <div className="grid grid-cols-2 gap-6">
          {/* Current User */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  {state.user?.username.charAt(0).toUpperCase()}
                </div>
                <span className="font-medium text-gray-900">
                  {state.user?.username} (You)
                </span>
              </div>
              <div className="flex items-center space-x-2">
                {isSubmitted && (
                  <span className="text-green-600 text-sm font-medium">✓ Submitted</span>
                )}
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(myProgress)}`}
                style={{ width: `${myProgress}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-600">Progress: {Math.round(myProgress)}%</div>
          </div>

          {/* Opponent */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-red-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                  {opponent.username.charAt(0).toUpperCase()}
                </div>
                <span className="font-medium text-gray-900">{opponent.username}</span>
              </div>
              <div className="flex items-center space-x-2">
                {opponent.submittedAt && (
                  <span className="text-green-600 text-sm font-medium">✓ Submitted</span>
                )}
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(opponent.progress)}`}
                style={{ width: `${opponent.progress}%` }}
              ></div>
            </div>
            <div className="text-xs text-gray-600">Progress: {Math.round(opponent.progress)}%</div>
          </div>
        </div>
      </div>

      {/* Question */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900">Challenge</h3>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">⭐ {question.xp_reward} XP</span>
            <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
              getLanguageFromQuestion() === 'python' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'
            }`}>
              {getLanguageFromQuestion() === 'python' ? '🐍 Python' : '⚡ C++'}
            </span>
          </div>
        </div>
        <p className="text-gray-700 leading-relaxed">{question.question_text}</p>
        
        {question.explanation && (
          <div className="mt-3 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">{question.explanation}</p>
          </div>
        )}
      </div>

      {/* Code Editor */}
      <div className="p-4">
        <MonacoCodeEditor
          language={getLanguageFromQuestion()}
          value={code}
          onChange={handleCodeChange}
          onRun={handleRunCode}
          isRunning={isRunning}
          disabled={isSubmitted || !isActive}
          height="350px"
          theme="vs-dark"
          showRunButton={true}
          showDebuggingHints={true}
          executionResult={executionResult}
        />
      </div>

      {/* Action Buttons */}
      <div className="p-4 bg-gray-50 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-600">
            {isSubmitted ? (
              <span className="text-green-600 font-medium">
                ✓ Code submitted! Waiting for results...
              </span>
            ) : timeRemaining <= 0 ? (
              <span className="text-red-600 font-medium">
                ⏰ Time's up! Code auto-submitted.
              </span>
            ) : (
              <span>
                💡 Write your solution and submit before time runs out!
              </span>
            )}
          </div>
          
          <div className="flex items-center space-x-3">
            {!isSubmitted && isActive && timeRemaining > 0 && (
              <button
                onClick={handleSubmit}
                disabled={!code.trim()}
                className={`px-6 py-2 rounded-lg font-medium transition-colors duration-200 ${
                  code.trim()
                    ? 'bg-green-600 hover:bg-green-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Submit Solution
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Status Messages */}
      {duelStatus === 'waiting' && (
        <div className="p-4 bg-yellow-50 border-t border-yellow-200">
          <div className="flex items-center space-x-2 text-yellow-800">
            <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="font-medium">Waiting for opponent to join...</span>
          </div>
        </div>
      )}

      {duelStatus === 'completed' && (
        <div className="p-4 bg-blue-50 border-t border-blue-200">
          <div className="flex items-center space-x-2 text-blue-800">
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Duel completed! Evaluating results...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default DuelArena;