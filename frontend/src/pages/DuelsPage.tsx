import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import DuelMatchmaking from '../components/duels/DuelMatchmaking';
import DuelArena from '../components/duels/DuelArena';
import DuelResults from '../components/duels/DuelResults';

type DuelState = 'menu' | 'matchmaking' | 'arena' | 'results';

interface DuelData {
  id: string;
  opponent: any;
  question: any;
  timeLimit: number;
  startTime?: number;
}

interface DuelResultData {
  result: 'win' | 'lose' | 'draw';
  xpGained: number;
  myStats: {
    submittedAt?: string;
    isCorrect?: boolean;
    executionTime?: number;
  };
}

const DuelsPage: React.FC = () => {
  const { state } = useAuth();
  const [duelState, setDuelState] = useState<DuelState>('menu');
  const [currentDuel, setCurrentDuel] = useState<DuelData | null>(null);
  const [duelResult, setDuelResult] = useState<DuelResultData | null>(null);
  const [loading, setLoading] = useState(false);
  const [recentDuels, setRecentDuels] = useState<any[]>([]);

  useEffect(() => {
    fetchRecentDuels();
  }, []);

  const fetchRecentDuels = async () => {
    try {
      // Mock recent duels data
      const mockDuels = [
        {
          id: 'duel_001',
          opponent: 'CodeMaster',
          result: 'win',
          xpGained: 150,
          completedAt: '2024-02-01T10:30:00Z',
          question: 'Array Maximum',
        },
        {
          id: 'duel_002',
          opponent: 'PythonPro',
          result: 'lose',
          xpGained: 50,
          completedAt: '2024-01-31T15:45:00Z',
          question: 'String Reversal',
        },
        {
          id: 'duel_003',
          opponent: 'AlgoExpert',
          result: 'draw',
          xpGained: 75,
          completedAt: '2024-01-30T09:15:00Z',
          question: 'Binary Search',
        },
      ];
      setRecentDuels(mockDuels);
    } catch (error) {
      console.error('Error fetching recent duels:', error);
    }
  };

  const handleMatchFound = (duelId: string, opponent: any, question: any) => {
    setCurrentDuel({
      id: duelId,
      opponent,
      question,
      timeLimit: 300, // 5 minutes
      startTime: Date.now(),
    });
    setDuelState('arena');
  };

  const handleDuelSubmit = async (code: string) => {
    if (!currentDuel) return;

    setLoading(true);
    
    try {
      // Simulate duel evaluation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Mock result calculation
      const isCorrect = Math.random() > 0.3; // 70% chance of correct solution
      const opponentCorrect = Math.random() > 0.4; // 60% chance opponent is correct
      const myTime = Math.random() * 200 + 50; // 50-250ms execution time
      const opponentTime = Math.random() * 200 + 50;
      
      let result: 'win' | 'lose' | 'draw';
      let xpGained = 25; // Base participation XP
      
      if (isCorrect && !opponentCorrect) {
        result = 'win';
        xpGained = currentDuel.question.xp_reward + 50; // Bonus for winning
      } else if (!isCorrect && opponentCorrect) {
        result = 'lose';
        xpGained = 25;
      } else if (isCorrect && opponentCorrect) {
        // Both correct, check timing
        if (myTime < opponentTime) {
          result = 'win';
          xpGained = currentDuel.question.xp_reward + 25;
        } else if (myTime > opponentTime) {
          result = 'lose';
          xpGained = currentDuel.question.xp_reward;
        } else {
          result = 'draw';
          xpGained = currentDuel.question.xp_reward;
        }
      } else {
        // Both incorrect
        result = 'draw';
        xpGained = 25;
      }

      setDuelResult({
        result,
        xpGained,
        myStats: {
          submittedAt: new Date().toISOString(),
          isCorrect,
          executionTime: myTime,
        },
      });

      // Update opponent stats
      setCurrentDuel(prev => prev ? {
        ...prev,
        opponent: {
          ...prev.opponent,
          submittedAt: new Date(Date.now() - Math.random() * 10000).toISOString(),
          isCorrect: opponentCorrect,
          executionTime: opponentTime,
        }
      } : null);

      setDuelState('results');
    } catch (error) {
      console.error('Error evaluating duel:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayAgain = () => {
    setCurrentDuel(null);
    setDuelResult(null);
    setDuelState('matchmaking');
  };

  const handleBackToMenu = () => {
    setCurrentDuel(null);
    setDuelResult(null);
    setDuelState('menu');
    fetchRecentDuels(); // Refresh recent duels
  };

  const handleCancelMatchmaking = () => {
    setDuelState('menu');
  };

  const renderDuelState = () => {
    switch (duelState) {
      case 'matchmaking':
        return (
          <DuelMatchmaking
            onMatchFound={handleMatchFound}
            onCancel={handleCancelMatchmaking}
          />
        );

      case 'arena':
        if (!currentDuel) return null;
        return (
          <DuelArena
            duelId={currentDuel.id}
            question={currentDuel.question}
            opponent={currentDuel.opponent}
            timeLimit={currentDuel.timeLimit}
            onSubmit={handleDuelSubmit}
            onComplete={(result) => console.log('Duel completed:', result)}
            isActive={true}
          />
        );

      case 'results':
        if (!currentDuel || !duelResult) return null;
        return (
          <DuelResults
            duelId={currentDuel.id}
            result={duelResult.result}
            opponent={currentDuel.opponent}
            myStats={duelResult.myStats}
            question={currentDuel.question}
            xpGained={duelResult.xpGained}
            onPlayAgain={handlePlayAgain}
            onBackToMenu={handleBackToMenu}
          />
        );

      default:
        return (
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">Code Duels</h1>
              <p className="text-xl text-gray-600">
                Challenge other programmers to fast-paced coding battles!
              </p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl mb-2">🏆</div>
                <div className="text-2xl font-bold text-green-600">12</div>
                <div className="text-sm text-gray-600">Wins</div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl mb-2">😔</div>
                <div className="text-2xl font-bold text-red-600">4</div>
                <div className="text-sm text-gray-600">Losses</div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl mb-2">🤝</div>
                <div className="text-2xl font-bold text-yellow-600">2</div>
                <div className="text-sm text-gray-600">Draws</div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
                <div className="text-3xl mb-2">📊</div>
                <div className="text-2xl font-bold text-blue-600">75%</div>
                <div className="text-sm text-gray-600">Win Rate</div>
              </div>
            </div>

            {/* Main Action */}
            <div className="text-center mb-8">
              <button
                onClick={() => setDuelState('matchmaking')}
                className="bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white font-bold py-4 px-8 rounded-xl text-xl transition-all duration-200 transform hover:scale-105 shadow-lg"
              >
                <span className="mr-2">⚔️</span>
                Start New Duel
              </button>
            </div>

            {/* Recent Duels */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="border-b border-gray-200 p-4">
                <h2 className="text-lg font-semibold text-gray-900">Recent Duels</h2>
              </div>
              <div className="p-4">
                {recentDuels.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <div className="text-4xl mb-2">⚔️</div>
                    <p>No duels yet. Start your first duel to see your history!</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {recentDuels.map((duel, index) => (
                      <div key={duel.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <div className={`text-2xl ${
                            duel.result === 'win' ? '🏆' :
                            duel.result === 'lose' ? '😔' : '🤝'
                          }`}>
                            {duel.result === 'win' ? '🏆' :
                             duel.result === 'lose' ? '😔' : '🤝'}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">
                              vs {duel.opponent}
                            </div>
                            <div className="text-sm text-gray-600">
                              {duel.question} • {new Date(duel.completedAt).toLocaleDateString()}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`font-semibold ${
                            duel.result === 'win' ? 'text-green-600' :
                            duel.result === 'lose' ? 'text-red-600' : 'text-yellow-600'
                          }`}>
                            {duel.result.toUpperCase()}
                          </div>
                          <div className="text-sm text-gray-600">
                            +{duel.xpGained} XP
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* How It Works */}
            <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-4">How Code Duels Work</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
                <div className="text-center">
                  <div className="text-2xl mb-2">🎯</div>
                  <div className="font-medium mb-1">1. Get Matched</div>
                  <div>Find an opponent with similar skill level</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-2">⏱️</div>
                  <div className="font-medium mb-1">2. Code Fast</div>
                  <div>Solve the same challenge within the time limit</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl mb-2">🏆</div>
                  <div className="font-medium mb-1">3. Win & Earn</div>
                  <div>Get bonus XP for correct and fast solutions</div>
                </div>
              </div>
            </div>
          </div>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {renderDuelState()}
      </div>
    </div>
  );
};

export default DuelsPage;