import React, { useState, useEffect } from 'react';

interface CelebrationAnimationProps {
  show: boolean;
  type: 'xp' | 'level-up' | 'achievement' | 'streak';
  message?: string;
  xpGained?: number;
  newLevel?: number;
  achievementIcon?: string;
  streakCount?: number;
  onComplete?: () => void;
  duration?: number;
}

const CelebrationAnimation: React.FC<CelebrationAnimationProps> = ({
  show,
  type,
  message,
  xpGained,
  newLevel,
  achievementIcon,
  streakCount,
  onComplete,
  duration = 3000,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [animationPhase, setAnimationPhase] = useState<'enter' | 'celebrate' | 'exit'>('enter');

  useEffect(() => {
    if (show) {
      setIsVisible(true);
      setAnimationPhase('enter');
      
      // Enter phase
      const enterTimer = setTimeout(() => {
        setAnimationPhase('celebrate');
      }, 300);

      // Exit phase
      const exitTimer = setTimeout(() => {
        setAnimationPhase('exit');
      }, duration - 500);

      // Complete
      const completeTimer = setTimeout(() => {
        setIsVisible(false);
        onComplete?.();
      }, duration);

      return () => {
        clearTimeout(enterTimer);
        clearTimeout(exitTimer);
        clearTimeout(completeTimer);
      };
    }
  }, [show, duration, onComplete]);

  if (!isVisible) return null;

  const getAnimationContent = () => {
    switch (type) {
      case 'xp':
        return {
          icon: '⭐',
          title: `+${xpGained} XP`,
          subtitle: message || 'Great job!',
          color: 'from-yellow-400 to-orange-500',
          particles: '⭐✨🌟',
        };
      
      case 'level-up':
        return {
          icon: '🎉',
          title: `Level ${newLevel}!`,
          subtitle: message || 'Level Up!',
          color: 'from-purple-400 to-pink-500',
          particles: '🎉🎊✨',
        };
      
      case 'achievement':
        return {
          icon: achievementIcon || '🏆',
          title: 'Achievement Unlocked!',
          subtitle: message || 'Well done!',
          color: 'from-blue-400 to-purple-500',
          particles: '🏆🎖️⭐',
        };
      
      case 'streak':
        return {
          icon: '🔥',
          title: `${streakCount} Day Streak!`,
          subtitle: message || 'Keep it up!',
          color: 'from-orange-400 to-red-500',
          particles: '🔥💪⚡',
        };
      
      default:
        return {
          icon: '🎉',
          title: 'Congratulations!',
          subtitle: message || 'Great work!',
          color: 'from-blue-400 to-purple-500',
          particles: '🎉✨⭐',
        };
    }
  };

  const content = getAnimationContent();

  // Generate random particles
  const generateParticles = () => {
    const particles = [];
    const particleChars = content.particles.split('');
    
    for (let i = 0; i < 12; i++) {
      const char = particleChars[Math.floor(Math.random() * particleChars.length)];
      const delay = Math.random() * 1000;
      const duration = 1500 + Math.random() * 1000;
      const startX = Math.random() * 100;
      const endX = startX + (Math.random() - 0.5) * 60;
      const rotation = Math.random() * 360;
      
      particles.push(
        <div
          key={i}
          className="absolute text-2xl pointer-events-none"
          style={{
            left: `${startX}%`,
            animationDelay: `${delay}ms`,
            animationDuration: `${duration}ms`,
            transform: `rotate(${rotation}deg)`,
          }}
        >
          <div
            className={`animate-bounce ${
              animationPhase === 'celebrate' ? 'animate-pulse' : ''
            }`}
            style={{
              animation: `
                particleFloat ${duration}ms ease-out ${delay}ms forwards,
                particleFade ${duration}ms ease-out ${delay}ms forwards
              `,
            }}
          >
            {char}
          </div>
        </div>
      );
    }
    
    return particles;
  };

  return (
    <>
      {/* CSS Animations */}
      <style jsx>{`
        @keyframes particleFloat {
          0% {
            transform: translateY(0px) scale(0.5);
            opacity: 1;
          }
          50% {
            transform: translateY(-100px) scale(1);
            opacity: 1;
          }
          100% {
            transform: translateY(-200px) scale(0.5);
            opacity: 0;
          }
        }
        
        @keyframes particleFade {
          0% { opacity: 1; }
          70% { opacity: 1; }
          100% { opacity: 0; }
        }
        
        @keyframes bounceIn {
          0% {
            transform: scale(0.3) translateY(100px);
            opacity: 0;
          }
          50% {
            transform: scale(1.05) translateY(-10px);
            opacity: 1;
          }
          70% {
            transform: scale(0.9) translateY(0px);
          }
          100% {
            transform: scale(1) translateY(0px);
            opacity: 1;
          }
        }
        
        @keyframes slideOut {
          0% {
            transform: scale(1) translateY(0px);
            opacity: 1;
          }
          100% {
            transform: scale(0.8) translateY(-50px);
            opacity: 0;
          }
        }
      `}</style>

      {/* Overlay */}
      <div className={`fixed inset-0 z-50 flex items-center justify-center transition-all duration-300 ${
        animationPhase === 'exit' ? 'opacity-0' : 'opacity-100'
      }`}>
        
        {/* Background */}
        <div className="absolute inset-0 bg-black/20 backdrop-blur-sm"></div>
        
        {/* Particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {animationPhase === 'celebrate' && generateParticles()}
        </div>
        
        {/* Main content */}
        <div className={`relative z-10 text-center transition-all duration-500 ${
          animationPhase === 'enter' ? 'animate-bounce' :
          animationPhase === 'exit' ? 'opacity-0 transform scale-75 -translate-y-8' :
          'animate-pulse'
        }`}>
          
          {/* Main card */}
          <div className={`bg-white rounded-2xl shadow-2xl p-8 max-w-sm mx-auto border-4 border-transparent bg-gradient-to-br ${content.color}`}>
            <div className="bg-white rounded-xl p-6 m-1">
              
              {/* Icon */}
              <div className={`text-6xl mb-4 ${
                animationPhase === 'celebrate' ? 'animate-bounce' : ''
              }`}>
                {content.icon}
              </div>
              
              {/* Title */}
              <h2 className={`text-2xl font-bold mb-2 bg-gradient-to-r ${content.color} bg-clip-text text-transparent`}>
                {content.title}
              </h2>
              
              {/* Subtitle */}
              <p className="text-gray-600 text-lg">
                {content.subtitle}
              </p>
              
              {/* Additional info for level up */}
              {type === 'level-up' && xpGained && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600">
                    +{xpGained} XP earned
                  </p>
                </div>
              )}
              
              {/* Progress indicator */}
              <div className="mt-6">
                <div className="w-full bg-gray-200 rounded-full h-1">
                  <div 
                    className={`h-1 rounded-full bg-gradient-to-r ${content.color} transition-all duration-2000 ${
                      animationPhase === 'celebrate' ? 'w-full' : 'w-0'
                    }`}
                  ></div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Skip button */}
          <button
            onClick={onComplete}
            className="mt-4 text-white/80 hover:text-white text-sm transition-colors duration-200"
          >
            Click to continue
          </button>
        </div>
      </div>
    </>
  );
};

export default CelebrationAnimation;