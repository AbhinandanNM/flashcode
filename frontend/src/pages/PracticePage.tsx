import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Question } from '../types';
import ApiClient from '../utils/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { QuestionRenderer } from '../components/questions';

const PracticePage: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, string>>({});
  const [feedback, setFeedback] = useState<Record<number, { isCorrect: boolean; explanation?: string }>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (lessonId) {
      fetchQuestions(parseInt(lessonId));
    }
  }, [lessonId]);

  const fetchQuestions = async (id: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await ApiClient.get(`/lessons/${id}/questions`);
      if (!response.ok) {
        throw new Error('Failed to fetch questions');
      }

      const data = await response.json();
      setQuestions(data);
    } catch (err) {
      console.error('Error fetching questions:', err);
      setError(err instanceof Error ? err.message : 'Failed to load questions');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async (answer: string) => {
    const currentQuestion = questions[currentQuestionIndex];
    if (!currentQuestion || isSubmitting) return;

    setIsSubmitting(true);
    
    try {
      // Submit answer to backend
      const response = await ApiClient.post('/questions/submit', {
        question_id: currentQuestion.id,
        user_answer: answer,
      });

      if (response.ok) {
        const result = await response.json();
        
        // Store user answer and feedback
        setUserAnswers(prev => ({
          ...prev,
          [currentQuestion.id]: answer
        }));
        
        setFeedback(prev => ({
          ...prev,
          [currentQuestion.id]: {
            isCorrect: result.is_correct,
            explanation: result.explanation || currentQuestion.explanation
          }
        }));
      }
    } catch (err) {
      console.error('Error submitting answer:', err);
      // Still show local feedback even if submission fails
      setUserAnswers(prev => ({
        ...prev,
        [currentQuestion.id]: answer
      }));
      
      setFeedback(prev => ({
        ...prev,
        [currentQuestion.id]: {
          isCorrect: answer.toLowerCase().trim() === currentQuestion.correct_answer.toLowerCase().trim(),
          explanation: currentQuestion.explanation
        }
      }));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAnswerChange = (answer: string) => {
    const currentQuestion = questions[currentQuestionIndex];
    if (!currentQuestion) return;

    setUserAnswers(prev => ({
      ...prev,
      [currentQuestion.id]: answer
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // All questions completed, navigate back to lesson
      navigate(`/lessons/${lessonId}`);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || questions.length === 0) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 mb-2">
            <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-red-900 mb-2">
            {error ? 'Error Loading Questions' : 'No Questions Available'}
          </h3>
          <p className="text-red-700 mb-4">
            {error || 'This lesson does not have any practice questions yet.'}
          </p>
          <button
            onClick={() => navigate(`/lessons/${lessonId}`)}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            Back to Lesson
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  const currentFeedback = feedback[currentQuestion.id];
  const currentAnswer = userAnswers[currentQuestion.id] || '';

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={() => navigate(`/lessons/${lessonId}`)}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors duration-200"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="font-medium">Back to Lesson</span>
          </button>
          
          <div className="text-sm text-gray-600">
            Question {currentQuestionIndex + 1} of {questions.length}
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* Question */}
      <div className="mb-6">
        <QuestionRenderer
          question={currentQuestion}
          userAnswer={currentAnswer}
          onAnswerSubmit={handleAnswerSubmit}
          onAnswerChange={handleAnswerChange}
          showFeedback={!!currentFeedback}
          isCorrect={currentFeedback?.isCorrect}
          explanation={currentFeedback?.explanation}
          disabled={isSubmitting}
        />
      </div>

      {/* Navigation */}
      {currentFeedback && (
        <div className="flex justify-between items-center">
          <button
            onClick={handlePreviousQuestion}
            disabled={currentQuestionIndex === 0}
            className={`flex items-center space-x-1 px-4 py-2 rounded-lg font-medium transition-colors duration-200 ${
              currentQuestionIndex === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-gray-600 hover:bg-gray-700 text-white'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span>Previous</span>
          </button>

          <div className="text-sm text-gray-600">
            {Object.keys(feedback).length} of {questions.length} answered
          </div>

          <button
            onClick={handleNextQuestion}
            className="flex items-center space-x-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors duration-200"
          >
            <span>
              {currentQuestionIndex === questions.length - 1 ? 'Complete' : 'Next'}
            </span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

export default PracticePage;