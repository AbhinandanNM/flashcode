import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { CelebrationAnimation } from '../gamification';

interface DuelResultsProps {
  duelId: string;
  result: 'win' | 'lose' | 'draw';
  opponent: {
    id: number;
    username: string;
    submittedAt?: string;
    isCorrect?: boolean;
    executionTime?: number;
  };
  myStats: {
    submittedAt?: string;
    isCorrect?: boolean;
    executionTime?: number;
  };
  question: {
    question_text: string;
    correct_answer: string;
    xp_reward: number;
  };
  xpGained: number;
  onPlayAgain: () => void;
  onBackToMenu: () => void;
}

const DuelResults: React.FC<DuelResultsProps> = ({
  duelId,
  result,
  opponent,
  myStats,
  question,
  xpGained,
  onPlayAgain,
  onBackToMenu,
}) => {
  const { state } = useAuth();
  const [showCelebration, setShowCelebration] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (result === 'win') {
      setShowCelebration(true);
    }
  }, [result]);

  const getResultIcon = () => {
    switch (result) {
      case 'win':
        return '🏆';
      case 'lose':
        return '😔';
      case 'draw':
        return '🤝';
      default:
        return '❓';
    }
  };

  const getResultColor = () => {
    switch (result) {
      case 'win':
        return 'from-green-400 to-emerald-500';
      case 'lose':
        return 'from-red-400 to-rose-500';
      case 'draw':
        return 'from-yellow-400 to-orange-500';
      default:
        return 'from-gray-400 to-gray-500';
    }
  };

  const getResultTitle = () => {
    switch (result) {
      case 'win':
        return 'Victory!';
      case 'lose':
        return 'Defeat';
      case 'draw':
        return 'Draw';
      default:
        return 'Result';
    }
  };

  const getResultMessage = () => {
    switch (result) {
      case 'win':
        return 'Congratulations! You outpaced your opponent!';
      case 'lose':
        return 'Better luck next time! Keep practicing!';
      case 'draw':
        return 'Great minds think alike! It\'s a tie!';
      default:
        return 'Duel completed.';
    }
  };

  const formatTime = (ms?: number) => {
    if (!ms) return 'N/A';
    return `${(ms / 1000).toFixed(2)}s`;
  };

  const getWinReason = () => {
    if (result !== 'win') return null;

    if (myStats.isCorrect && !opponent.isCorrect) {
      return 'Your solution was correct while your opponent\'s was not!';
    }
    
    if (myStats.isCorrect && opponent.isCorrect) {
      if (myStats.submittedAt && opponent.submittedAt) {
        const myTime = new Date(myStats.submittedAt).getTime();
        const opponentTime = new Date(opponent.submittedAt).getTime();
        if (myTime < opponentTime) {
          return 'Both solutions were correct, but you were faster!';
        }
      }
      if (myStats.executionTime && opponent.executionTime && myStats.executionTime < opponent.executionTime) {
        return 'Both solutions were correct, but yours was more efficient!';
      }
    }

    return 'You performed better overall!';
  };

  return (
    <>
      <CelebrationAnimation
        show={showCelebration}
        type="achievement"
        message={`You won the duel against ${opponent.username}!`}
        achievementIcon="🏆"
        onComplete={() => setShowCelebration(false)}
        duration={3000}
      />

      <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden max-w-2xl mx-auto">
        {/* Header */}
        <div className={`bg-gradient-to-r ${getResultColor()} text-white p-6 text-center`}>
          <div className="text-6xl mb-4">{getResultIcon()}</div>
          <h1 className="text-3xl font-bold mb-2">{getResultTitle()}</h1>
          <p className="text-lg opacity-90">{getResultMessage()}</p>
          {result === 'win' && getWinReason() && (
            <p className="text-sm mt-2 bg-white/20 rounded-lg p-2">
              {getWinReason()}
            </p>
          )}
        </div>

        {/* XP Reward */}
        <div className="p-6 border-b border-gray-200">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <span className="text-2xl">⭐</span>
              <span className="text-2xl font-bold text-yellow-600">+{xpGained} XP</span>
            </div>
            <p className="text-gray-600">
              {result === 'win' ? 'Victory bonus included!' : 
               result === 'draw' ? 'Participation reward' : 
               'Better luck next time!'}
            </p>
          </div>
        </div>

        {/* Duel Summary */}
        <div className="p-6 border-b border-gray-200">
          <div className="grid grid-cols-2 gap-6">
            {/* Your Performance */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-blue-100 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-blue-600">
                  {state.user?.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">
                {state.user?.username} (You)
              </h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${
                    myStats.isCorrect ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {myStats.isCorrect ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Time:</span>
                  <span className="font-medium">{formatTime(myStats.executionTime)}</span>
                </div>
                {myStats.submittedAt && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Submitted:</span>
                    <span className="font-medium">
                      {new Date(myStats.submittedAt).toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Opponent Performance */}
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-3 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-2xl font-bold text-red-600">
                  {opponent.username.charAt(0).toUpperCase()}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">{opponent.username}</h3>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${
                    opponent.isCorrect ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {opponent.isCorrect ? '✓ Correct' : '✗ Incorrect'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Time:</span>
                  <span className="font-medium">{formatTime(opponent.executionTime)}</span>
                </div>
                {opponent.submittedAt && (
                  <div className="flex justify-between">
                    <span className="text-gray-600">Submitted:</span>
                    <span className="font-medium">
                      {new Date(opponent.submittedAt).toLocaleTimeString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Question Details */}
        <div className="p-6 border-b border-gray-200">
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="w-full flex items-center justify-between text-left"
          >
            <h3 className="font-semibold text-gray-900">Challenge Details</h3>
            <svg 
              className={`w-5 h-5 text-gray-500 transition-transform duration-200 ${
                showDetails ? 'rotate-180' : ''
              }`} 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          {showDetails && (
            <div className="mt-4 space-y-3">
              <div>
                <h4 className="font-medium text-gray-700 mb-1">Question:</h4>
                <p className="text-gray-600 text-sm">{question.question_text}</p>
              </div>
              <div>
                <h4 className="font-medium text-gray-700 mb-1">Expected Solution:</h4>
                <pre className="bg-gray-100 p-3 rounded text-xs font-mono overflow-x-auto">
                  {question.correct_answer}
                </pre>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-6">
          <div className="flex space-x-4">
            <button
              onClick={onPlayAgain}
              className="flex-1 bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white font-medium py-3 px-4 rounded-lg transition-all duration-200"
            >
              Play Again
            </button>
            <button
              onClick={onBackToMenu}
              className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
            >
              Back to Menu
            </button>
          </div>
        </div>

        {/* Duel Info */}
        <div className="px-6 pb-6">
          <div className="text-center text-xs text-gray-500">
            Duel ID: {duelId.slice(-8).toUpperCase()} • 
            Completed at {new Date().toLocaleTimeString()}
          </div>
        </div>
      </div>
    </>
  );
};

export default DuelResults;