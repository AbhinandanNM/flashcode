import React, { useState, useEffect } from 'react';
import { Question } from '../../types';

interface QueueItem {
  question: Question;
  nextReview: string;
  interval: number; // days
  easeFactor: number;
  reviewCount: number;
  lastDifficulty?: 'easy' | 'medium' | 'hard';
}

interface SpacedRepetitionQueueProps {
  onStartReview: (questions: Question[]) => void;
  onViewSchedule: () => void;
}

const SpacedRepetitionQueue: React.FC<SpacedRepetitionQueueProps> = ({
  onStartReview,
  onViewSchedule,
}) => {
  const [queueItems, setQueueItems] = useState<QueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<'due' | 'upcoming' | 'all'>('due');

  useEffect(() => {
    fetchQueue();
  }, []);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      
      // Mock spaced repetition queue data
      const mockQueue: QueueItem[] = [
        {
          question: {
            id: 1,
            lesson_id: 1,
            type: 'flashcard',
            question_text: 'What is a Python list?',
            correct_answer: 'A Python list is an ordered collection of items that can be changed (mutable).',
            explanation: 'Lists are one of the most versatile data types in Python.',
            difficulty: 2,
            xp_reward: 25,
          },
          nextReview: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago (due)
          interval: 1,
          easeFactor: 2.5,
          reviewCount: 3,
          lastDifficulty: 'medium',
        },
        {
          question: {
            id: 2,
            lesson_id: 1,
            type: 'flashcard',
            question_text: 'What does the range() function do in Python?',
            correct_answer: 'The range() function generates a sequence of numbers.',
            explanation: 'Commonly used in for loops to iterate a specific number of times.',
            difficulty: 1,
            xp_reward: 20,
          },
          nextReview: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago (due)
          interval: 2,
          easeFactor: 2.8,
          reviewCount: 5,
          lastDifficulty: 'easy',
        },
        {
          question: {
            id: 3,
            lesson_id: 2,
            type: 'flashcard',
            question_text: 'What is the difference between == and is in Python?',
            correct_answer: '== compares values, while is compares object identity.',
            explanation: 'Use == for value comparison and is for identity comparison.',
            difficulty: 3,
            xp_reward: 35,
          },
          nextReview: new Date(Date.now() + 3600000).toISOString(), // 1 hour from now (upcoming)
          interval: 7,
          easeFactor: 2.2,
          reviewCount: 2,
          lastDifficulty: 'hard',
        },
        {
          question: {
            id: 4,
            lesson_id: 2,
            type: 'flashcard',
            question_text: 'What is a Python dictionary?',
            correct_answer: 'A dictionary is an unordered collection of key-value pairs.',
            explanation: 'Dictionaries are mutable and indexed by keys.',
            difficulty: 2,
            xp_reward: 30,
          },
          nextReview: new Date(Date.now() + 86400000).toISOString(), // 1 day from now
          interval: 4,
          easeFactor: 2.6,
          reviewCount: 4,
          lastDifficulty: 'medium',
        },
      ];

      setQueueItems(mockQueue);
    } catch (error) {
      console.error('Error fetching queue:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterItems = () => {
    const now = new Date();
    
    switch (selectedCategory) {
      case 'due':
        return queueItems.filter(item => new Date(item.nextReview) <= now);
      case 'upcoming':
        return queueItems.filter(item => new Date(item.nextReview) > now);
      default:
        return queueItems;
    }
  };

  const getDueItems = () => {
    const now = new Date();
    return queueItems.filter(item => new Date(item.nextReview) <= now);
  };

  const getUpcomingItems = () => {
    const now = new Date();
    return queueItems.filter(item => new Date(item.nextReview) > now);
  };

  const formatTimeUntilReview = (nextReview: string) => {
    const now = new Date();
    const reviewTime = new Date(nextReview);
    const diffMs = reviewTime.getTime() - now.getTime();
    
    if (diffMs <= 0) {
      const overdue = Math.abs(diffMs);
      const hours = Math.floor(overdue / (1000 * 60 * 60));
      const minutes = Math.floor((overdue % (1000 * 60 * 60)) / (1000 * 60));
      
      if (hours > 0) {
        return `${hours}h ${minutes}m overdue`;
      } else {
        return `${minutes}m overdue`;
      }
    }
    
    const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    if (days > 0) {
      return `in ${days}d ${hours}h`;
    } else if (hours > 0) {
      return `in ${hours}h ${minutes}m`;
    } else {
      return `in ${minutes}m`;
    }
  };

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case 'easy': return 'text-green-600 bg-green-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'hard': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getRetentionColor = (easeFactor: number) => {
    if (easeFactor >= 2.5) return 'text-green-600';
    if (easeFactor >= 2.0) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredItems = filterItems();
  const dueCount = getDueItems().length;
  const upcomingCount = getUpcomingItems().length;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          {[...Array(3)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gray-200 rounded"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <span className="text-red-600 text-lg">⏰</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Due Now</p>
              <p className="text-2xl font-bold text-red-600">{dueCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 text-lg">📅</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Upcoming</p>
              <p className="text-2xl font-bold text-blue-600">{upcomingCount}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 text-lg">🧠</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Cards</p>
              <p className="text-2xl font-bold text-green-600">{queueItems.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={() => onStartReview(getDueItems().map(item => item.question))}
          disabled={dueCount === 0}
          className={`flex-1 py-3 px-4 rounded-lg font-medium transition-colors duration-200 ${
            dueCount > 0
              ? 'bg-red-600 hover:bg-red-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Review Due Cards ({dueCount})
        </button>
        
        <button
          onClick={onViewSchedule}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
        >
          View Schedule
        </button>
      </div>

      {/* Filter Tabs */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {([
              { key: 'due', label: 'Due Now', count: dueCount },
              { key: 'upcoming', label: 'Upcoming', count: upcomingCount },
              { key: 'all', label: 'All Cards', count: queueItems.length },
            ] as const).map((tab) => (
              <button
                key={tab.key}
                onClick={() => setSelectedCategory(tab.key)}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  selectedCategory === tab.key
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label} ({tab.count})
              </button>
            ))}
          </nav>
        </div>

        {/* Queue Items */}
        <div className="p-6">
          {filteredItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">🎉</div>
              <p className="text-lg font-medium mb-1">
                {selectedCategory === 'due' ? 'All caught up!' : 'No cards found'}
              </p>
              <p className="text-sm">
                {selectedCategory === 'due' 
                  ? 'Great job! Check back later for more reviews.'
                  : 'Try selecting a different category.'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {filteredItems.map((item) => (
                <div key={item.question.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="font-medium text-gray-900 line-clamp-1">
                          {item.question.question_text}
                        </h3>
                        {item.lastDifficulty && (
                          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(item.lastDifficulty)}`}>
                            {item.lastDifficulty}
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-600">
                        <span>
                          {new Date(item.nextReview) <= new Date() ? '🔴' : '🟡'} 
                          {formatTimeUntilReview(item.nextReview)}
                        </span>
                        <span>Reviews: {item.reviewCount}</span>
                        <span>Interval: {item.interval}d</span>
                        <span className={getRetentionColor(item.easeFactor)}>
                          Retention: {Math.round((item.easeFactor - 1.3) / 1.7 * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">
                        +{item.question.xp_reward} XP
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SpacedRepetitionQueue;