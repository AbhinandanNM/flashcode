import React, { useState } from 'react';
import { Question } from '../../types';
import { useResponsive } from '../../hooks/useResponsive';
import { useSwipeGesture, useDoubleTap } from '../../hooks/useTouchGestures';

interface FlashcardComponentProps {
  question: Question;
  userAnswer?: string;
  onAnswerSubmit: (answer: string) => void;
  onAnswerChange?: (answer: string) => void;
  showFeedback?: boolean;
  isCorrect?: boolean;
  explanation?: string;
  disabled?: boolean;
}

const FlashcardComponent: React.FC<FlashcardComponentProps> = ({
  question,
  userAnswer = '',
  onAnswerSubmit,
  onAnswerChange,
  showFeedback = false,
  isCorrect,
  disabled = false,
}) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [hasSubmitted, setHasSubmitted] = useState(showFeedback);
  const { isMobile, isTablet } = useResponsive();

  const handleFlip = () => {
    if (disabled) return;
    setIsFlipped(!isFlipped);
  };

  const handleDifficultySelect = (difficulty: string) => {
    if (disabled || hasSubmitted) return;
    
    setSelectedDifficulty(difficulty);
    if (onAnswerChange) {
      onAnswerChange(difficulty);
    }
  };

  const handleSubmit = () => {
    if (!selectedDifficulty || disabled || hasSubmitted) return;
    
    setHasSubmitted(true);
    onAnswerSubmit(selectedDifficulty);
  };

  // Touch gesture handlers
  const swipeRef = useSwipeGesture((direction) => {
    if (disabled) return;
    
    if (direction === 'left' || direction === 'right') {
      handleFlip();
    } else if (isFlipped && !hasSubmitted) {
      if (direction === 'up') {
        handleDifficultySelect('easy');
      } else if (direction === 'down') {
        handleDifficultySelect('hard');
      }
    }
  });

  const doubleTapRef = useDoubleTap(() => {
    if (!disabled && !hasSubmitted) {
      handleFlip();
    }
  });

  // Combine refs for touch gestures
  const cardRef = (element: HTMLDivElement | null) => {
    if (swipeRef.current !== element) {
      swipeRef.current = element;
    }
    if (doubleTapRef.current !== element) {
      doubleTapRef.current = element;
    }
  };

  const difficultyOptions = [
    { value: 'easy', label: 'Easy', color: 'bg-green-500 hover:bg-green-600', description: 'I knew this well' },
    { value: 'medium', label: 'Medium', color: 'bg-yellow-500 hover:bg-yellow-600', description: 'I had to think about it' },
    { value: 'hard', label: 'Hard', color: 'bg-red-500 hover:bg-red-600', description: 'I struggled with this' },
  ];

  const getDifficultyButtonStyle = (difficulty: string) => {
    const option = difficultyOptions.find(opt => opt.value === difficulty);
    const baseStyle = "flex-1 py-3 px-4 rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2";
    
    if (selectedDifficulty === difficulty) {
      return `${baseStyle} ${option?.color} text-white ring-2 ring-offset-2 ring-gray-400`;
    }
    
    return `${baseStyle} ${option?.color} text-white opacity-80 hover:opacity-100`;
  };

  return (
    <div className={`space-y-6 ${isMobile ? 'px-4' : ''}`}>
      {/* Flashcard */}
      <div className="relative">
        <div 
          ref={cardRef}
          className={`relative w-full ${
            isMobile ? 'min-h-64' : 'min-h-48'
          } cursor-pointer transition-transform duration-500 transform-style-preserve-3d ${
            isFlipped ? 'rotate-y-180' : ''
          } touch-manipulation`}
          onClick={handleFlip}
        >
          {/* Front of card */}
          <div className={`absolute inset-0 w-full h-full backface-hidden ${
            isFlipped ? 'rotate-y-180' : ''
          }`}>
            <div className={`bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl ${
              isMobile ? 'p-8' : 'p-6'
            } text-white shadow-lg h-full flex flex-col justify-center items-center text-center`}>
              <div className="mb-4">
                <svg className={`${isMobile ? 'w-10 h-10' : 'w-8 h-8'} mx-auto mb-2 opacity-80`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className={`${isMobile ? 'text-2xl' : 'text-xl'} font-semibold mb-2`}>Question</h3>
              <p className={`${isMobile ? 'text-xl' : 'text-lg'} leading-relaxed`}>{question.question_text}</p>
              <div className={`mt-4 ${isMobile ? 'text-base' : 'text-sm'} opacity-80`}>
                {isMobile ? 'Tap, double-tap, or swipe to reveal answer' : 'Click to reveal answer'}
              </div>
            </div>
          </div>

          {/* Back of card */}
          <div className={`absolute inset-0 w-full h-full backface-hidden rotate-y-180 ${
            isFlipped ? '' : 'rotate-y-180'
          }`}>
            <div className={`bg-gradient-to-br from-green-500 to-green-600 rounded-xl ${
              isMobile ? 'p-8' : 'p-6'
            } text-white shadow-lg h-full flex flex-col justify-center items-center text-center`}>
              <div className="mb-4">
                <svg className={`${isMobile ? 'w-10 h-10' : 'w-8 h-8'} mx-auto mb-2 opacity-80`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className={`${isMobile ? 'text-2xl' : 'text-xl'} font-semibold mb-2`}>Answer</h3>
              <p className={`${isMobile ? 'text-xl' : 'text-lg'} leading-relaxed`}>{question.correct_answer}</p>
              {question.explanation && (
                <div className={`mt-4 ${isMobile ? 'text-base' : 'text-sm'} opacity-90 border-t border-white/20 pt-4`}>
                  <p>{question.explanation}</p>
                </div>
              )}
              <div className={`mt-4 ${isMobile ? 'text-base' : 'text-sm'} opacity-80`}>
                {isMobile ? 'Swipe up/down to rate difficulty' : 'Click to flip back'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Instructions */}
      {!isFlipped && !hasSubmitted && (
        <div className="text-center text-gray-600">
          <p className="text-sm">💡 Click the card to reveal the answer, then rate how well you knew it.</p>
        </div>
      )}

      {/* Difficulty Rating */}
      {isFlipped && !hasSubmitted && !showFeedback && (
        <div className="space-y-4">
          <div className="text-center">
            <h4 className="text-lg font-medium text-gray-900 mb-2">How well did you know this?</h4>
            <p className="text-sm text-gray-600">Your rating helps us schedule when to show this card again.</p>
          </div>
          
          <div className={`flex ${isMobile ? 'flex-col space-y-3' : 'space-x-3'}`}>
            {difficultyOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleDifficultySelect(option.value)}
                disabled={disabled}
                className={`${getDifficultyButtonStyle(option.value)} ${
                  isMobile ? 'py-4 text-lg' : ''
                } touch-manipulation`}
              >
                <div>
                  <div className="font-medium">{option.label}</div>
                  <div className={`${isMobile ? 'text-sm' : 'text-xs'} opacity-90 mt-1`}>
                    {option.description}
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Submit Button */}
      {isFlipped && selectedDifficulty && !hasSubmitted && !showFeedback && (
        <div className="pt-2">
          <button
            onClick={handleSubmit}
            disabled={disabled}
            className={`w-full ${
              isMobile ? 'py-4 text-lg' : 'py-3'
            } px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 touch-manipulation`}
          >
            Submit Rating
          </button>
        </div>
      )}

      {/* Results Summary */}
      {showFeedback && hasSubmitted && (
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <p>Your rating: <span className="font-medium capitalize">{selectedDifficulty || userAnswer}</span></p>
            <p className="mt-1 text-xs">
              This card will be scheduled for review based on your rating.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default FlashcardComponent;