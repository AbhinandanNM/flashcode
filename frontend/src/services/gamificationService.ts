import ApiClient from '../utils/api';

export interface UserStats {
  totalXP: number;
  level: number;
  xpToNextLevel: number;
  streak: number;
  longestStreak: number;
  lessonsCompleted: number;
  questionsAnswered: number;
  correctAnswers: number;
  averageScore: number;
  joinedDate: string;
  lastActivity: string;
}

export interface LeaderboardEntry {
  userId: number;
  username: string;
  totalXP: number;
  level: number;
  streak: number;
  rank: number;
  avatar?: string;
}

export interface Achievement {
  id: number;
  name: string;
  description: string;
  icon: string;
  category: 'learning' | 'streak' | 'social' | 'challenge';
  requirement: number;
  xpReward: number;
  unlockedAt?: string;
}

export interface DuelRequest {
  opponentId?: number; // If null, match with random player or bot
  questionIds?: number[]; // If null, system selects questions
  timeLimit?: number; // In seconds, default 300 (5 minutes)
}

export interface Duel {
  id: number;
  challengerId: number;
  opponentId: number;
  status: 'waiting' | 'active' | 'completed' | 'cancelled';
  questions: Question[];
  timeLimit: number;
  challengerScore: number;
  opponentScore: number;
  winnerId?: number;
  createdAt: string;
  completedAt?: string;
}

export interface DuelResult {
  duel: Duel;
  userScore: number;
  opponentScore: number;
  isWinner: boolean;
  xpAwarded: number;
  newRank?: number;
}

export class GamificationService {
  // Get user statistics
  static async getUserStats(): Promise<UserStats> {
    return ApiClient.get('/gamification/stats');
  }

  // Get leaderboard
  static async getLeaderboard(
    timeframe: 'daily' | 'weekly' | 'monthly' | 'all-time' = 'weekly',
    limit: number = 50
  ): Promise<LeaderboardEntry[]> {
    return ApiClient.get(`/gamification/leaderboard?timeframe=${timeframe}&limit=${limit}`);
  }

  // Get user's rank
  static async getUserRank(
    timeframe: 'daily' | 'weekly' | 'monthly' | 'all-time' = 'weekly'
  ): Promise<{ rank: number; totalUsers: number }> {
    return ApiClient.get(`/gamification/rank?timeframe=${timeframe}`);
  }

  // Get user achievements
  static async getUserAchievements(): Promise<Achievement[]> {
    return ApiClient.get('/gamification/achievements');
  }

  // Get all available achievements
  static async getAllAchievements(): Promise<Achievement[]> {
    return ApiClient.get('/gamification/achievements/all');
  }

  // Update daily streak
  static async updateStreak(): Promise<{ streak: number; xpAwarded: number }> {
    return ApiClient.post('/gamification/streak');
  }

  // Award XP for completing activities
  static async awardXP(
    activity: 'lesson_complete' | 'question_correct' | 'streak_bonus' | 'duel_win',
    amount: number,
    metadata?: any
  ): Promise<{ newXP: number; levelUp: boolean; newLevel?: number }> {
    return ApiClient.post('/gamification/award-xp', {
      activity,
      amount,
      metadata
    });
  }

  // Create a duel challenge
  static async createDuel(request: DuelRequest): Promise<Duel> {
    return ApiClient.post('/gamification/duels', request);
  }

  // Accept a duel challenge
  static async acceptDuel(duelId: number): Promise<Duel> {
    return ApiClient.post(`/gamification/duels/${duelId}/accept`);
  }

  // Decline a duel challenge
  static async declineDuel(duelId: number): Promise<void> {
    return ApiClient.post(`/gamification/duels/${duelId}/decline`);
  }

  // Submit duel answer
  static async submitDuelAnswer(
    duelId: number,
    questionId: number,
    answer: string,
    timeTaken: number
  ): Promise<{ isCorrect: boolean; score: number }> {
    return ApiClient.post(`/gamification/duels/${duelId}/answer`, {
      questionId,
      answer,
      timeTaken
    });
  }

  // Get duel status
  static async getDuel(duelId: number): Promise<Duel> {
    return ApiClient.get(`/gamification/duels/${duelId}`);
  }

  // Get user's duel history
  static async getDuelHistory(limit: number = 20): Promise<Duel[]> {
    return ApiClient.get(`/gamification/duels/history?limit=${limit}`);
  }

  // Get pending duel invitations
  static async getPendingDuels(): Promise<Duel[]> {
    return ApiClient.get('/gamification/duels/pending');
  }

  // Complete a duel
  static async completeDuel(duelId: number): Promise<DuelResult> {
    return ApiClient.post(`/gamification/duels/${duelId}/complete`);
  }

  // Get XP history
  static async getXPHistory(limit: number = 50): Promise<{
    activity: string;
    xpAwarded: number;
    timestamp: string;
    metadata?: any;
  }[]> {
    return ApiClient.get(`/gamification/xp-history?limit=${limit}`);
  }

  // Get level information
  static async getLevelInfo(level?: number): Promise<{
    level: number;
    xpRequired: number;
    xpToNext: number;
    title: string;
    benefits: string[];
  }> {
    const endpoint = level ? `/gamification/level/${level}` : '/gamification/level';
    return ApiClient.get(endpoint);
  }
}