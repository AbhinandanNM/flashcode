import { useCallback, useState } from 'react';
import { useApi } from './useApi';
import { QuestionService, SubmitAnswerRequest, QuestionFilters } from '../services/questionService';
import { useToast } from '../contexts/ToastContext';

// Hook for fetching a specific question
export function useQuestion(questionId: number) {
  return useApi(
    () => QuestionService.getQuestion(questionId),
    {
      immediate: !!questionId,
      showErrorToast: true
    }
  );
}

// Hook for fetching questions with filters
export function useQuestions(filters: QuestionFilters = {}) {
  return useApi(
    () => QuestionService.getQuestions(filters),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for submitting answers with optimistic updates
export function useQuestionSubmission() {
  const [submissionHistory, setSubmissionHistory] = useState<Map<number, any>>(new Map());
  const { showSuccess, showError } = useToast();

  const api = useApi(
    (request: SubmitAnswerRequest) => QuestionService.submitAnswer(request),
    {
      immediate: false,
      showErrorToast: false, // Handle errors manually
      onSuccess: (result) => {
        if (result.isCorrect) {
          showSuccess(
            'Correct!', 
            `Great job! You earned ${result.xpAwarded} XP.`
          );
        } else {
          showError(
            'Incorrect', 
            result.explanation || 'Try again!'
          );
        }
      }
    }
  );

  const submitAnswer = useCallback(async (request: SubmitAnswerRequest) => {
    // Store submission for optimistic UI updates
    setSubmissionHistory(prev => new Map(prev.set(request.questionId, {
      userAnswer: request.userAnswer,
      submittedAt: new Date(),
      pending: true
    })));

    try {
      const result = await api.execute(request);
      
      // Update submission history with result
      setSubmissionHistory(prev => new Map(prev.set(request.questionId, {
        userAnswer: request.userAnswer,
        submittedAt: new Date(),
        isCorrect: result?.isCorrect,
        xpAwarded: result?.xpAwarded,
        explanation: result?.explanation,
        pending: false
      })));

      return result;
    } catch (error) {
      // Remove optimistic update on error
      setSubmissionHistory(prev => {
        const newMap = new Map(prev);
        newMap.delete(request.questionId);
        return newMap;
      });
      throw error;
    }
  }, [api]);

  const getSubmissionStatus = useCallback((questionId: number) => {
    return submissionHistory.get(questionId);
  }, [submissionHistory]);

  return {
    ...api,
    submitAnswer,
    getSubmissionStatus,
    submissionHistory: Array.from(submissionHistory.entries())
  };
}

// Hook for question attempts
export function useQuestionAttempts(questionId: number) {
  return useApi(
    () => QuestionService.getQuestionAttempts(questionId),
    {
      immediate: !!questionId,
      showErrorToast: true
    }
  );
}

// Hook for spaced repetition questions
export function useReviewQuestions() {
  return useApi(
    () => QuestionService.getQuestionsForReview(),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for updating review status
export function useReviewUpdate() {
  const { showSuccess } = useToast();

  return useApi(
    (questionId: number, performance: 'easy' | 'medium' | 'hard') => 
      QuestionService.updateReviewStatus(questionId, performance),
    {
      immediate: false,
      showSuccessToast: true,
      successMessage: 'Review updated successfully!'
    }
  );
}

// Hook for random practice questions
export function useRandomQuestions(count: number = 10, filters: QuestionFilters = {}) {
  return useApi(
    () => QuestionService.getRandomQuestions(count, filters),
    {
      immediate: false,
      showErrorToast: true
    }
  );
}

// Hook for question statistics
export function useQuestionStats() {
  return useApi(
    () => QuestionService.getQuestionStats(),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Combined hook for question practice session
export function useQuestionSession(questions: number[] | QuestionFilters) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [sessionStats, setSessionStats] = useState({
    correct: 0,
    total: 0,
    xpEarned: 0,
    startTime: new Date()
  });

  // Fetch questions based on IDs or filters
  const questionsApi = Array.isArray(questions)
    ? useApi(() => Promise.all(questions.map(id => QuestionService.getQuestion(id))))
    : useRandomQuestions(10, questions);

  const submission = useQuestionSubmission();

  const currentQuestion = questionsApi.data?.[currentIndex];
  const isLastQuestion = currentIndex === (questionsApi.data?.length || 0) - 1;
  const progress = questionsApi.data ? (currentIndex + 1) / questionsApi.data.length : 0;

  const submitCurrentAnswer = useCallback(async (answer: string, timeTaken?: number) => {
    if (!currentQuestion) return null;

    const result = await submission.submitAnswer({
      questionId: currentQuestion.id,
      userAnswer: answer,
      timeTaken
    });

    if (result) {
      setSessionStats(prev => ({
        ...prev,
        correct: prev.correct + (result.isCorrect ? 1 : 0),
        total: prev.total + 1,
        xpEarned: prev.xpEarned + result.xpAwarded
      }));
    }

    return result;
  }, [currentQuestion, submission]);

  const nextQuestion = useCallback(() => {
    if (!isLastQuestion) {
      setCurrentIndex(prev => prev + 1);
    }
  }, [isLastQuestion]);

  const previousQuestion = useCallback(() => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1);
    }
  }, [currentIndex]);

  const resetSession = useCallback(() => {
    setCurrentIndex(0);
    setSessionStats({
      correct: 0,
      total: 0,
      xpEarned: 0,
      startTime: new Date()
    });
    questionsApi.refresh();
  }, [questionsApi]);

  return {
    questions: questionsApi.data,
    loading: questionsApi.loading,
    error: questionsApi.error,
    currentQuestion,
    currentIndex,
    isLastQuestion,
    progress,
    sessionStats,
    submitCurrentAnswer,
    nextQuestion,
    previousQuestion,
    resetSession,
    submissionLoading: submission.loading
  };
}