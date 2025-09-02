import React, { useState, useEffect } from 'react';
import { Question } from '../../types';

interface FlashcardReviewProps {
  questions: Question[];
  onComplete: (results: ReviewResult[]) => void;
  onExit: () => void;
}

interface ReviewResult {
  questionId: number;
  difficulty: 'easy' | 'medium' | 'hard';
  timeSpent: number;
  reviewedAt: string;
}

const FlashcardReview: React.FC<FlashcardReviewProps> = ({
  questions,
  onComplete,
  onExit,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [results, setResults] = useState<ReviewResult[]>([]);
  const [startTime, setStartTime] = useState<number>(Date.now());
  const [sessionStats, setSessionStats] = useState({
    reviewed: 0,
    easy: 0,
    medium: 0,
    hard: 0,
  });

  const currentQuestion = questions[currentIndex];
  const progress = ((currentIndex + (isFlipped ? 0.5 : 0)) / questions.length) * 100;

  useEffect(() => {
    setStartTime(Date.now());
  }, [currentIndex]);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleDifficultySelect = (difficulty: 'easy' | 'medium' | 'hard') => {
    const timeSpent = Date.now() - startTime;
    const result: ReviewResult = {
      questionId: currentQuestion.id,
      difficulty,
      timeSpent,
      reviewedAt: new Date().toISOString(),
    };

    const newResults = [...results, result];
    setResults(newResults);

    // Update session stats
    setSessionStats(prev => ({
      ...prev,
      reviewed: prev.reviewed + 1,
      [difficulty]: prev[difficulty] + 1,
    }));

    // Move to next question or complete session
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
      setIsFlipped(false);
    } else {
      onComplete(newResults);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-500 hover:bg-green-600';
      case 'medium': return 'bg-yellow-500 hover:bg-yellow-600';
      case 'hard': return 'bg-red-500 hover:bg-red-600';
      default: return 'bg-gray-500 hover:bg-gray-600';
    }
  };

  const getDifficultyDescription = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'I knew this well';
      case 'medium': return 'I had to think about it';
      case 'hard': return 'I struggled with this';
      default: return '';
    }
  };

  if (!currentQuestion) {
    return null;
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">🧠</span>
            <div>
              <h2 className="text-lg font-semibold text-gray-900">Flashcard Review</h2>
              <p className="text-sm text-gray-600">
                Card {currentIndex + 1} of {questions.length}
              </p>
            </div>
          </div>
          
          <button
            onClick={onExit}
            className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>{Math.round(progress)}% complete</span>
          <span>{questions.length - currentIndex - 1} remaining</span>
        </div>
      </div>

      {/* Flashcard */}
      <div className="relative mb-6">
        <div 
          className={`relative w-full min-h-80 cursor-pointer transition-transform duration-500 transform-style-preserve-3d ${
            isFlipped ? 'rotate-y-180' : ''
          }`}
          onClick={handleFlip}
        >
          {/* Front of card */}
          <div className={`absolute inset-0 w-full h-full backface-hidden ${
            isFlipped ? 'rotate-y-180' : ''
          }`}>
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-8 text-white shadow-lg h-full flex flex-col justify-center items-center text-center">
              <div className="mb-6">
                <svg className="w-12 h-12 mx-auto mb-4 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Question</h3>
              <p className="text-lg leading-relaxed max-w-md">
                {currentQuestion.question_text}
              </p>
              <div className="mt-8 text-sm opacity-80 animate-pulse">
                Click to reveal answer
              </div>
            </div>
          </div>

          {/* Back of card */}
          <div className={`absolute inset-0 w-full h-full backface-hidden rotate-y-180 ${
            isFlipped ? '' : 'rotate-y-180'
          }`}>
            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-8 text-white shadow-lg h-full flex flex-col justify-center items-center text-center">
              <div className="mb-6">
                <svg className="w-12 h-12 mx-auto mb-4 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-4">Answer</h3>
              <p className="text-lg leading-relaxed max-w-md mb-4">
                {currentQuestion.correct_answer}
              </p>
              {currentQuestion.explanation && (
                <div className="mt-4 text-sm opacity-90 border-t border-white/20 pt-4 max-w-md">
                  <p>{currentQuestion.explanation}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Difficulty Rating */}
      {isFlipped && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="text-center mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              How well did you know this?
            </h3>
            <p className="text-sm text-gray-600">
              Your rating helps us schedule when to show this card again.
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(['easy', 'medium', 'hard'] as const).map((difficulty) => (
              <button
                key={difficulty}
                onClick={() => handleDifficultySelect(difficulty)}
                className={`p-4 rounded-lg text-white font-medium transition-all duration-200 transform hover:scale-105 ${getDifficultyColor(difficulty)}`}
              >
                <div className="text-lg font-bold mb-1 capitalize">{difficulty}</div>
                <div className="text-sm opacity-90">
                  {getDifficultyDescription(difficulty)}
                </div>
                <div className="text-xs opacity-75 mt-2">
                  {difficulty === 'easy' ? 'Review in 4 days' :
                   difficulty === 'medium' ? 'Review in 1 day' :
                   'Review in 10 minutes'}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Instructions */}
      {!isFlipped && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <p className="text-blue-800 text-sm">
            💡 Read the question carefully, then click the card to reveal the answer.
          </p>
        </div>
      )}

      {/* Session Stats */}
      <div className="mt-6 bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Session Progress</h4>
        <div className="grid grid-cols-4 gap-4 text-center text-sm">
          <div>
            <div className="font-semibold text-gray-900">{sessionStats.reviewed}</div>
            <div className="text-gray-600">Reviewed</div>
          </div>
          <div>
            <div className="font-semibold text-green-600">{sessionStats.easy}</div>
            <div className="text-gray-600">Easy</div>
          </div>
          <div>
            <div className="font-semibold text-yellow-600">{sessionStats.medium}</div>
            <div className="text-gray-600">Medium</div>
          </div>
          <div>
            <div className="font-semibold text-red-600">{sessionStats.hard}</div>
            <div className="text-gray-600">Hard</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FlashcardReview;