import React from 'react';
import { Lesson, Progress } from '../../types';

interface LessonCardProps {
  lesson: Lesson;
  progress?: Progress | null;
  onClick: () => void;
}

const LessonCard: React.FC<LessonCardProps> = ({ lesson, progress, onClick }) => {
  const getDifficultyColor = (difficulty: number) => {
    switch (difficulty) {
      case 1: return 'bg-green-100 text-green-800';
      case 2: return 'bg-blue-100 text-blue-800';
      case 3: return 'bg-yellow-100 text-yellow-800';
      case 4: return 'bg-orange-100 text-orange-800';
      case 5: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyText = (difficulty: number) => {
    switch (difficulty) {
      case 1: return 'Beginner';
      case 2: return 'Easy';
      case 3: return 'Medium';
      case 4: return 'Hard';
      case 5: return 'Expert';
      default: return 'Unknown';
    }
  };

  const getLanguageIcon = (language: string) => {
    switch (language.toLowerCase()) {
      case 'python':
        return '🐍';
      case 'cpp':
        return '⚡';
      default:
        return '💻';
    }
  };

  const getProgressColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-300';
    }
  };

  const getProgressText = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      default:
        return 'Not Started';
    }
  };

  return (
    <div 
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 cursor-pointer border border-gray-200"
      onClick={onClick}
    >
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">{getLanguageIcon(lesson.language)}</span>
            <div>
              <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                {lesson.title}
              </h3>
              <p className="text-sm text-gray-500 capitalize">
                {lesson.language}
              </p>
            </div>
          </div>
          
          {/* Progress indicator */}
          <div className="flex flex-col items-end">
            <div className={`w-3 h-3 rounded-full ${getProgressColor(progress?.status)}`}></div>
            <span className="text-xs text-gray-500 mt-1">
              {getProgressText(progress?.status)}
            </span>
          </div>
        </div>

        {/* Difficulty and XP */}
        <div className="flex items-center justify-between mb-4">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(lesson.difficulty)}`}>
            {getDifficultyText(lesson.difficulty)}
          </span>
          
          <div className="flex items-center space-x-1 text-sm text-gray-600">
            <span>⭐</span>
            <span>{lesson.xp_reward} XP</span>
          </div>
        </div>

        {/* Progress bar */}
        {progress && (
          <div className="mb-4">
            <div className="flex justify-between text-xs text-gray-600 mb-1">
              <span>Progress</span>
              <span>{Math.round((progress.score || 0) * 100)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(progress.status)}`}
                style={{ width: `${(progress.score || 0) * 100}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Lesson {lesson.order_index}</span>
          {progress && progress.attempts > 0 && (
            <span>{progress.attempts} attempt{progress.attempts !== 1 ? 's' : ''}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default LessonCard;