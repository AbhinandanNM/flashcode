import ApiClient from '../utils/api';
import { Lesson, Question, Progress } from '../types';
import { apiCache, CacheKeys, CacheTTL } from '../utils/cache';

export interface LessonFilters {
  language?: string;
  difficulty?: number;
  search?: string;
}

export interface LessonProgress {
  lessonId: number;
  status: 'not_started' | 'in_progress' | 'completed';
  score: number;
  attempts: number;
  lastReviewed?: string;
  nextReview?: string;
}

export class LessonService {
  // Get all lessons with optional filters
  static async getLessons(filters: LessonFilters = {}): Promise<Lesson[]> {
    const queryParams = new URLSearchParams();
    
    if (filters.language) queryParams.append('language', filters.language);
    if (filters.difficulty) queryParams.append('difficulty', filters.difficulty.toString());
    if (filters.search) queryParams.append('search', filters.search);
    
    const query = queryParams.toString();
    const endpoint = `/lessons${query ? `?${query}` : ''}`;
    const cacheKey = `${CacheKeys.LESSONS}:${query}`;
    
    return apiCache.get(
      cacheKey,
      () => ApiClient.get(endpoint),
      CacheTTL.LESSONS
    );
  }

  // Get a specific lesson by ID
  static async getLesson(lessonId: number): Promise<Lesson> {
    return apiCache.get(
      CacheKeys.LESSON(lessonId),
      () => ApiClient.get(`/lessons/${lessonId}`),
      CacheTTL.LESSON_CONTENT
    );
  }

  // Get questions for a specific lesson
  static async getLessonQuestions(lessonId: number): Promise<Question[]> {
    return apiCache.get(
      CacheKeys.LESSON_QUESTIONS(lessonId),
      () => ApiClient.get(`/lessons/${lessonId}/questions`),
      CacheTTL.LESSON_CONTENT
    );
  }

  // Get user's progress for a specific lesson
  static async getLessonProgress(lessonId: number): Promise<LessonProgress> {
    return ApiClient.get(`/lessons/${lessonId}/progress`);
  }

  // Update lesson progress
  static async updateLessonProgress(
    lessonId: number, 
    progress: Partial<LessonProgress>
  ): Promise<LessonProgress> {
    return ApiClient.post(`/lessons/${lessonId}/progress`, progress);
  }

  // Start a lesson
  static async startLesson(lessonId: number): Promise<LessonProgress> {
    return ApiClient.post(`/lessons/${lessonId}/start`);
  }

  // Complete a lesson
  static async completeLesson(lessonId: number, score: number): Promise<LessonProgress> {
    return ApiClient.post(`/lessons/${lessonId}/complete`, { score });
  }

  // Get user's overall progress
  static async getUserProgress(): Promise<Progress[]> {
    return ApiClient.get('/progress');
  }

  // Get lessons by language
  static async getLessonsByLanguage(language: string): Promise<Lesson[]> {
    return ApiClient.get(`/lessons?language=${language}`);
  }

  // Get recommended lessons for user
  static async getRecommendedLessons(): Promise<Lesson[]> {
    return ApiClient.get('/lessons/recommended');
  }

  // Search lessons
  static async searchLessons(query: string): Promise<Lesson[]> {
    return ApiClient.get(`/lessons/search?q=${encodeURIComponent(query)}`);
  }
}