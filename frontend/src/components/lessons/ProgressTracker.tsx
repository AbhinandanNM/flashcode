import React from 'react';
import { Progress } from '../../types';

interface ProgressTrackerProps {
  progress: Progress | null;
  lessonTitle: string;
  totalQuestions?: number;
  completedQuestions?: number;
}

const ProgressTracker: React.FC<ProgressTrackerProps> = ({
  progress,
  lessonTitle,
  totalQuestions = 0,
  completedQuestions = 0,
}) => {
  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'in_progress':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'in_progress':
        return '🔄';
      default:
        return '⏳';
    }
  };

  const getStatusText = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'Completed';
      case 'in_progress':
        return 'In Progress';
      default:
        return 'Not Started';
    }
  };

  const progressPercentage = progress ? Math.round((progress.score || 0) * 100) : 0;
  const questionsProgress = totalQuestions > 0 ? Math.round((completedQuestions / totalQuestions) * 100) : 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Progress Tracker</h3>
      
      {/* Lesson Status */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Lesson Status</span>
          <div className={`flex items-center space-x-1 ${getStatusColor(progress?.status)}`}>
            <span>{getStatusIcon(progress?.status)}</span>
            <span className="text-sm font-medium">{getStatusText(progress?.status)}</span>
          </div>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ${
              progress?.status === 'completed' ? 'bg-green-500' :
              progress?.status === 'in_progress' ? 'bg-yellow-500' : 'bg-gray-400'
            }`}
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>
        
        <div className="flex justify-between text-xs text-gray-600 mt-1">
          <span>{lessonTitle}</span>
          <span>{progressPercentage}%</span>
        </div>
      </div>

      {/* Questions Progress */}
      {totalQuestions > 0 && (
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Questions</span>
            <span className="text-sm text-gray-600">
              {completedQuestions} of {totalQuestions}
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="h-2 bg-blue-500 rounded-full transition-all duration-500"
              style={{ width: `${questionsProgress}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Statistics */}
      {progress && (
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{progress.attempts}</div>
            <div className="text-xs text-gray-600">Attempts</div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{progressPercentage}%</div>
            <div className="text-xs text-gray-600">Score</div>
          </div>
        </div>
      )}

      {/* Last Activity */}
      {progress?.last_reviewed && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-xs text-gray-600">
            Last reviewed: {new Date(progress.last_reviewed).toLocaleDateString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProgressTracker;