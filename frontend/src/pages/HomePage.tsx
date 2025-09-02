import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const HomePage: React.FC = () => {
  const { state } = useAuth();

  return (
    <div className="text-center">
      <div className="max-w-4xl mx-auto">
        {/* Hero Section */}
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Learn Programming with{' '}
            <span className="text-blue-600">CodeCrafts</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Master Python and C++ through gamified lessons, interactive challenges, 
            and competitive duels. Build your coding skills one lesson at a time.
          </p>
          
          {!state.isAuthenticated ? (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors duration-200"
              >
                Start Learning
              </Link>
              <Link
                to="/login"
                className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors duration-200"
              >
                Login
              </Link>
            </div>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/lessons"
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors duration-200"
              >
                Continue Learning
              </Link>
              <Link
                to="/duels"
                className="border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white px-8 py-3 rounded-lg text-lg font-semibold transition-colors duration-200"
              >
                Challenge Others
              </Link>
            </div>
          )}
        </div>

        {/* Features Section */}
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">📚</div>
            <h3 className="text-xl font-semibold mb-2">Interactive Lessons</h3>
            <p className="text-gray-600">
              Learn through bite-sized lessons with immediate practice questions and code challenges.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">🎮</div>
            <h3 className="text-xl font-semibold mb-2">Gamified Learning</h3>
            <p className="text-gray-600">
              Earn XP, maintain streaks, and climb leaderboards while mastering programming concepts.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-4xl mb-4">⚔️</div>
            <h3 className="text-xl font-semibold mb-2">Competitive Duels</h3>
            <p className="text-gray-600">
              Challenge other learners in timed coding battles to test your skills.
            </p>
          </div>
        </div>

        {/* Languages Section */}
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Languages You'll Master
          </h2>
          <div className="flex justify-center space-x-8">
            <div className="text-center">
              <div className="text-6xl mb-2">🐍</div>
              <h3 className="text-xl font-semibold">Python</h3>
              <p className="text-gray-600">Perfect for beginners</p>
            </div>
            <div className="text-center">
              <div className="text-6xl mb-2">⚡</div>
              <h3 className="text-xl font-semibold">C++</h3>
              <p className="text-gray-600">Advanced performance</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;