import React from 'react';
import { useNavigate } from 'react-router-dom';

interface LessonNavigationProps {
  currentLessonId: number;
  previousLessonId?: number;
  nextLessonId?: number;
  onPrevious?: () => void;
  onNext?: () => void;
  showBackToLessons?: boolean;
}

const LessonNavigation: React.FC<LessonNavigationProps> = ({
  currentLessonId,
  previousLessonId,
  nextLessonId,
  onPrevious,
  onNext,
  showBackToLessons = true,
}) => {
  const navigate = useNavigate();

  const handleBackToLessons = () => {
    navigate('/lessons');
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center justify-between">
        {/* Left side - Back to lessons */}
        {showBackToLessons && (
          <button
            onClick={handleBackToLessons}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="font-medium">Back to Lessons</span>
          </button>
        )}

        {/* Center - Current lesson indicator */}
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <span>📖</span>
          <span>Lesson {currentLessonId}</span>
        </div>

        {/* Right side - Previous/Next navigation */}
        <div className="flex items-center space-x-2">
          {previousLessonId && onPrevious && (
            <button
              onClick={onPrevious}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors duration-200"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span>Previous</span>
            </button>
          )}

          {nextLessonId && onNext && (
            <button
              onClick={onNext}
              className="flex items-center space-x-1 px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-200"
            >
              <span>Next</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default LessonNavigation;