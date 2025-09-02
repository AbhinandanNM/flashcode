import React, { useState, useEffect } from 'react';
import { Question } from '../../types';

interface FillBlankComponentProps {
  question: Question;
  userAnswer?: string;
  onAnswerSubmit: (answer: string) => void;
  onAnswerChange?: (answer: string) => void;
  showFeedback?: boolean;
  isCorrect?: boolean;
  explanation?: string;
  disabled?: boolean;
}

const FillBlankComponent: React.FC<FillBlankComponentProps> = ({
  question,
  userAnswer = '',
  onAnswerSubmit,
  onAnswerChange,
  showFeedback = false,
  isCorrect,
  disabled = false,
}) => {
  const [answers, setAnswers] = useState<string[]>([]);
  const [hasSubmitted, setHasSubmitted] = useState(showFeedback);
  const [blanks, setBlanks] = useState<string[]>([]);

  useEffect(() => {
    // Parse the question text to find blanks (marked with _____ or {blank})
    const questionText = question.question_text;
    const blankMatches = questionText.match(/(_____|\{blank\})/g) || [];
    setBlanks(blankMatches);
    
    // Initialize answers array
    if (userAnswer) {
      // If userAnswer is provided, try to parse it (assuming it's JSON or comma-separated)
      try {
        const parsedAnswers = JSON.parse(userAnswer);
        setAnswers(Array.isArray(parsedAnswers) ? parsedAnswers : [userAnswer]);
      } catch {
        // If not JSON, treat as single answer or comma-separated
        setAnswers(userAnswer.includes(',') ? userAnswer.split(',').map(a => a.trim()) : [userAnswer]);
      }
    } else {
      setAnswers(new Array(blankMatches.length).fill(''));
    }
  }, [question.question_text, userAnswer]);

  const handleAnswerChange = (index: number, value: string) => {
    if (disabled || hasSubmitted) return;
    
    const newAnswers = [...answers];
    newAnswers[index] = value;
    setAnswers(newAnswers);
    
    if (onAnswerChange) {
      onAnswerChange(JSON.stringify(newAnswers));
    }
  };

  const handleSubmit = () => {
    if (disabled || hasSubmitted) return;
    
    const allAnswersFilled = answers.every(answer => answer.trim() !== '');
    if (!allAnswersFilled) return;
    
    setHasSubmitted(true);
    onAnswerSubmit(JSON.stringify(answers));
  };

  const renderQuestionWithBlanks = () => {
    const questionText = question.question_text;
    const parts = questionText.split(/(_____|\{blank\})/);
    let blankIndex = 0;

    return parts.map((part, index) => {
      if (part === '_____' || part === '{blank}') {
        const currentBlankIndex = blankIndex++;
        const answer = answers[currentBlankIndex] || '';
        
        return (
          <span key={index} className="inline-block mx-1">
            <input
              type="text"
              value={answer}
              onChange={(e) => handleAnswerChange(currentBlankIndex, e.target.value)}
              disabled={disabled || hasSubmitted}
              placeholder="Your answer"
              className={`inline-block min-w-24 px-2 py-1 text-center border-b-2 bg-transparent focus:outline-none transition-colors duration-200 ${
                showFeedback && hasSubmitted
                  ? isCorrect
                    ? 'border-green-500 text-green-700'
                    : 'border-red-500 text-red-700'
                  : 'border-blue-300 focus:border-blue-500'
              }`}
              style={{ width: `${Math.max(answer.length + 2, 8)}ch` }}
            />
          </span>
        );
      }
      return <span key={index}>{part}</span>;
    });
  };

  const getCorrectAnswers = () => {
    try {
      const correctAnswers = JSON.parse(question.correct_answer);
      return Array.isArray(correctAnswers) ? correctAnswers : [question.correct_answer];
    } catch {
      return [question.correct_answer];
    }
  };

  const allAnswersFilled = answers.every(answer => answer.trim() !== '');
  const correctAnswers = getCorrectAnswers();

  return (
    <div className="space-y-4">
      {/* Question with blanks */}
      <div className="text-lg leading-relaxed">
        {renderQuestionWithBlanks()}
      </div>

      {/* Instructions */}
      {!hasSubmitted && (
        <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
          <p>💡 Fill in the blank{blanks.length > 1 ? 's' : ''} with the correct answer{blanks.length > 1 ? 's' : ''}.</p>
        </div>
      )}

      {/* Submit Button */}
      {!showFeedback && !hasSubmitted && (
        <div className="pt-2">
          <button
            onClick={handleSubmit}
            disabled={!allAnswersFilled || disabled}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors duration-200 ${
              allAnswersFilled && !disabled
                ? 'bg-blue-600 hover:bg-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Submit Answer{blanks.length > 1 ? 's' : ''}
          </button>
        </div>
      )}

      {/* Results Summary */}
      {showFeedback && hasSubmitted && (
        <div className="pt-4 border-t border-gray-200 space-y-2">
          <div className="text-sm">
            <p className="font-medium text-gray-700 mb-2">Answer Summary:</p>
            {answers.map((answer, index) => (
              <div key={index} className="flex justify-between items-center py-1">
                <span className="text-gray-600">Blank {index + 1}:</span>
                <div className="flex items-center space-x-2">
                  <span className={`font-medium ${
                    answer.toLowerCase().trim() === correctAnswers[index]?.toLowerCase().trim()
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}>
                    {answer}
                  </span>
                  {answer.toLowerCase().trim() !== correctAnswers[index]?.toLowerCase().trim() && (
                    <>
                      <span className="text-gray-400">→</span>
                      <span className="font-medium text-green-600">
                        {correctAnswers[index]}
                      </span>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default FillBlankComponent;