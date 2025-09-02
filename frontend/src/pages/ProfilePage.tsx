import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import UserProfile from '../components/auth/UserProfile';
import { XPBar, StreakCounter, AchievementBadges } from '../components/gamification';

const ProfilePage: React.FC = () => {
  const { state } = useAuth();
  const [selectedAchievement, setSelectedAchievement] = useState<any>(null);

  // Mock achievements data
  const mockAchievements = [
    {
      id: 'first-lesson',
      name: 'First Steps',
      description: 'Complete your first lesson',
      icon: '🎯',
      category: 'learning' as const,
      rarity: 'common' as const,
      unlocked: true,
      unlockedAt: '2024-01-15T10:00:00Z',
      xpReward: 50,
    },
    {
      id: 'week-streak',
      name: 'Week Warrior',
      description: 'Maintain a 7-day learning streak',
      icon: '🔥',
      category: 'streak' as const,
      rarity: 'rare' as const,
      unlocked: state.user?.streak >= 7,
      unlockedAt: state.user?.streak >= 7 ? '2024-01-22T10:00:00Z' : undefined,
      progress: state.user?.streak || 0,
      maxProgress: 7,
      xpReward: 200,
    },
    {
      id: 'python-master',
      name: 'Python Master',
      description: 'Complete 10 Python lessons',
      icon: '🐍',
      category: 'learning' as const,
      rarity: 'epic' as const,
      unlocked: false,
      progress: 3,
      maxProgress: 10,
      xpReward: 500,
    },
    {
      id: 'code-ninja',
      name: 'Code Ninja',
      description: 'Solve 50 coding challenges',
      icon: '🥷',
      category: 'learning' as const,
      rarity: 'legendary' as const,
      unlocked: false,
      progress: 12,
      maxProgress: 50,
      xpReward: 1000,
    },
    {
      id: 'social-butterfly',
      name: 'Social Butterfly',
      description: 'Help 5 other learners',
      icon: '🦋',
      category: 'social' as const,
      rarity: 'rare' as const,
      unlocked: false,
      progress: 1,
      maxProgress: 5,
      xpReward: 300,
    },
  ];

  const handleAchievementClick = (achievement: any) => {
    setSelectedAchievement(achievement);
  };

  // Calculate level from XP (simple formula)
  const calculateLevel = (xp: number) => {
    return Math.floor(xp / 1000) + 1;
  };

  const calculateLevelXP = (level: number) => {
    return (level - 1) * 1000;
  };

  const calculateNextLevelXP = (level: number) => {
    return level * 1000;
  };

  const currentLevel = state.user ? calculateLevel(state.user.xp) : 1;
  const levelXP = calculateLevelXP(currentLevel);
  const nextLevelXP = calculateNextLevelXP(currentLevel);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Profile</h1>
        <p className="text-gray-600">Track your progress and achievements</p>
      </div>
      
      {/* Gamification Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* XP Progress */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Experience Progress</h3>
          <XPBar
            currentXP={state.user?.xp || 0}
            levelXP={levelXP}
            nextLevelXP={nextLevelXP}
            level={currentLevel}
            animated={true}
            showLevel={true}
            size="lg"
            color="blue"
          />
        </div>

        {/* Streak Counter */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex items-center justify-center">
          <StreakCounter
            streak={state.user?.streak || 0}
            lastActivity={state.user?.last_activity}
            animated={true}
            size="md"
            showFireAnimation={true}
          />
        </div>
      </div>
      
      {/* User Profile */}
      <div className="mb-8">
        <UserProfile />
      </div>
      
      {/* Achievements */}
      <div className="mb-8">
        <AchievementBadges
          achievements={mockAchievements}
          showLocked={true}
          layout="grid"
          size="md"
          onAchievementClick={handleAchievementClick}
        />
      </div>

      {/* Additional Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Learning Stats</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Lessons Completed</span>
              <span className="font-semibold">12</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Questions Answered</span>
              <span className="font-semibold">156</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Accuracy Rate</span>
              <span className="font-semibold text-green-600">87%</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-3 text-sm">
            <div className="flex items-center space-x-2">
              <span className="text-green-500">✓</span>
              <span className="text-gray-600">Completed Python Loops</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-blue-500">📚</span>
              <span className="text-gray-600">Started Variables lesson</span>
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-yellow-500">⭐</span>
              <span className="text-gray-600">Earned 50 XP</span>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Goals</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Weekly XP Goal</span>
                <span className="font-semibold">320/500</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{ width: '64%' }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-600">Monthly Lessons</span>
                <span className="font-semibold">8/15</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{ width: '53%' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;