// Common types used across the application

export interface User {
  id: number;
  username: string;
  email: string;
  xp: number;
  streak: number;
  joined_on: string;
  last_activity: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface Lesson {
  id: number;
  language: string;
  title: string;
  theory: string;
  difficulty: number;
  xp_reward: number;
  order_index: number;
  is_published: boolean;
  created_at: string;
}

export interface Question {
  id: number;
  lesson_id: number;
  type: 'mcq' | 'fill_blank' | 'flashcard' | 'code';
  question_text: string;
  options?: any;
  correct_answer: string;
  explanation?: string;
  difficulty: number;
  xp_reward: number;
}

export interface Progress {
  id: number;
  user_id: number;
  lesson_id: number;
  status: 'not_started' | 'in_progress' | 'completed';
  score: number;
  attempts: number;
  last_reviewed?: string;
  next_review?: string;
  created_at: string;
  updated_at: string;
}