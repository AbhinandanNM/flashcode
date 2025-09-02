import React, { useState, useEffect } from 'react';
import { Question } from '../../types';

interface ScheduleItem {
  date: string;
  questions: {
    question: Question;
    nextReview: string;
    interval: number;
    reviewCount: number;
    easeFactor: number;
  }[];
}

interface ReviewScheduleProps {
  onBack: () => void;
}

const ReviewSchedule: React.FC<ReviewScheduleProps> = ({ onBack }) => {
  const [scheduleItems, setScheduleItems] = useState<ScheduleItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month'>('week');

  useEffect(() => {
    fetchSchedule();
  }, [selectedPeriod]);

  const fetchSchedule = async () => {
    try {
      setLoading(true);
      
      // Mock schedule data
      const mockSchedule: ScheduleItem[] = [];
      const today = new Date();
      
      // Generate schedule for the next 30 days
      for (let i = 0; i < (selectedPeriod === 'week' ? 7 : 30); i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        
        // Mock questions for each day (random distribution)
        const questionCount = Math.floor(Math.random() * 8) + (i === 0 ? 3 : 0); // More questions today
        const questions = [];
        
        for (let j = 0; j < questionCount; j++) {
          questions.push({
            question: {
              id: i * 10 + j,
              lesson_id: Math.floor(Math.random() * 5) + 1,
              type: 'flashcard' as const,
              question_text: `Sample question ${i * 10 + j + 1}`,
              correct_answer: `Sample answer ${i * 10 + j + 1}`,
              explanation: 'Sample explanation',
              difficulty: Math.floor(Math.random() * 3) + 1,
              xp_reward: Math.floor(Math.random() * 30) + 20,
            },
            nextReview: date.toISOString(),
            interval: Math.floor(Math.random() * 14) + 1,
            reviewCount: Math.floor(Math.random() * 10) + 1,
            easeFactor: 1.3 + Math.random() * 1.7,
          });
        }
        
        if (questions.length > 0) {
          mockSchedule.push({
            date: date.toISOString().split('T')[0],
            questions,
          });
        }
      }
      
      setScheduleItems(mockSchedule);
    } catch (error) {
      console.error('Error fetching schedule:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(today.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    } else {
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const getDateColor = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    
    if (date.toDateString() === today.toDateString()) {
      return 'bg-red-100 text-red-800 border-red-200';
    } else if (date < today) {
      return 'bg-gray-100 text-gray-600 border-gray-200';
    } else {
      return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  const getTotalQuestions = () => {
    return scheduleItems.reduce((total, item) => total + item.questions.length, 0);
  };

  const getAveragePerDay = () => {
    if (scheduleItems.length === 0) return 0;
    return Math.round(getTotalQuestions() / scheduleItems.length);
  };

  const getPeakDay = () => {
    if (scheduleItems.length === 0) return null;
    const maxItem = scheduleItems.reduce((max, item) => 
      item.questions.length > max.questions.length ? item : max
    );
    return {
      date: formatDate(maxItem.date),
      count: maxItem.questions.length,
    };
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          {[...Array(7)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="h-16 w-20 bg-gray-200 rounded"></div>
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
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <button
              onClick={onBack}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
            </button>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Review Schedule</h2>
              <p className="text-gray-600">Plan your learning sessions</p>
            </div>
          </div>
          
          <div className="flex bg-gray-100 rounded-lg p-1">
            {(['week', 'month'] as const).map((period) => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 text-sm font-medium rounded-md transition-colors duration-200 ${
                  selectedPeriod === period
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {period === 'week' ? 'This Week' : 'This Month'}
              </button>
            ))}
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{getTotalQuestions()}</div>
            <div className="text-sm text-blue-800">Total Reviews</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{getAveragePerDay()}</div>
            <div className="text-sm text-green-800">Avg per Day</div>
          </div>
          <div className="text-center p-4 bg-orange-50 rounded-lg">
            <div className="text-2xl font-bold text-orange-600">
              {getPeakDay()?.count || 0}
            </div>
            <div className="text-sm text-orange-800">
              Peak Day {getPeakDay() ? `(${getPeakDay()!.date})` : ''}
            </div>
          </div>
        </div>
      </div>

      {/* Schedule */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="border-b border-gray-200 p-4">
          <h3 className="text-lg font-semibold text-gray-900">
            {selectedPeriod === 'week' ? 'Next 7 Days' : 'Next 30 Days'}
          </h3>
        </div>
        
        <div className="p-4">
          {scheduleItems.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <div className="text-4xl mb-2">📅</div>
              <p>No reviews scheduled for this period.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {scheduleItems.map((item) => (
                <div key={item.date} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${getDateColor(item.date)}`}>
                      {formatDate(item.date)}
                    </div>
                    <div className="text-sm text-gray-600">
                      {item.questions.length} card{item.questions.length !== 1 ? 's' : ''}
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-3">
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span>Workload</span>
                      <span>{item.questions.length} reviews</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ${
                          item.questions.length <= 5 ? 'bg-green-500' :
                          item.questions.length <= 10 ? 'bg-yellow-500' :
                          'bg-red-500'
                        }`}
                        style={{ width: `${Math.min((item.questions.length / 15) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  {/* Question Preview */}
                  <div className="space-y-2">
                    {item.questions.slice(0, 3).map((q, index) => (
                      <div key={q.question.id} className="flex items-center justify-between text-sm">
                        <span className="text-gray-700 truncate flex-1 mr-4">
                          {q.question.question_text}
                        </span>
                        <div className="flex items-center space-x-2 text-xs text-gray-500">
                          <span>#{q.reviewCount}</span>
                          <span>{q.interval}d</span>
                          <span>+{q.question.xp_reward}</span>
                        </div>
                      </div>
                    ))}
                    
                    {item.questions.length > 3 && (
                      <div className="text-xs text-gray-500 text-center pt-2 border-t border-gray-100">
                        +{item.questions.length - 3} more cards
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">📚 Study Tips</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Review cards consistently every day for best retention</li>
          <li>• Don't skip difficult cards - they need more practice</li>
          <li>• Take breaks between review sessions to avoid fatigue</li>
          <li>• Focus on understanding, not just memorization</li>
        </ul>
      </div>
    </div>
  );
};

export default ReviewSchedule;