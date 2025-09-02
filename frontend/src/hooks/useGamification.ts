import { useCallback, useState } from 'react';
import { useApi } from './useApi';
import { GamificationService, DuelRequest } from '../services/gamificationService';
import { useToast } from '../contexts/ToastContext';

// Hook for user statistics
export function useUserStats() {
  return useApi(
    () => GamificationService.getUserStats(),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for leaderboard
export function useLeaderboard(
  timeframe: 'daily' | 'weekly' | 'monthly' | 'all-time' = 'weekly',
  limit: number = 50
) {
  return useApi(
    () => GamificationService.getLeaderboard(timeframe, limit),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for user rank
export function useUserRank(
  timeframe: 'daily' | 'weekly' | 'monthly' | 'all-time' = 'weekly'
) {
  return useApi(
    () => GamificationService.getUserRank(timeframe),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Hook for achievements
export function useAchievements() {
  const userAchievements = useApi(
    () => GamificationService.getUserAchievements(),
    {
      immediate: true,
      showErrorToast: true
    }
  );

  const allAchievements = useApi(
    () => GamificationService.getAllAchievements(),
    {
      immediate: true,
      showErrorToast: true
    }
  );

  return {
    userAchievements: userAchievements.data,
    allAchievements: allAchievements.data,
    loading: userAchievements.loading || allAchievements.loading,
    error: userAchievements.error || allAchievements.error,
    refresh: () => {
      userAchievements.refresh();
      allAchievements.refresh();
    }
  };
}

// Hook for streak management
export function useStreak() {
  const { showSuccess } = useToast();

  return useApi(
    () => GamificationService.updateStreak(),
    {
      immediate: false,
      showErrorToast: true,
      onSuccess: (result) => {
        showSuccess(
          'Streak Updated!', 
          `Current streak: ${result.streak} days. You earned ${result.xpAwarded} XP!`
        );
      }
    }
  );
}

// Hook for XP management
export function useXPManagement() {
  const { showSuccess } = useToast();
  const [xpHistory, setXpHistory] = useState<any[]>([]);

  const awardXP = useApi(
    (activity: string, amount: number, metadata?: any) => 
      GamificationService.awardXP(activity, amount, metadata),
    {
      immediate: false,
      showErrorToast: true,
      onSuccess: (result) => {
        if (result.levelUp) {
          showSuccess(
            'Level Up!', 
            `Congratulations! You reached level ${result.newLevel}!`
          );
        }
        
        // Add to local history for immediate UI updates
        setXpHistory(prev => [{
          activity,
          xpAwarded: amount,
          timestamp: new Date().toISOString(),
          metadata
        }, ...prev]);
      }
    }
  );

  const xpHistoryApi = useApi(
    (limit: number = 50) => GamificationService.getXPHistory(limit),
    {
      immediate: true,
      showErrorToast: true,
      onSuccess: (data) => {
        setXpHistory(data);
      }
    }
  );

  return {
    awardXP: awardXP.execute,
    xpHistory,
    loading: awardXP.loading || xpHistoryApi.loading,
    error: awardXP.error || xpHistoryApi.error,
    refreshHistory: xpHistoryApi.refresh
  };
}

// Hook for duel management
export function useDuels() {
  const [activeDuel, setActiveDuel] = useState<any>(null);
  const { showSuccess, showInfo } = useToast();

  const createDuel = useApi(
    (request: DuelRequest) => GamificationService.createDuel(request),
    {
      immediate: false,
      showErrorToast: true,
      onSuccess: (duel) => {
        setActiveDuel(duel);
        showSuccess('Duel Created!', 'Waiting for an opponent...');
      }
    }
  );

  const acceptDuel = useApi(
    (duelId: number) => GamificationService.acceptDuel(duelId),
    {
      immediate: false,
      showErrorToast: true,
      onSuccess: (duel) => {
        setActiveDuel(duel);
        showSuccess('Duel Accepted!', 'Let the battle begin!');
      }
    }
  );

  const declineDuel = useApi(
    (duelId: number) => GamificationService.declineDuel(duelId),
    {
      immediate: false,
      showErrorToast: true,
      onSuccess: () => {
        showInfo('Duel Declined', 'You declined the duel challenge.');
      }
    }
  );

  const submitDuelAnswer = useApi(
    (duelId: number, questionId: number, answer: string, timeTaken: number) =>
      GamificationService.submitDuelAnswer(duelId, questionId, answer, timeTaken),
    {
      immediate: false,
      showErrorToast: true
    }
  );

  const completeDuel = useApi(
    (duelId: number) => GamificationService.completeDuel(duelId),
    {
      immediate: false,
      showErrorToast: true,
      onSuccess: (result) => {
        setActiveDuel(null);
        if (result.isWinner) {
          showSuccess(
            'Victory!', 
            `You won the duel and earned ${result.xpAwarded} XP!`
          );
        } else {
          showInfo('Duel Complete', 'Good effort! Better luck next time.');
        }
      }
    }
  );

  const duelHistory = useApi(
    (limit: number = 20) => GamificationService.getDuelHistory(limit),
    {
      immediate: true,
      showErrorToast: true
    }
  );

  const pendingDuels = useApi(
    () => GamificationService.getPendingDuels(),
    {
      immediate: true,
      showErrorToast: true
    }
  );

  return {
    // Active duel state
    activeDuel,
    setActiveDuel,
    
    // Duel actions
    createDuel: createDuel.execute,
    acceptDuel: acceptDuel.execute,
    declineDuel: declineDuel.execute,
    submitAnswer: submitDuelAnswer.execute,
    completeDuel: completeDuel.execute,
    
    // Duel data
    duelHistory: duelHistory.data,
    pendingDuels: pendingDuels.data,
    
    // Loading states
    creating: createDuel.loading,
    accepting: acceptDuel.loading,
    declining: declineDuel.loading,
    submitting: submitDuelAnswer.loading,
    completing: completeDuel.loading,
    
    // Refresh functions
    refreshHistory: duelHistory.refresh,
    refreshPending: pendingDuels.refresh,
    
    // Errors
    error: createDuel.error || acceptDuel.error || declineDuel.error || 
           submitDuelAnswer.error || completeDuel.error
  };
}

// Hook for level information
export function useLevelInfo(level?: number) {
  return useApi(
    () => GamificationService.getLevelInfo(level),
    {
      immediate: true,
      showErrorToast: true
    }
  );
}

// Combined hook for gamification dashboard
export function useGamificationDashboard() {
  const stats = useUserStats();
  const rank = useUserRank();
  const achievements = useAchievements();
  const xpManagement = useXPManagement();
  const duels = useDuels();

  const loading = stats.loading || rank.loading || achievements.loading;
  const error = stats.error || rank.error || achievements.error;

  const refresh = useCallback(() => {
    stats.refresh();
    rank.refresh();
    achievements.refresh();
    xpManagement.refreshHistory();
    duels.refreshHistory();
    duels.refreshPending();
  }, [stats, rank, achievements, xpManagement, duels]);

  return {
    stats: stats.data,
    rank: rank.data,
    userAchievements: achievements.userAchievements,
    allAchievements: achievements.allAchievements,
    xpHistory: xpManagement.xpHistory,
    duelHistory: duels.duelHistory,
    pendingDuels: duels.pendingDuels,
    loading,
    error,
    refresh,
    
    // Actions
    awardXP: xpManagement.awardXP,
    createDuel: duels.createDuel,
    acceptDuel: duels.acceptDuel,
    declineDuel: duels.declineDuel
  };
}