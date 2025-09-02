import React, { useState } from 'react';

interface DuelHistoryEntry {
  id: string;
  opponent: string;
  result: 'win' | 'lose' | 'draw';
  xpGained: number;
  completedAt: string;
  question: string;
  language: 'python' | 'cpp';
  difficulty: 'easy' | 'medium' | 'hard';
  duration: number; // in seconds
  myScore: number;
  opponentScore: number;
}

interface DuelHistoryProps {
  duels: DuelHistoryEntry[];
  loading?: boolean;
}

const DuelHistory: React.FC<DuelHistoryProps> = ({ duels, loading = false }) => {
  const [filter, setFilter] = useState<'all' | 'win' | 'lose' | 'draw'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'xp' | 'duration'>('date');

  const filteredDuels = duels.filter(duel => {
    if (filter === 'all') return true;
    return duel.result === filter;
  });

  const sortedDuels = [...filteredDuels].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime();
      case 'xp':
        return b.xpGained - a.xpGained;
      case 'duration':
        return a.duration - b.duration;
      default:
        return 0;
    }
  });

  const getResultIcon = (result: string) => {
    switch (result) {
      case 'win': return '🏆';
      case 'lose': return '😔';
      case 'draw': return '🤝';
      default: return '❓';
    }
  };

  const getResultColor = (result: string) => {
    switch (result) {
      case 'win': return 'text-green-600 bg-green-50 border-green-200';
      case 'lose': return 'text-red-600 bg-red-50 border-red-200';
      case 'draw': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const calculateWinRate = () => {
    if (duels.length === 0) return 0;
    const wins = duels.filter(duel => duel.result === 'win').length;
    return Math.round((wins / duels.length) * 100);
  };

  const getTotalXP = () => {
    return duels.reduce((total, duel) => total + duel.xpGained, 0);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/3"></div>
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gray-200 rounded-full"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </div>
              <div className="h-8 w-16 bg-gray-200 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Duel History</h2>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span>Win Rate: <span className="font-semibold text-green-600">{calculateWinRate()}%</span></span>
            <span>Total XP: <span className="font-semibold text-blue-600">{getTotalXP()}</span></span>
          </div>
        </div>

        {/* Filters */}
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            {(['all', 'win', 'lose', 'draw'] as const).map((filterOption) => (
              <button
                key={filterOption}
                onClick={() => setFilter(filterOption)}
                className={`px-3 py-1 text-xs font-medium rounded-full transition-colors duration-200 ${
                  filter === filterOption
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {filterOption === 'all' ? 'All' : filterOption.charAt(0).toUpperCase() + filterOption.slice(1)}
              </button>
            ))}
          </div>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'xp' | 'duration')}
            className="text-xs border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="date">Sort by Date</option>
            <option value="xp">Sort by XP</option>
            <option value="duration">Sort by Duration</option>
          </select>
        </div>
      </div>

      {/* Duel List */}
      <div className="p-4">
        {sortedDuels.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <div className="text-4xl mb-2">⚔️</div>
            <p>No duels found.</p>
            <p className="text-sm mt-1">
              {filter === 'all' ? 'Start your first duel!' : `No ${filter} duels yet.`}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {sortedDuels.map((duel) => (
              <div key={duel.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200">
                <div className="flex items-center justify-between">
                  {/* Left side - Duel info */}
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-full border-2 flex items-center justify-center ${getResultColor(duel.result)}`}>
                      <span className="text-xl">{getResultIcon(duel.result)}</span>
                    </div>
                    
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-gray-900">vs {duel.opponent}</span>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${getDifficultyColor(duel.difficulty)}`}>
                          {duel.difficulty}
                        </span>
                        <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                          duel.language === 'python' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'
                        }`}>
                          {duel.language === 'python' ? '🐍' : '⚡'} {duel.language.toUpperCase()}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600">
                        {duel.question} • {formatDuration(duel.duration)}
                      </div>
                      
                      <div className="text-xs text-gray-500 mt-1">
                        {new Date(duel.completedAt).toLocaleDateString()} at {new Date(duel.completedAt).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>

                  {/* Right side - Results */}
                  <div className="text-right">
                    <div className={`font-semibold text-lg ${
                      duel.result === 'win' ? 'text-green-600' :
                      duel.result === 'lose' ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {duel.result.toUpperCase()}
                    </div>
                    
                    <div className="text-sm text-gray-600 mb-1">
                      +{duel.xpGained} XP
                    </div>
                    
                    <div className="text-xs text-gray-500">
                      Score: {duel.myScore} - {duel.opponentScore}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Summary Stats */}
      {duels.length > 0 && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="grid grid-cols-4 gap-4 text-center text-sm">
            <div>
              <div className="font-semibold text-gray-900">{duels.length}</div>
              <div className="text-gray-600">Total Duels</div>
            </div>
            <div>
              <div className="font-semibold text-green-600">
                {duels.filter(d => d.result === 'win').length}
              </div>
              <div className="text-gray-600">Wins</div>
            </div>
            <div>
              <div className="font-semibold text-red-600">
                {duels.filter(d => d.result === 'lose').length}
              </div>
              <div className="text-gray-600">Losses</div>
            </div>
            <div>
              <div className="font-semibold text-yellow-600">
                {duels.filter(d => d.result === 'draw').length}
              </div>
              <div className="text-gray-600">Draws</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DuelHistory;