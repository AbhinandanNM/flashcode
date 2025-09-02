import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from '../common/LoadingSpinner';

interface MatchmakingProps {
  onMatchFound: (duelId: string, opponent: any, question: any) => void;
  onCancel: () => void;
}

interface QueueStatus {
  position: number;
  estimatedWaitTime: number;
  playersInQueue: number;
}

const DuelMatchmaking: React.FC<MatchmakingProps> = ({ onMatchFound, onCancel }) => {
  const { state } = useAuth();
  const [isSearching, setIsSearching] = useState(false);
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null);
  const [searchTime, setSearchTime] = useState(0);
  const [selectedDifficulty, setSelectedDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [selectedLanguage, setSelectedLanguage] = useState<'python' | 'cpp'>('python');

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (isSearching) {
      timer = setInterval(() => {
        setSearchTime(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [isSearching]);

  // Mock matchmaking process
  useEffect(() => {
    if (isSearching) {
      // Simulate queue updates
      const queueTimer = setInterval(() => {
        setQueueStatus(prev => ({
          position: Math.max(1, (prev?.position || 5) - 1),
          estimatedWaitTime: Math.max(10, (prev?.estimatedWaitTime || 60) - 5),
          playersInQueue: Math.floor(Math.random() * 20) + 10,
        }));
      }, 2000);

      // Simulate finding a match
      const matchTimer = setTimeout(() => {
        const mockOpponent = {
          id: 2,
          username: 'CodeNinja',
          progress: 0,
          isReady: true,
        };

        const mockQuestion = {
          id: 1,
          lesson_id: 1,
          type: 'code' as const,
          question_text: `Write a ${selectedLanguage === 'python' ? 'Python' : 'C++'} function that finds the maximum number in an array.`,
          correct_answer: selectedLanguage === 'python' 
            ? 'def find_max(arr):\n    return max(arr)' 
            : 'int findMax(vector<int>& arr) {\n    return *max_element(arr.begin(), arr.end());\n}',
          explanation: 'Find the largest element in the given array.',
          difficulty: selectedDifficulty === 'easy' ? 1 : selectedDifficulty === 'medium' ? 2 : 3,
          xp_reward: selectedDifficulty === 'easy' ? 50 : selectedDifficulty === 'medium' ? 100 : 150,
        };

        const duelId = `duel_${Date.now()}`;
        onMatchFound(duelId, mockOpponent, mockQuestion);
      }, Math.random() * 10000 + 5000); // 5-15 seconds

      return () => {
        clearInterval(queueTimer);
        clearTimeout(matchTimer);
      };
    }
  }, [isSearching, selectedDifficulty, selectedLanguage, onMatchFound]);

  const handleStartSearch = () => {
    setIsSearching(true);
    setSearchTime(0);
    setQueueStatus({
      position: 5,
      estimatedWaitTime: 60,
      playersInQueue: 15,
    });
  };

  const handleCancelSearch = () => {
    setIsSearching(false);
    setQueueStatus(null);
    setSearchTime(0);
    onCancel();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isSearching) {
    return (
      <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8 text-center max-w-md mx-auto">
        {/* Searching Animation */}
        <div className="mb-6">
          <div className="relative">
            <div className="w-20 h-20 mx-auto mb-4 relative">
              <div className="absolute inset-0 border-4 border-blue-200 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-blue-600 rounded-full border-t-transparent animate-spin"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-2xl">⚔️</span>
              </div>
            </div>
          </div>
          
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Finding Opponent</h2>
          <p className="text-gray-600">Searching for a worthy challenger...</p>
        </div>

        {/* Search Status */}
        <div className="space-y-4 mb-6">
          <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-sm text-gray-600">Search Time</span>
            <span className="font-mono text-lg text-blue-600">{formatTime(searchTime)}</span>
          </div>

          {queueStatus && (
            <>
              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Queue Position</span>
                <span className="font-semibold text-gray-900">#{queueStatus.position}</span>
              </div>

              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Players in Queue</span>
                <span className="font-semibold text-gray-900">{queueStatus.playersInQueue}</span>
              </div>

              <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="text-sm text-gray-600">Est. Wait Time</span>
                <span className="font-semibold text-orange-600">{queueStatus.estimatedWaitTime}s</span>
              </div>
            </>
          )}
        </div>

        {/* Search Preferences */}
        <div className="text-left mb-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">Search Preferences</h3>
          <div className="space-y-1 text-sm text-blue-800">
            <div>Language: <span className="font-medium capitalize">{selectedLanguage}</span></div>
            <div>Difficulty: <span className="font-medium capitalize">{selectedDifficulty}</span></div>
            <div>Skill Level: <span className="font-medium">Matched</span></div>
          </div>
        </div>

        {/* Cancel Button */}
        <button
          onClick={handleCancelSearch}
          className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-3 px-4 rounded-lg transition-colors duration-200"
        >
          Cancel Search
        </button>

        {/* Tips */}
        <div className="mt-6 text-xs text-gray-500">
          💡 Tip: Practice coding challenges while you wait!
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-8 max-w-md mx-auto">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-red-500 to-orange-500 rounded-full flex items-center justify-center">
          <span className="text-3xl">⚔️</span>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Code Duel</h2>
        <p className="text-gray-600">Challenge another programmer to a coding battle!</p>
      </div>

      {/* Preferences */}
      <div className="space-y-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Programming Language
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => setSelectedLanguage('python')}
              className={`p-3 rounded-lg border-2 transition-colors duration-200 ${
                selectedLanguage === 'python'
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-1">🐍</div>
              <div className="text-sm font-medium">Python</div>
            </button>
            <button
              onClick={() => setSelectedLanguage('cpp')}
              className={`p-3 rounded-lg border-2 transition-colors duration-200 ${
                selectedLanguage === 'cpp'
                  ? 'border-orange-500 bg-orange-50 text-orange-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-2xl mb-1">⚡</div>
              <div className="text-sm font-medium">C++</div>
            </button>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Difficulty Level
          </label>
          <div className="grid grid-cols-3 gap-2">
            {(['easy', 'medium', 'hard'] as const).map((difficulty) => (
              <button
                key={difficulty}
                onClick={() => setSelectedDifficulty(difficulty)}
                className={`p-2 rounded-lg border-2 transition-colors duration-200 ${
                  selectedDifficulty === difficulty
                    ? difficulty === 'easy' ? 'border-green-500 bg-green-50 text-green-700' :
                      difficulty === 'medium' ? 'border-yellow-500 bg-yellow-50 text-yellow-700' :
                      'border-red-500 bg-red-50 text-red-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-sm font-medium capitalize">{difficulty}</div>
                <div className="text-xs text-gray-500">
                  {difficulty === 'easy' ? '50 XP' : difficulty === 'medium' ? '100 XP' : '150 XP'}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* User Stats */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="font-medium text-gray-900 mb-2">Your Stats</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Current XP</div>
            <div className="font-semibold">{state.user?.xp || 0}</div>
          </div>
          <div>
            <div className="text-gray-600">Streak</div>
            <div className="font-semibold flex items-center">
              {state.user?.streak || 0}
              {(state.user?.streak || 0) > 0 && <span className="ml-1 text-orange-500">🔥</span>}
            </div>
          </div>
          <div>
            <div className="text-gray-600">Duels Won</div>
            <div className="font-semibold">12</div>
          </div>
          <div>
            <div className="text-gray-600">Win Rate</div>
            <div className="font-semibold text-green-600">75%</div>
          </div>
        </div>
      </div>

      {/* Start Button */}
      <button
        onClick={handleStartSearch}
        className="w-full bg-gradient-to-r from-red-500 to-orange-500 hover:from-red-600 hover:to-orange-600 text-white font-bold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-105"
      >
        Start Duel
      </button>

      {/* Info */}
      <div className="mt-4 text-xs text-gray-500 text-center">
        <p>• Duels are timed coding challenges</p>
        <p>• Winner gets bonus XP and bragging rights</p>
        <p>• Fair matchmaking based on skill level</p>
      </div>
    </div>
  );
};

export default DuelMatchmaking;