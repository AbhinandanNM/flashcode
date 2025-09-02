import React, { useState, useEffect } from 'react';

interface StreakCounterProps {
  streak: number;
  lastActivity?: string;
  animated?: boolean;
  size?: 'sm' | 'md' | 'lg';
  showFireAnimation?: boolean;
}

const StreakCounter: React.FC<StreakCounterProps> = ({
  streak,
  lastActivity,
  animated = true,
  size = 'md',
  showFireAnimation = true,
}) => {
  const [displayStreak, setDisplayStreak] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (animated && displayStreak !== streak) {
      setIsAnimating(true);
      const duration = 1000;
      const steps = 30;
      const increment = (streak - displayStreak) / steps;
      let currentStep = 0;

      const timer = setInterval(() => {
        currentStep++;
        setDisplayStreak(prev => {
          const newValue = displayStreak + (increment * currentStep);
          return currentStep >= steps ? streak : Math.round(newValue);
        });

        if (currentStep >= steps) {
          clearInterval(timer);
          setIsAnimating(false);
        }
      }, duration / steps);

      return () => clearInterval(timer);
    }
  }, [streak, displayStreak, animated]);

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          container: 'p-3',
          number: 'text-2xl',
          label: 'text-xs',
          fire: 'text-2xl',
        };
      case 'lg':
        return {
          container: 'p-6',
          number: 'text-5xl',
          label: 'text-base',
          fire: 'text-4xl',
        };
      default:
        return {
          container: 'p-4',
          number: 'text-3xl',
          label: 'text-sm',
          fire: 'text-3xl',
        };
    }
  };

  const getStreakLevel = () => {
    if (streak >= 100) return { level: 'legendary', color: 'from-purple-500 to-pink-500', fires: 5 };
    if (streak >= 50) return { level: 'master', color: 'from-orange-500 to-red-500', fires: 4 };
    if (streak >= 30) return { level: 'expert', color: 'from-red-500 to-orange-500', fires: 3 };
    if (streak >= 14) return { level: 'advanced', color: 'from-yellow-500 to-orange-500', fires: 2 };
    if (streak >= 7) return { level: 'intermediate', color: 'from-yellow-400 to-yellow-500', fires: 1 };
    return { level: 'beginner', color: 'from-gray-400 to-gray-500', fires: 0 };
  };

  const isStreakActive = () => {
    if (!lastActivity) return false;
    const lastDate = new Date(lastActivity);
    const today = new Date();
    const diffTime = Math.abs(today.getTime() - lastDate.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 1;
  };

  const sizeClasses = getSizeClasses();
  const streakLevel = getStreakLevel();
  const isActive = isStreakActive();

  const renderFireEmojis = () => {
    if (!showFireAnimation || streak === 0) return null;
    
    const fires = [];
    for (let i = 0; i < streakLevel.fires; i++) {
      fires.push(
        <span
          key={i}
          className={`${sizeClasses.fire} ${
            isAnimating ? 'animate-bounce' : 'animate-pulse'
          }`}
          style={{ animationDelay: `${i * 0.1}s` }}
        >
          🔥
        </span>
      );
    }
    return fires;
  };

  return (
    <div className={`relative bg-white rounded-xl shadow-lg border-2 ${
      isActive ? 'border-orange-300' : 'border-gray-200'
    } ${sizeClasses.container} text-center transition-all duration-300 hover:shadow-xl`}>
      
      {/* Background gradient for high streaks */}
      {streak >= 7 && (
        <div className={`absolute inset-0 bg-gradient-to-br ${streakLevel.color} opacity-10 rounded-xl`}></div>
      )}

      {/* Fire animations */}
      {showFireAnimation && streak > 0 && (
        <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
          {renderFireEmojis()}
        </div>
      )}

      {/* Streak number */}
      <div className="relative z-10">
        <div className={`font-bold ${sizeClasses.number} ${
          streak >= 30 ? 'text-transparent bg-clip-text bg-gradient-to-r ' + streakLevel.color :
          streak >= 7 ? 'text-orange-600' :
          streak > 0 ? 'text-yellow-600' :
          'text-gray-400'
        } ${isAnimating ? 'animate-pulse' : ''}`}>
          {animated ? displayStreak : streak}
        </div>
        
        <div className={`${sizeClasses.label} font-medium ${
          isActive ? 'text-orange-600' : 'text-gray-600'
        }`}>
          Day{streak !== 1 ? 's' : ''} Streak
        </div>

        {/* Streak level badge */}
        {streak >= 7 && (
          <div className={`mt-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
            streak >= 100 ? 'bg-purple-100 text-purple-800' :
            streak >= 50 ? 'bg-red-100 text-red-800' :
            streak >= 30 ? 'bg-orange-100 text-orange-800' :
            streak >= 14 ? 'bg-yellow-100 text-yellow-800' :
            'bg-yellow-50 text-yellow-700'
          }`}>
            {streakLevel.level.charAt(0).toUpperCase() + streakLevel.level.slice(1)}
          </div>
        )}

        {/* Status indicator */}
        <div className="mt-2 flex items-center justify-center space-x-1">
          <div className={`w-2 h-2 rounded-full ${
            isActive ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
          }`}></div>
          <span className={`text-xs ${
            isActive ? 'text-green-600' : 'text-gray-500'
          }`}>
            {isActive ? 'Active' : 'Inactive'}
          </span>
        </div>

        {/* Motivational messages */}
        {streak === 0 && (
          <div className="mt-2 text-xs text-gray-500">
            Start your learning streak today! 🚀
          </div>
        )}
        
        {streak > 0 && streak < 7 && (
          <div className="mt-2 text-xs text-orange-600">
            Keep going! {7 - streak} more day{7 - streak !== 1 ? 's' : ''} to unlock fire! 🔥
          </div>
        )}
        
        {streak >= 7 && streak < 30 && (
          <div className="mt-2 text-xs text-orange-600">
            You're on fire! 🔥 Keep the momentum going!
          </div>
        )}
        
        {streak >= 30 && (
          <div className="mt-2 text-xs text-red-600">
            Incredible dedication! You're a learning machine! 🚀
          </div>
        )}

        {/* Warning for inactive streak */}
        {streak > 0 && !isActive && (
          <div className="mt-2 text-xs text-red-500 animate-pulse">
            ⚠️ Streak at risk! Learn today to keep it alive!
          </div>
        )}
      </div>
    </div>
  );
};

export default StreakCounter;