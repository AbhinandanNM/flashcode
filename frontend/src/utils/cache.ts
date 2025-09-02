// Simple in-memory cache with TTL support
export interface CacheEntry<T> {
  data: T;
  timestamp: number;
  ttl: number;
}

export class Cache {
  private static instance: Cache;
  private cache = new Map<string, CacheEntry<any>>();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  static getInstance(): Cache {
    if (!Cache.instance) {
      Cache.instance = new Cache();
    }
    return Cache.instance;
  }

  set<T>(key: string, data: T, ttl?: number): void {
    const entry: CacheEntry<T> = {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.defaultTTL
    };
    this.cache.set(key, entry);
  }

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if entry has expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return null;
    }

    return entry.data;
  }

  has(key: string): boolean {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return false;
    }

    // Check if entry has expired
    if (Date.now() - entry.timestamp > entry.ttl) {
      this.cache.delete(key);
      return false;
    }

    return true;
  }

  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  // Clean up expired entries
  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        this.cache.delete(key);
      }
    }
  }

  // Get cache statistics
  getStats(): {
    size: number;
    keys: string[];
    expired: number;
  } {
    const now = Date.now();
    let expired = 0;
    
    for (const [key, entry] of this.cache.entries()) {
      if (now - entry.timestamp > entry.ttl) {
        expired++;
      }
    }

    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys()),
      expired
    };
  }
}

// Cache keys for different data types
export const CacheKeys = {
  // Lessons
  LESSONS: 'lessons',
  LESSON: (id: number) => `lesson:${id}`,
  LESSON_QUESTIONS: (id: number) => `lesson:${id}:questions`,
  LESSON_PROGRESS: (id: number) => `lesson:${id}:progress`,
  USER_PROGRESS: 'user:progress',
  RECOMMENDED_LESSONS: 'lessons:recommended',
  
  // Questions
  QUESTION: (id: number) => `question:${id}`,
  QUESTIONS_REVIEW: 'questions:review',
  QUESTION_STATS: 'questions:stats',
  
  // Gamification
  USER_STATS: 'user:stats',
  LEADERBOARD: (timeframe: string) => `leaderboard:${timeframe}`,
  USER_RANK: (timeframe: string) => `user:rank:${timeframe}`,
  ACHIEVEMENTS: 'achievements',
  USER_ACHIEVEMENTS: 'user:achievements',
  XP_HISTORY: 'user:xp-history',
  
  // Duels
  DUEL_HISTORY: 'duels:history',
  PENDING_DUELS: 'duels:pending',
  
  // Code execution
  CODE_TEMPLATES: (language: string, type: string) => `template:${language}:${type}`,
  SUBMISSION_HISTORY: (questionId?: number) => 
    questionId ? `submissions:${questionId}` : 'submissions',
  BEST_SOLUTION: (questionId: number) => `best-solution:${questionId}`
};

// Cache TTL configurations (in milliseconds)
export const CacheTTL = {
  SHORT: 1 * 60 * 1000,      // 1 minute
  MEDIUM: 5 * 60 * 1000,     // 5 minutes
  LONG: 15 * 60 * 1000,      // 15 minutes
  VERY_LONG: 60 * 60 * 1000, // 1 hour
  
  // Specific data types
  LESSONS: 15 * 60 * 1000,        // 15 minutes
  LESSON_CONTENT: 60 * 60 * 1000, // 1 hour
  USER_PROGRESS: 5 * 60 * 1000,   // 5 minutes
  LEADERBOARD: 2 * 60 * 1000,     // 2 minutes
  ACHIEVEMENTS: 30 * 60 * 1000,   // 30 minutes
  CODE_TEMPLATES: 60 * 60 * 1000  // 1 hour
};

// Enhanced API client with caching
export class CachedApiClient {
  private cache = Cache.getInstance();

  async get<T>(
    key: string, 
    fetcher: () => Promise<T>, 
    ttl?: number,
    forceRefresh = false
  ): Promise<T> {
    // Return cached data if available and not forcing refresh
    if (!forceRefresh && this.cache.has(key)) {
      const cached = this.cache.get<T>(key);
      if (cached !== null) {
        return cached;
      }
    }

    // Fetch fresh data
    const data = await fetcher();
    
    // Cache the result
    this.cache.set(key, data, ttl);
    
    return data;
  }

  invalidate(key: string): void {
    this.cache.delete(key);
  }

  invalidatePattern(pattern: string): void {
    const keys = this.cache.getStats().keys;
    const regex = new RegExp(pattern);
    
    keys.forEach(key => {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    });
  }

  clear(): void {
    this.cache.clear();
  }
}

// Global cache instance
export const apiCache = new CachedApiClient();

// Cache invalidation helpers
export const invalidateCache = {
  // Invalidate lesson-related cache
  lessons: () => {
    apiCache.invalidatePattern('^lessons');
    apiCache.invalidatePattern('^lesson:');
  },
  
  // Invalidate user progress cache
  progress: () => {
    apiCache.invalidatePattern('progress');
    apiCache.invalidatePattern('user:progress');
  },
  
  // Invalidate gamification cache
  gamification: () => {
    apiCache.invalidatePattern('^user:stats');
    apiCache.invalidatePattern('^leaderboard:');
    apiCache.invalidatePattern('^user:rank:');
    apiCache.invalidatePattern('achievements');
  },
  
  // Invalidate question cache
  questions: () => {
    apiCache.invalidatePattern('^question');
    apiCache.invalidatePattern('questions:');
  },
  
  // Invalidate all cache
  all: () => {
    apiCache.clear();
  }
};

// Auto cleanup interval (run every 10 minutes)
setInterval(() => {
  Cache.getInstance().cleanup();
}, 10 * 60 * 1000);