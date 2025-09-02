import { useCallback, useMemo } from 'react';
import { useApi } from './useApi';
import { LessonService, LessonFilters, LessonProgress } from '../services/lessonService';
import { Lesson, Progress } from '../types';

// Hook for fetching all lessons
export function useLessons(filters: LessonFilters = {}) {
  return useApi(
    () => LessonService.getLessons(filters),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for fetching a specific lesson
export function useLesson(lessonId: number) {
  return useApi(
    () => LessonService.getLesson(lessonId),
    {
      immediate: !!lessonId,
      showErrorToast: true
    }
  );
}

// Hook for fetching lesson questions
export function useLessonQuestions(lessonId: number) {
  return useApi(
    () => LessonService.getLessonQuestions(lessonId),
    {
      immediate: !!lessonId,
      showErrorToast: true
    }
  );
}

// Hook for lesson progress with optimistic updates
export function useLessonProgress(lessonId: number) {
  const api = useApi(
    () => LessonService.getLessonProgress(lessonId),
    {
      immediate: !!lessonId,
      showErrorToast: true
    }
  );

  const updateProgress = useCallback(async (progress: Partial<LessonProgress>) => {
    if (!api.data) return null;

    // Optimistic update
    const optimisticData = { ...api.data, ...progress };
    api.setData(optimisticData);

    try {
      const result = await LessonService.updateLessonProgress(lessonId, progress);
      api.setData(result);
      return result;
    } catch (error) {
      // Revert optimistic update on error
      api.refresh();
      throw error;
    }
  }, [api, lessonId]);

  const startLesson = useCallback(async () => {
    try {
      const result = await LessonService.startLesson(lessonId);
      api.setData(result);
      return result;
    } catch (error) {
      api.refresh();
      throw error;
    }
  }, [api, lessonId]);

  const completeLesson = useCallback(async (score: number) => {
    try {
      const result = await LessonService.completeLesson(lessonId, score);
      api.setData(result);
      return result;
    } catch (error) {
      api.refresh();
      throw error;
    }
  }, [api, lessonId]);

  return {
    ...api,
    updateProgress,
    startLesson,
    completeLesson
  };
}

// Hook for user's overall progress
export function useUserProgress() {
  return useApi(
    () => LessonService.getUserProgress(),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for lessons by language
export function useLessonsByLanguage(language: string) {
  return useApi(
    () => LessonService.getLessonsByLanguage(language),
    {
      immediate: !!language,
      showErrorToast: true
    }
  );
}

// Hook for recommended lessons
export function useRecommendedLessons() {
  return useApi(
    () => LessonService.getRecommendedLessons(),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for lesson search with debouncing
export function useLessonSearch() {
  const api = useApi(
    (query: string) => LessonService.searchLessons(query),
    {
      immediate: false,
      showErrorToast: true
    }
  );

  const search = useCallback((query: string) => {
    if (query.trim().length < 2) {
      api.setData([]);
      return;
    }
    api.execute(query);
  }, [api]);

  return {
    ...api,
    search
  };
}

// Combined hook for lesson detail page
export function useLessonDetail(lessonId: number) {
  const lesson = useLesson(lessonId);
  const questions = useLessonQuestions(lessonId);
  const progress = useLessonProgress(lessonId);

  const loading = lesson.loading || questions.loading || progress.loading;
  const error = lesson.error || questions.error || progress.error;

  const refresh = useCallback(() => {
    lesson.refresh();
    questions.refresh();
    progress.refresh();
  }, [lesson, questions, progress]);

  return {
    lesson: lesson.data,
    questions: questions.data,
    progress: progress.data,
    loading,
    error,
    refresh,
    updateProgress: progress.updateProgress,
    startLesson: progress.startLesson,
    completeLesson: progress.completeLesson
  };
}