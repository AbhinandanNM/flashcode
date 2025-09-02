import ApiClient from '../utils/api';
import { Question, QuestionAttempt } from '../types';

export interface SubmitAnswerRequest {
  questionId: number;
  userAnswer: string;
  timeTaken?: number;
}

export interface SubmitAnswerResponse {
  isCorrect: boolean;
  explanation?: string;
  correctAnswer?: string;
  xpAwarded: number;
  attempt: QuestionAttempt;
}

export interface QuestionFilters {
  type?: 'mcq' | 'fill_blank' | 'flashcard' | 'code';
  difficulty?: number;
  lessonId?: number;
}

export class QuestionService {
  // Get a specific question by ID
  static async getQuestion(questionId: number): Promise<Question> {
    return ApiClient.get(`/questions/${questionId}`);
  }

  // Get questions with filters
  static async getQuestions(filters: QuestionFilters = {}): Promise<Question[]> {
    const queryParams = new URLSearchParams();
    
    if (filters.type) queryParams.append('type', filters.type);
    if (filters.difficulty) queryParams.append('difficulty', filters.difficulty.toString());
    if (filters.lessonId) queryParams.append('lesson_id', filters.lessonId.toString());
    
    const query = queryParams.toString();
    const endpoint = `/questions${query ? `?${query}` : ''}`;
    
    return ApiClient.get(endpoint);
  }

  // Submit an answer to a question
  static async submitAnswer(request: SubmitAnswerRequest): Promise<SubmitAnswerResponse> {
    return ApiClient.post('/questions/submit', request);
  }

  // Get user's attempts for a question
  static async getQuestionAttempts(questionId: number): Promise<QuestionAttempt[]> {
    return ApiClient.get(`/questions/${questionId}/attempts`);
  }

  // Get questions due for review (spaced repetition)
  static async getQuestionsForReview(): Promise<Question[]> {
    return ApiClient.get('/questions/review');
  }

  // Update review status for a question
  static async updateReviewStatus(
    questionId: number, 
    performance: 'easy' | 'medium' | 'hard'
  ): Promise<void> {
    return ApiClient.post(`/questions/${questionId}/review`, { performance });
  }

  // Get random questions for practice
  static async getRandomQuestions(
    count: number = 10, 
    filters: QuestionFilters = {}
  ): Promise<Question[]> {
    const queryParams = new URLSearchParams();
    queryParams.append('count', count.toString());
    
    if (filters.type) queryParams.append('type', filters.type);
    if (filters.difficulty) queryParams.append('difficulty', filters.difficulty.toString());
    if (filters.lessonId) queryParams.append('lesson_id', filters.lessonId.toString());
    
    return ApiClient.get(`/questions/random?${queryParams.toString()}`);
  }

  // Get user's question statistics
  static async getQuestionStats(): Promise<{
    totalAttempts: number;
    correctAttempts: number;
    averageScore: number;
    streakCount: number;
    questionTypeStats: Record<string, { attempts: number; correct: number }>;
  }> {
    return ApiClient.get('/questions/stats');
  }
}