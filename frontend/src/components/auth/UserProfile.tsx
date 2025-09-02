import React from 'react';
import { useAuth } from '../../contexts/AuthContext';

const UserProfile: React.FC = () => {
  const { state } = useAuth();

  if (!state.user) {
    return null;
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatLastActivity = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Active now';
    } else if (diffInHours < 24) {
      return `${diffInHours} hours ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays} days ago`;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-4 mb-6">
        <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
          <span className="text-2xl font-bold text-white">
            {state.user.username.charAt(0).toUpperCase()}
          </span>
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900">{state.user.username}</h2>
          <p className="text-gray-600">{state.user.email}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {/* XP Display */}
        <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-yellow-100 text-sm">Total XP</p>
              <p className="text-2xl font-bold">{state.user.xp.toLocaleString()}</p>
            </div>
            <div className="text-3xl">⭐</div>
          </div>
        </div>

        {/* Streak Display */}
        <div className="bg-gradient-to-r from-orange-400 to-red-500 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-orange-100 text-sm">Current Streak</p>
              <p className="text-2xl font-bold">{state.user.streak} days</p>
            </div>
            <div className="text-3xl">🔥</div>
          </div>
        </div>

        {/* Level Display (calculated from XP) */}
        <div className="bg-gradient-to-r from-blue-400 to-blue-600 rounded-lg p-4 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm">Level</p>
              <p className="text-2xl font-bold">{Math.floor(state.user.xp / 100) + 1}</p>
            </div>
            <div className="text-3xl">🏆</div>
          </div>
        </div>
      </div>

      <div className="border-t pt-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
          <div>
            <span className="font-medium">Joined:</span> {formatDate(state.user.joined_on)}
          </div>
          <div>
            <span className="font-medium">Last Active:</span> {formatLastActivity(state.user.last_activity)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;