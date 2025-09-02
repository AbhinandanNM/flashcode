import React from 'react';
import { Question } from '../../types';
import MCQComponent from './MCQComponent';
import FillBlankComponent from './FillBlankComponent';
import FlashcardComponent from './FlashcardComponent';
import CodeEditorComponent from './CodeEditorComponent';

interface QuestionRendererProps {
  question: Question;
  userAnswer?: string;
  onAnswerSubmit: (answer: string) => void;
  onAnswerChange?: (answer: string) => void;
  showFeedback?: boolean;
  isCorrect?: boolean;
  explanation?: string;
  disabled?: boolean;
}

const QuestionRenderer: React.FC<QuestionRendererProps> = ({
  question,
  userAnswer = '',
  onAnswerSubmit,
  onAnswerChange,
  showFeedback = false,
  isCorrect,
  explanation,
  disabled = false,
}) => {
  const renderQuestionComponent = () => {
    const commonProps = {
      question,
      userAnswer,
      onAnswerSubmit,
      onAnswerChange,
      showFeedback,
      isCorrect,
      explanation,
      disabled,
    };

    switch (question.type) {
      case 'mcq':
        return <MCQComponent {...commonProps} />;
      case 'fill_blank':
        return <FillBlankComponent {...commonProps} />;
      case 'flashcard':
        return <FlashcardComponent {...commonProps} />;
      case 'code':
        return <CodeEditorComponent {...commonProps} />;
      default:
        return (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">
              Unsupported question type: {question.type}
            </p>
          </div>
        );
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Question Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-600">
              Question {question.id}
            </span>
            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
              question.type === 'mcq' ? 'bg-blue-100 text-blue-800' :
              question.type === 'fill_blank' ? 'bg-green-100 text-green-800' :
              question.type === 'flashcard' ? 'bg-purple-100 text-purple-800' :
              question.type === 'code' ? 'bg-orange-100 text-orange-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {question.type === 'mcq' ? 'Multiple Choice' :
               question.type === 'fill_blank' ? 'Fill in the Blank' :
               question.type === 'flashcard' ? 'Flashcard' :
               question.type === 'code' ? 'Code Challenge' :
               question.type}
            </span>
          </div>
          <div className="flex items-center space-x-1 text-sm text-gray-600">
            <span>⭐</span>
            <span>{question.xp_reward} XP</span>
          </div>
        </div>
        
        <h3 className="text-lg font-medium text-gray-900">
          {question.question_text}
        </h3>
      </div>

      {/* Question Content */}
      <div className="p-4">
        {renderQuestionComponent()}
      </div>

      {/* Feedback Section */}
      {showFeedback && (
        <div className={`border-t border-gray-200 p-4 ${
          isCorrect ? 'bg-green-50' : 'bg-red-50'
        }`}>
          <div className="flex items-start space-x-3">
            <div className={`flex-shrink-0 ${
              isCorrect ? 'text-green-600' : 'text-red-600'
            }`}>
              {isCorrect ? (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              )}
            </div>
            <div>
              <p className={`font-medium ${
                isCorrect ? 'text-green-800' : 'text-red-800'
              }`}>
                {isCorrect ? 'Correct!' : 'Incorrect'}
              </p>
              {explanation && (
                <p className={`mt-1 text-sm ${
                  isCorrect ? 'text-green-700' : 'text-red-700'
                }`}>
                  {explanation}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuestionRenderer;