import React, { useState, useEffect } from 'react';

interface XPBarProps {
  currentXP: number;
  levelXP?: number;
  nextLevelXP?: number;
  level?: number;
  animated?: boolean;
  showLevel?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: 'blue' | 'green' | 'purple' | 'gold';
}

const XPBar: React.FC<XPBarProps> = ({
  currentXP,
  levelXP = 0,
  nextLevelXP = 1000,
  level = 1,
  animated = true,
  showLevel = true,
  size = 'md',
  color = 'blue',
}) => {
  const [displayXP, setDisplayXP] = useState(levelXP);
  const [isAnimating, setIsAnimating] = useState(false);

  // Calculate progress within current level
  const progressXP = currentXP - levelXP;
  const requiredXP = nextLevelXP - levelXP;
  const progressPercentage = Math.min((progressXP / requiredXP) * 100, 100);

  useEffect(() => {
    if (animated && displayXP !== currentXP) {
      setIsAnimating(true);
      const duration = 1500; // 1.5 seconds
      const steps = 60;
      const increment = (currentXP - displayXP) / steps;
      let currentStep = 0;

      const timer = setInterval(() => {
        currentStep++;
        setDisplayXP(prev => {
          const newValue = displayXP + (increment * currentStep);
          return currentStep >= steps ? currentXP : newValue;
        });

        if (currentStep >= steps) {
          clearInterval(timer);
          setIsAnimating(false);
        }
      }, duration / steps);

      return () => clearInterval(timer);
    }
  }, [currentXP, displayXP, animated]);

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return {
          container: 'h-2',
          text: 'text-xs',
          level: 'text-sm',
        };
      case 'lg':
        return {
          container: 'h-6',
          text: 'text-sm',
          level: 'text-lg',
        };
      default:
        return {
          container: 'h-4',
          text: 'text-xs',
          level: 'text-base',
        };
    }
  };

  const getColorClasses = () => {
    switch (color) {
      case 'green':
        return {
          bg: 'bg-green-500',
          glow: 'shadow-green-500/50',
          text: 'text-green-600',
        };
      case 'purple':
        return {
          bg: 'bg-purple-500',
          glow: 'shadow-purple-500/50',
          text: 'text-purple-600',
        };
      case 'gold':
        return {
          bg: 'bg-gradient-to-r from-yellow-400 to-yellow-600',
          glow: 'shadow-yellow-500/50',
          text: 'text-yellow-600',
        };
      default:
        return {
          bg: 'bg-blue-500',
          glow: 'shadow-blue-500/50',
          text: 'text-blue-600',
        };
    }
  };

  const sizeClasses = getSizeClasses();
  const colorClasses = getColorClasses();

  return (
    <div className="w-full">
      {/* Level and XP Display */}
      {showLevel && (
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className={`font-bold ${colorClasses.text} ${sizeClasses.level}`}>
              Level {level}
            </span>
            {isAnimating && (
              <div className="flex items-center space-x-1">
                <svg className="w-4 h-4 text-yellow-500 animate-pulse" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span className="text-xs text-yellow-600 font-medium">+{Math.round(currentXP - levelXP)} XP</span>
              </div>
            )}
          </div>
          <span className={`${sizeClasses.text} text-gray-600`}>
            {Math.round(animated ? displayXP : currentXP).toLocaleString()} / {nextLevelXP.toLocaleString()} XP
          </span>
        </div>
      )}

      {/* Progress Bar */}
      <div className="relative">
        <div className={`w-full bg-gray-200 rounded-full ${sizeClasses.container} overflow-hidden`}>
          <div
            className={`${sizeClasses.container} ${colorClasses.bg} rounded-full transition-all duration-1000 ease-out ${
              animated ? 'shadow-lg ' + colorClasses.glow : ''
            }`}
            style={{ 
              width: `${animated ? (displayXP - levelXP) / requiredXP * 100 : progressPercentage}%`,
              minWidth: progressPercentage > 0 ? '2px' : '0px'
            }}
          >
            {/* Shine effect */}
            {animated && progressPercentage > 10 && (
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
            )}
          </div>
        </div>

        {/* Progress percentage text overlay */}
        {size !== 'sm' && progressPercentage > 15 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-medium text-white drop-shadow-sm">
              {Math.round(progressPercentage)}%
            </span>
          </div>
        )}
      </div>

      {/* XP to next level */}
      {showLevel && (
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-500">
            {Math.max(0, nextLevelXP - currentXP).toLocaleString()} XP to level {level + 1}
          </span>
          {progressPercentage >= 100 && (
            <span className="text-xs font-medium text-green-600 animate-pulse">
              🎉 Level Up Available!
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default XPBar;