import React, { useState } from 'react';

interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: 'learning' | 'streak' | 'social' | 'special';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  unlocked: boolean;
  unlockedAt?: string;
  progress?: number;
  maxProgress?: number;
  xpReward?: number;
}

interface AchievementBadgesProps {
  achievements: Achievement[];
  showLocked?: boolean;
  layout?: 'grid' | 'list';
  size?: 'sm' | 'md' | 'lg';
  onAchievementClick?: (achievement: Achievement) => void;
}

const AchievementBadges: React.FC<AchievementBadgesProps> = ({
  achievements,
  showLocked = true,
  layout = 'grid',
  size = 'md',
  onAchievementClick,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [showUnlockedOnly, setShowUnlockedOnly] = useState(false);

  const categories = [
    { id: 'all', name: 'All', icon: '🏆' },
    { id: 'learning', name: 'Learning', icon: '📚' },
    { id: 'streak', name: 'Streaks', icon: '🔥' },
    { id: 'social', name: 'Social', icon: '👥' },
    { id: 'special', name: 'Special', icon: '⭐' },
  ];

  const getRarityColor = (rarity: Achievement['rarity']) => {
    switch (rarity) {
      case 'common':
        return 'from-gray-400 to-gray-600';
      case 'rare':
        return 'from-blue-400 to-blue-600';
      case 'epic':
        return 'from-purple-400 to-purple-600';
      case 'legendary':
        return 'from-yellow-400 to-orange-500';
      default:
        return 'from-gray-400 to-gray-600';
    }
  };

  const getRarityBorder = (rarity: Achievement['rarity']) => {
    switch (rarity) {
      case 'common':
        return 'border-gray-300';
      case 'rare':
        return 'border-blue-300';
      case 'epic':
        return 'border-purple-300';
      case 'legendary':
        return 'border-yellow-300 shadow-yellow-200/50';
      default:
        return 'border-gray-300';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          badge: 'w-16 h-16',
          icon: 'text-2xl',
          grid: 'grid-cols-6 gap-2',
          text: 'text-xs',
        };
      case 'lg':
        return {
          badge: 'w-24 h-24',
          icon: 'text-4xl',
          grid: 'grid-cols-3 gap-4',
          text: 'text-sm',
        };
      default:
        return {
          badge: 'w-20 h-20',
          icon: 'text-3xl',
          grid: 'grid-cols-4 gap-3',
          text: 'text-xs',
        };
    }
  };

  const filteredAchievements = achievements.filter(achievement => {
    if (selectedCategory !== 'all' && achievement.category !== selectedCategory) {
      return false;
    }
    if (showUnlockedOnly && !achievement.unlocked) {
      return false;
    }
    if (!showLocked && !achievement.unlocked) {
      return false;
    }
    return true;
  });

  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const totalCount = achievements.length;
  const sizeClasses = getSizeClasses();

  const renderBadge = (achievement: Achievement) => {
    const isUnlocked = achievement.unlocked;
    const hasProgress = achievement.progress !== undefined && achievement.maxProgress !== undefined;
    const progressPercentage = hasProgress ? (achievement.progress! / achievement.maxProgress!) * 100 : 0;

    return (
      <div
        key={achievement.id}
        className={`relative group cursor-pointer transition-all duration-300 hover:scale-105 ${
          isUnlocked ? 'hover:shadow-lg' : ''
        }`}
        onClick={() => onAchievementClick?.(achievement)}
      >
        {/* Badge container */}
        <div className={`
          ${sizeClasses.badge} rounded-full border-4 ${getRarityBorder(achievement.rarity)}
          flex items-center justify-center relative overflow-hidden
          ${isUnlocked 
            ? `bg-gradient-to-br ${getRarityColor(achievement.rarity)} shadow-lg` 
            : 'bg-gray-200 border-gray-300'
          }
          ${achievement.rarity === 'legendary' && isUnlocked ? 'animate-pulse' : ''}
        `}>
          
          {/* Background pattern for legendary */}
          {achievement.rarity === 'legendary' && isUnlocked && (
            <div className="absolute inset-0 bg-gradient-to-br from-yellow-300/30 to-orange-400/30 animate-pulse"></div>
          )}

          {/* Icon */}
          <span className={`${sizeClasses.icon} ${
            isUnlocked ? 'grayscale-0' : 'grayscale opacity-50'
          } relative z-10`}>
            {achievement.icon}
          </span>

          {/* Lock overlay for locked achievements */}
          {!isUnlocked && (
            <div className="absolute inset-0 bg-gray-500/50 flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
              </svg>
            </div>
          )}

          {/* Progress ring for achievements with progress */}
          {hasProgress && !isUnlocked && (
            <svg className="absolute inset-0 w-full h-full transform -rotate-90">
              <circle
                cx="50%"
                cy="50%"
                r="45%"
                fill="none"
                stroke="rgba(255,255,255,0.3)"
                strokeWidth="2"
              />
              <circle
                cx="50%"
                cy="50%"
                r="45%"
                fill="none"
                stroke="rgba(59,130,246,0.8)"
                strokeWidth="2"
                strokeDasharray={`${progressPercentage * 2.83} 283`}
                className="transition-all duration-500"
              />
            </svg>
          )}

          {/* New achievement glow */}
          {isUnlocked && achievement.unlockedAt && (
            <div className="absolute inset-0 rounded-full bg-yellow-400/30 animate-ping"></div>
          )}
        </div>

        {/* Tooltip */}
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-20">
          <div className="bg-gray-900 text-white text-xs rounded-lg p-3 shadow-lg max-w-48">
            <div className="font-semibold">{achievement.name}</div>
            <div className="text-gray-300 mt-1">{achievement.description}</div>
            
            {hasProgress && !isUnlocked && (
              <div className="mt-2">
                <div className="text-blue-300 text-xs">
                  Progress: {achievement.progress}/{achievement.maxProgress}
                </div>
                <div className="w-full bg-gray-700 rounded-full h-1 mt-1">
                  <div 
                    className="bg-blue-400 h-1 rounded-full transition-all duration-300"
                    style={{ width: `${progressPercentage}%` }}
                  ></div>
                </div>
              </div>
            )}
            
            {achievement.xpReward && (
              <div className="mt-2 text-yellow-300 text-xs">
                +{achievement.xpReward} XP
              </div>
            )}
            
            {isUnlocked && achievement.unlockedAt && (
              <div className="mt-2 text-green-300 text-xs">
                Unlocked {new Date(achievement.unlockedAt).toLocaleDateString()}
              </div>
            )}
            
            <div className={`mt-1 text-xs font-medium ${
              achievement.rarity === 'common' ? 'text-gray-400' :
              achievement.rarity === 'rare' ? 'text-blue-400' :
              achievement.rarity === 'epic' ? 'text-purple-400' :
              'text-yellow-400'
            }`}>
              {achievement.rarity.charAt(0).toUpperCase() + achievement.rarity.slice(1)}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <span className="mr-2">🏅</span>
            Achievements
          </h3>
          <div className="text-sm text-gray-600">
            {unlockedCount} / {totalCount} unlocked
          </div>
        </div>

        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
          <div 
            className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-500"
            style={{ width: `${(unlockedCount / totalCount) * 100}%` }}
          ></div>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            {categories.map(category => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-3 py-1 text-xs font-medium rounded-full transition-colors duration-200 ${
                  selectedCategory === category.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <span className="mr-1">{category.icon}</span>
                {category.name}
              </button>
            ))}
          </div>

          <button
            onClick={() => setShowUnlockedOnly(!showUnlockedOnly)}
            className={`px-3 py-1 text-xs font-medium rounded-full transition-colors duration-200 ${
              showUnlockedOnly
                ? 'bg-green-100 text-green-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {showUnlockedOnly ? 'Show All' : 'Unlocked Only'}
          </button>
        </div>
      </div>

      {/* Achievements */}
      <div className="p-4">
        {filteredAchievements.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🏅</div>
            <p>No achievements found.</p>
            <p className="text-sm mt-1">
              {showUnlockedOnly ? 'Try showing all achievements.' : 'Start learning to unlock achievements!'}
            </p>
          </div>
        ) : (
          <div className={`${sizeClasses.grid}`}>
            {filteredAchievements.map(renderBadge)}
          </div>
        )}
      </div>
    </div>
  );
};

export default AchievementBadges;