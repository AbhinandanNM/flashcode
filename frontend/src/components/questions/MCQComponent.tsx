import React, { useState } from 'react';
import { Question } from '../../types';

interface MCQComponentProps {
  question: Question;
  userAnswer?: string;
  onAnswerSubmit: (answer: string) => void;
  onAnswerChange?: (answer: string) => void;
  showFeedback?: boolean;
  isCorrect?: boolean;
  explanation?: string;
  disabled?: boolean;
}

const MCQComponent: React.FC<MCQComponentProps> = ({
  question,
  userAnswer = '',
  onAnswerSubmit,
  onAnswerChange,
  showFeedback = false,
  isCorrect,
  disabled = false,
}) => {
  const [selectedOption, setSelectedOption] = useState<string>(userAnswer);
  const [hasSubmitted, setHasSubmitted] = useState(showFeedback);

  // Parse options from question.options (expected to be an array of strings)
  const options = Array.isArray(question.options) ? question.options : [];

  const handleOptionSelect = (option: string) => {
    if (disabled || hasSubmitted) return;
    
    setSelectedOption(option);
    if (onAnswerChange) {
      onAnswerChange(option);
    }
  };

  const handleSubmit = () => {
    if (!selectedOption || disabled || hasSubmitted) return;
    
    setHasSubmitted(true);
    onAnswerSubmit(selectedOption);
  };

  const getOptionStyle = (option: string) => {
    const baseStyle = "w-full text-left p-4 rounded-lg border-2 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500";
    
    if (showFeedback && hasSubmitted) {
      if (option === question.correct_answer) {
        return `${baseStyle} border-green-500 bg-green-50 text-green-800`;
      } else if (option === selectedOption && option !== question.correct_answer) {
        return `${baseStyle} border-red-500 bg-red-50 text-red-800`;
      } else {
        return `${baseStyle} border-gray-200 bg-gray-50 text-gray-600`;
      }
    }
    
    if (selectedOption === option) {
      return `${baseStyle} border-blue-500 bg-blue-50 text-blue-800`;
    }
    
    return `${baseStyle} border-gray-200 hover:border-gray-300 hover:bg-gray-50`;
  };

  const getOptionIcon = (option: string) => {
    if (showFeedback && hasSubmitted) {
      if (option === question.correct_answer) {
        return (
          <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      } else if (option === selectedOption && option !== question.correct_answer) {
        return (
          <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      }
    }
    
    return (
      <div className={`w-5 h-5 rounded-full border-2 ${
        selectedOption === option 
          ? 'border-blue-500 bg-blue-500' 
          : 'border-gray-300'
      }`}>
        {selectedOption === option && (
          <div className="w-full h-full rounded-full bg-white scale-50"></div>
        )}
      </div>
    );
  };

  if (options.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-700">
          No options available for this question.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Options */}
      <div className="space-y-3">
        {options.map((option, index) => (
          <button
            key={index}
            onClick={() => handleOptionSelect(option)}
            disabled={disabled || hasSubmitted}
            className={getOptionStyle(option)}
          >
            <div className="flex items-center space-x-3">
              {getOptionIcon(option)}
              <span className="flex-1 text-left">{option}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Submit Button */}
      {!showFeedback && !hasSubmitted && (
        <div className="pt-4">
          <button
            onClick={handleSubmit}
            disabled={!selectedOption || disabled}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200 ${
              selectedOption && !disabled
                ? 'bg-blue-600 hover:bg-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Submit Answer
          </button>
        </div>
      )}

      {/* Results Summary */}
      {showFeedback && hasSubmitted && (
        <div className="pt-4 border-t border-gray-200">
          <div className="text-sm text-gray-600">
            <p>Your answer: <span className="font-medium">{selectedOption}</span></p>
            <p>Correct answer: <span className="font-medium text-green-600">{question.correct_answer}</span></p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MCQComponent;