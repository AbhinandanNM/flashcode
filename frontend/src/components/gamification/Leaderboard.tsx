import React, { useState, useEffect } from 'react';
import { User } from '../../types';

interface LeaderboardEntry extends User {
  rank: number;
  xp_gained_this_week?: number;
  lessons_completed?: number;
  streak?: number;
}

interface LeaderboardProps {
  entries: LeaderboardEntry[];
  currentUserId?: number;
  timeframe?: 'weekly' | 'monthly' | 'all-time';
  onTimeframeChange?: (timeframe: 'weekly' | 'monthly' | 'all-time') => void;
  loading?: boolean;
  maxEntries?: number;
}

const Leaderboard: React.FC<LeaderboardProps> = ({
  entries,
  currentUserId,
  timeframe = 'weekly',
  onTimeframeChange,
  loading = false,
  maxEntries = 10,
}) => {
  const [selectedTimeframe, setSelectedTimeframe] = useState(timeframe);

  const handleTimeframeChange = (newTimeframe: 'weekly' | 'monthly' | 'all-time') => {
    setSelectedTimeframe(newTimeframe);
    if (onTimeframeChange) {
      onTimeframeChange(newTimeframe);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `#${rank}`;
    }
  };

  const getRankColor = (rank: number) => {
    switch (rank) {
      case 1:
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 2:
        return 'text-gray-600 bg-gray-50 border-gray-200';
      case 3:
        return 'text-orange-600 bg-orange-50 border-orange-200';
      default:
        return 'text-gray-700 bg-white border-gray-200';
    }
  };

  const getXPDisplay = (entry: LeaderboardEntry) => {
    switch (selectedTimeframe) {
      case 'weekly':
        return entry.xp_gained_this_week || 0;
      case 'monthly':
        return entry.xp_gained_this_week || 0; // Would be xp_gained_this_month in real implementation
      default:
        return entry.xp;
    }
  };

  const displayedEntries = entries.slice(0, maxEntries);
  const currentUserEntry = entries.find(entry => entry.id === currentUserId);
  const currentUserRank = currentUserEntry?.rank;

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center space-x-4">
                <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                </div>
                <div className="h-4 bg-gray-200 rounded w-16"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <span className="mr-2">🏆</span>
            Leaderboard
          </h3>
          
          {/* Timeframe selector */}
          <div className="flex bg-gray-100 rounded-lg p-1">
            {(['weekly', 'monthly', 'all-time'] as const).map((period) => (
              <button
                key={period}
                onClick={() => handleTimeframeChange(period)}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-colors duration-200 ${
                  selectedTimeframe === period
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {period === 'all-time' ? 'All Time' : period.charAt(0).toUpperCase() + period.slice(1)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Leaderboard entries */}
      <div className="p-4">
        {displayedEntries.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">🏆</div>
            <p>No leaderboard data available yet.</p>
            <p className="text-sm mt-1">Complete lessons to appear on the leaderboard!</p>
          </div>
        ) : (
          <div className="space-y-3">
            {displayedEntries.map((entry, index) => (
              <div
                key={entry.id}
                className={`flex items-center p-3 rounded-lg border transition-all duration-200 hover:shadow-md ${
                  entry.id === currentUserId
                    ? 'ring-2 ring-blue-500 bg-blue-50 border-blue-200'
                    : getRankColor(entry.rank)
                }`}
              >
                {/* Rank */}
                <div className="flex-shrink-0 w-12 text-center">
                  <span className={`text-lg font-bold ${
                    entry.rank <= 3 ? 'text-2xl' : 'text-gray-600'
                  }`}>
                    {getRankIcon(entry.rank)}
                  </span>
                </div>

                {/* User info */}
                <div className="flex-1 ml-3">
                  <div className="flex items-center space-x-2">
                    <h4 className={`font-medium ${
                      entry.id === currentUserId ? 'text-blue-900' : 'text-gray-900'
                    }`}>
                      {entry.username}
                      {entry.id === currentUserId && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                          You
                        </span>
                      )}
                    </h4>
                    
                    {/* Streak indicator */}
                    {entry.streak && entry.streak > 0 && (
                      <div className="flex items-center space-x-1">
                        <span className="text-orange-500">🔥</span>
                        <span className="text-xs text-orange-600 font-medium">
                          {entry.streak}
                        </span>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-4 mt-1">
                    <span className="text-sm text-gray-600">
                      {getXPDisplay(entry).toLocaleString()} XP
                      {selectedTimeframe !== 'all-time' && (
                        <span className="text-xs text-gray-500 ml-1">
                          this {selectedTimeframe.replace('-', ' ')}
                        </span>
                      )}
                    </span>
                    
                    {entry.lessons_completed && (
                      <span className="text-xs text-gray-500">
                        {entry.lessons_completed} lessons
                      </span>
                    )}
                  </div>
                </div>

                {/* XP Badge */}
                <div className={`flex-shrink-0 px-3 py-1 rounded-full text-sm font-medium ${
                  entry.rank === 1 ? 'bg-yellow-100 text-yellow-800' :
                  entry.rank === 2 ? 'bg-gray-100 text-gray-800' :
                  entry.rank === 3 ? 'bg-orange-100 text-orange-800' :
                  'bg-blue-100 text-blue-800'
                }`}>
                  {getXPDisplay(entry).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Current user position if not in top entries */}
        {currentUserEntry && currentUserRank && currentUserRank > maxEntries && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="text-center text-sm text-gray-600 mb-2">Your Position</div>
            <div className="flex items-center p-3 rounded-lg border-2 border-blue-200 bg-blue-50">
              <div className="flex-shrink-0 w-12 text-center">
                <span className="text-lg font-bold text-blue-600">#{currentUserRank}</span>
              </div>
              <div className="flex-1 ml-3">
                <h4 className="font-medium text-blue-900">{currentUserEntry.username}</h4>
                <span className="text-sm text-blue-700">
                  {getXPDisplay(currentUserEntry).toLocaleString()} XP
                </span>
              </div>
              <div className="flex-shrink-0 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {getXPDisplay(currentUserEntry).toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="mt-4 pt-4 border-t border-gray-200 text-center">
          <p className="text-xs text-gray-500">
            Rankings update every hour • Complete lessons and earn XP to climb the leaderboard!
          </p>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;