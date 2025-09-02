import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Question } from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';
import SpacedRepetitionQueue from '../components/flashcards/SpacedRepetitionQueue';
import FlashcardReview from '../components/flashcards/FlashcardReview';
import ReviewSchedule from '../components/flashcards/ReviewSchedule';
import { CelebrationAnimation } from '../components/gamification';

type FlashcardState = 'queue' | 'review' | 'schedule' | 'results';

interface ReviewResult {
  questionId: number;
  difficulty: 'easy' | 'medium' | 'hard';
  timeSpent: number;
  reviewedAt: string;
}

interface SessionResults {
  totalReviewed: number;
  totalTime: number;
  xpGained: number;
  breakdown: {
    easy: number;
    medium: number;
    hard: number;
  };
}

const FlashcardsPage: React.FC = () => {
  const { state } = useAuth();
  const [flashcardState, setFlashcardState] = useState<FlashcardState>('queue');
  const [reviewQuestions, setReviewQuestions] = useState<Question[]>([]);
  const [sessionResults, setSessionResults] = useState<SessionResults | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCelebration, setShowCelebration] = useState(false);

  const handleStartReview = (questions: Question[]) => {
    if (questions.length === 0) {
      alert('No questions available for review!');
      return;
    }
    
    setReviewQuestions(questions);
    setFlashcardState('review');
  };

  const handleReviewComplete = async (results: ReviewResult[]) => {
    setLoading(true);
    
    try {
      // Calculate session results
      const totalTime = results.reduce((sum, result) => sum + result.timeSpent, 0);
      const breakdown = results.reduce(
        (acc, result) => {
          acc[result.difficulty]++;
          return acc;
        },
        { easy: 0, medium: 0, hard: 0 }
      );
      
      // Calculate XP based on performance
      let xpGained = 0;
      results.forEach(result => {
        const baseXP = 10; // Base XP per card
        const difficultyMultiplier = result.difficulty === 'easy' ? 1.5 : 
                                   result.difficulty === 'medium' ? 1.0 : 0.5;
        xpGained += Math.round(baseXP * difficultyMultiplier);
      });
      
      const sessionData: SessionResults = {
        totalReviewed: results.length,
        totalTime,
        xpGained,
        breakdown,
      };
      
      setSessionResults(sessionData);
      
      // Submit results to backend (mock)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show celebration for good performance
      if (results.length >= 5 || breakdown.easy >= 3) {
        setShowCelebration(true);
      }
      
      setFlashcardState('results');
    } catch (error) {
      console.error('Error processing review results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToQueue = () => {
    setFlashcardState('queue');
    setReviewQuestions([]);
    setSessionResults(null);
  };

  const handleViewSchedule = () => {
    setFlashcardState('schedule');
  };

  const handleBackFromSchedule = () => {
    setFlashcardState('queue');
  };

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`;
    } else {
      return `${remainingSeconds}s`;
    }
  };

  const renderFlashcardState = () => {
    switch (flashcardState) {
      case 'review':
        return (
          <FlashcardReview
            questions={reviewQuestions}
            onComplete={handleReviewComplete}
            onExit={handleBackToQueue}
          />
        );

      case 'schedule':
        return (
          <ReviewSchedule
            onBack={handleBackFromSchedule}
          />
        );

      case 'results':
        if (!sessionResults) return null;
        
        return (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-green-400 to-blue-500 text-white p-6 text-center">
                <div className="text-4xl mb-4">🎉</div>
                <h1 className="text-2xl font-bold mb-2">Review Complete!</h1>
                <p className="text-lg opacity-90">Great job on your study session</p>
              </div>

              {/* Results */}
              <div className="p-6">
                <div className="grid grid-cols-2 gap-6 mb-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{sessionResults.totalReviewed}</div>
                    <div className="text-gray-600">Cards Reviewed</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">+{sessionResults.xpGained}</div>
                    <div className="text-gray-600">XP Gained</div>
                  </div>
                </div>

                <div className="mb-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Performance Breakdown</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-green-600">Easy</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${(sessionResults.breakdown.easy / sessionResults.totalReviewed) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-8">{sessionResults.breakdown.easy}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-yellow-600">Medium</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-yellow-500 h-2 rounded-full"
                            style={{ width: `${(sessionResults.breakdown.medium / sessionResults.totalReviewed) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-8">{sessionResults.breakdown.medium}</span>
                      </div>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-red-600">Hard</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-red-500 h-2 rounded-full"
                            style={{ width: `${(sessionResults.breakdown.hard / sessionResults.totalReviewed) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium w-8">{sessionResults.breakdown.hard}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="text-center text-sm text-gray-600 mb-6">
                  Session time: {formatTime(sessionResults.totalTime)}
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={handleBackToQueue}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
                  >
                    Continue Studying
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Flashcard Review</h1>
              <p className="text-gray-600">
                Use spaced repetition to improve your long-term retention
              </p>
            </div>

            <SpacedRepetitionQueue
              onStartReview={handleStartReview}
              onViewSchedule={handleViewSchedule}
            />

            {/* How It Works */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-4">How Spaced Repetition Works</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
                <div className="text-center">
                  <div className="text-2xl mb-2">🧠</div>
                  <div className="font-medium mb-1">Smart Scheduling</div>
                  <div>Cards you find difficult appear more frequently</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-2">📈</div>
                  <div className="font-medium mb-1">Optimal Intervals</div>
                  <div>Review timing is based on memory science</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-2">🎯</div>
                  <div className="font-medium mb-1">Long-term Retention</div>
                  <div>Build lasting knowledge that sticks</div>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <>
      <CelebrationAnimation
        show={showCelebration}
        type="achievement"
        message="Excellent review session!"
        achievementIcon="🧠"
        onComplete={() => setShowCelebration(false)}
        duration={2500}
      />
      
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="container mx-auto px-4">
          {renderFlashcardState()}
        </div>
      </div>
    </>
  );
};

export default FlashcardsPage;