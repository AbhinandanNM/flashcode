import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ApiClient from '../utils/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Leaderboard } from '../components/gamification';

interface LeaderboardEntry {
  id: number;
  username: string;
  email: string;
  xp: number;
  streak: number;
  joined_on: string;
  last_activity: string;
  rank: number;
  xp_gained_this_week?: number;
  lessons_completed?: number;
}

const LeaderboardPage: React.FC = () => {
  const { user } = useAuth();
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeframe, setTimeframe] = useState<'weekly' | 'monthly' | 'all-time'>('weekly');

  useEffect(() => {
    fetchLeaderboard();
  }, [timeframe]);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await ApiClient.get(`/game/leaderboard?timeframe=${timeframe}`);
      if (!response.ok) {
        throw new Error('Failed to fetch leaderboard');
      }

      const data = await response.json();
      
      // Add rank to each entry
      const rankedEntries = data.map((entry: any, index: number) => ({
        ...entry,
        rank: index + 1,
        xp_gained_this_week: entry.xp_gained_this_week || Math.floor(Math.random() * 500), // Mock data
        lessons_completed: entry.lessons_completed || Math.floor(Math.random() * 20), // Mock data
      }));
      
      setEntries(rankedEntries);
    } catch (err) {
      console.error('Error fetching leaderboard:', err);
      setError(err instanceof Error ? err.message : 'Failed to load leaderboard');
      
      // Mock data for development
      const mockEntries: LeaderboardEntry[] = [
        {
          id: 1,
          username: 'CodeMaster',
          email: 'codemaster@example.com',
          xp: 2500,
          streak: 15,
          joined_on: '2024-01-15',
          last_activity: '2024-02-01',
          rank: 1,
          xp_gained_this_week: 450,
          lessons_completed: 18,
        },
        {
          id: 2,
          username: 'PythonPro',
          email: 'pythonpro@example.com',
          xp: 2200,
          streak: 12,
          joined_on: '2024-01-20',
          last_activity: '2024-02-01',
          rank: 2,
          xp_gained_this_week: 380,
          lessons_completed: 15,
        },
        {
          id: 3,
          username: 'AlgoExpert',
          email: 'algoexpert@example.com',
          xp: 1950,
          streak: 8,
          joined_on: '2024-01-25',
          last_activity: '2024-01-31',
          rank: 3,
          xp_gained_this_week: 320,
          lessons_completed: 12,
        },
        {
          id: 4,
          username: 'DevNinja',
          email: 'devninja@example.com',
          xp: 1800,
          streak: 5,
          joined_on: '2024-01-28',
          last_activity: '2024-01-30',
          rank: 4,
          xp_gained_this_week: 280,
          lessons_completed: 10,
        },
        {
          id: 5,
          username: 'CodeCrafter',
          email: 'codecrafter@example.com',
          xp: 1650,
          streak: 3,
          joined_on: '2024-01-30',
          last_activity: '2024-01-31',
          rank: 5,
          xp_gained_this_week: 240,
          lessons_completed: 8,
        },
      ];
      
      // Add current user if not in top 5
      if (user && !mockEntries.find(entry => entry.id === user.id)) {
        mockEntries.push({
          id: user.id,
          username: user.username,
          email: user.email,
          xp: user.xp,
          streak: user.streak,
          joined_on: user.joined_on,
          last_activity: user.last_activity,
          rank: 15,
          xp_gained_this_week: 120,
          lessons_completed: 5,
        });
      }
      
      setEntries(mockEntries);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeframeChange = (newTimeframe: 'weekly' | 'monthly' | 'all-time') => {
    setTimeframe(newTimeframe);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Leaderboard</h1>
        <p className="text-gray-600">
          See how you stack up against other learners. Complete lessons and earn XP to climb the rankings!
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-yellow-600 text-lg">👑</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Current Leader</p>
              <p className="text-lg font-semibold text-gray-900">
                {entries.length > 0 ? entries[0].username : 'Loading...'}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 text-lg">👥</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Learners</p>
              <p className="text-lg font-semibold text-gray-900">{entries.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 text-lg">📊</span>
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Your Rank</p>
              <p className="text-lg font-semibold text-gray-900">
                {user ? (entries.find(e => e.id === user.id)?.rank || 'Unranked') : 'Login to see'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center mb-8">
          <div className="text-red-600 mb-2">
            <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-red-900 mb-2">Error Loading Leaderboard</h3>
          <p className="text-red-700 mb-4">{error}</p>
          <p className="text-sm text-red-600 mb-4">Showing sample data for demonstration.</p>
          <button
            onClick={fetchLeaderboard}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Leaderboard */}
      <Leaderboard
        entries={entries}
        currentUserId={user?.id}
        timeframe={timeframe}
        onTimeframeChange={handleTimeframeChange}
        loading={loading}
        maxEntries={10}
      />

      {/* Tips */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-medium text-blue-900 mb-2">💡 Tips to Climb the Leaderboard</h3>
        <ul className="text-blue-800 space-y-1 text-sm">
          <li>• Complete lessons daily to maintain your streak</li>
          <li>• Focus on harder lessons for more XP rewards</li>
          <li>• Participate in coding challenges and duels</li>
          <li>• Help other learners to earn bonus XP</li>
          <li>• Unlock achievements for extra points</li>
        </ul>
      </div>
    </div>
  );
};

export default LeaderboardPage;