import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useResponsive } from '../../hooks/useResponsive';

const Navbar: React.FC = () => {
  const { state, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { isMobile, isTablet } = useResponsive();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
    setIsMobileMenuOpen(false);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo and Brand */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="text-2xl font-bold">🚀</div>
              <span className="text-xl font-bold">CodeCrafts</span>
            </Link>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            {state.isAuthenticated ? (
              <>
                <Link 
                  to="/lessons" 
                  className="hover:text-blue-200 transition-colors duration-200"
                >
                  Lessons
                </Link>
                <Link 
                  to="/flashcards" 
                  className="hover:text-blue-200 transition-colors duration-200"
                >
                  Flashcards
                </Link>
                <Link 
                  to="/duels" 
                  className="hover:text-blue-200 transition-colors duration-200"
                >
                  Duels
                </Link>
                <Link 
                  to="/leaderboard" 
                  className="hover:text-blue-200 transition-colors duration-200"
                >
                  Leaderboard
                </Link>
              </>
            ) : (
              <>
                <Link 
                  to="/about" 
                  className="hover:text-blue-200 transition-colors duration-200"
                >
                  About
                </Link>
              </>
            )}
          </div>

          {/* User Profile / Auth Buttons */}
          <div className="flex items-center space-x-4">
            {state.isAuthenticated && state.user ? (
              <>
                {/* XP Display */}
                <div className="hidden sm:flex items-center space-x-2 bg-blue-700 px-3 py-1 rounded-full">
                  <span className="text-yellow-300">⭐</span>
                  <span className="font-semibold">{state.user.xp} XP</span>
                </div>

                {/* Streak Display */}
                <div className="hidden sm:flex items-center space-x-2 bg-orange-500 px-3 py-1 rounded-full">
                  <span className="text-red-400">🔥</span>
                  <span className="font-semibold">{state.user.streak}</span>
                </div>

                {/* User Menu */}
                <div className="relative group">
                  <button className="flex items-center space-x-2 hover:text-blue-200 transition-colors duration-200">
                    <div className="w-8 h-8 bg-blue-800 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold">
                        {state.user.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <span className="hidden md:block">{state.user.username}</span>
                  </button>
                  
                  {/* Dropdown Menu */}
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <Link
                      to="/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Profile
                    </Link>
                    <Link
                      to="/settings"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Settings
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex items-center space-x-4">
                <Link
                  to="/login"
                  className="hover:text-blue-200 transition-colors duration-200"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-md transition-colors duration-200"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          {isMobile && (
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-blue-100 hover:text-white hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white transition-colors"
              aria-expanded="false"
            >
              <span className="sr-only">Open main menu</span>
              {!isMobileMenuOpen ? (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              ) : (
                <svg className="block h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              )}
            </button>
          )}
        </div>

        {/* Mobile menu */}
        {isMobile && (
          <div className={`${isMobileMenuOpen ? 'block' : 'hidden'} pb-3 pt-2 border-t border-blue-500`}>
            <div className="px-2 space-y-1">
              {state.isAuthenticated ? (
                <>
                  <Link
                    to="/lessons"
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      isActive('/lessons')
                        ? 'bg-blue-700 text-white'
                        : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                    }`}
                    onClick={closeMobileMenu}
                  >
                    <span className="mr-3 text-lg">📚</span>
                    Lessons
                  </Link>
                  <Link
                    to="/flashcards"
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      isActive('/flashcards')
                        ? 'bg-blue-700 text-white'
                        : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                    }`}
                    onClick={closeMobileMenu}
                  >
                    <span className="mr-3 text-lg">🃏</span>
                    Flashcards
                  </Link>
                  <Link
                    to="/duels"
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      isActive('/duels')
                        ? 'bg-blue-700 text-white'
                        : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                    }`}
                    onClick={closeMobileMenu}
                  >
                    <span className="mr-3 text-lg">⚔️</span>
                    Duels
                  </Link>
                  <Link
                    to="/leaderboard"
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      isActive('/leaderboard')
                        ? 'bg-blue-700 text-white'
                        : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                    }`}
                    onClick={closeMobileMenu}
                  >
                    <span className="mr-3 text-lg">🏆</span>
                    Leaderboard
                  </Link>
                  <Link
                    to="/profile"
                    className={`flex items-center px-3 py-2 rounded-md text-base font-medium transition-colors ${
                      isActive('/profile')
                        ? 'bg-blue-700 text-white'
                        : 'text-blue-100 hover:bg-blue-500 hover:text-white'
                    }`}
                    onClick={closeMobileMenu}
                  >
                    <span className="mr-3 text-lg">👤</span>
                    Profile
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left flex items-center px-3 py-2 rounded-md text-base font-medium text-blue-100 hover:bg-blue-500 hover:text-white transition-colors"
                  >
                    <span className="mr-3 text-lg">🚪</span>
                    Logout
                  </button>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="block px-3 py-2 rounded-md text-base font-medium text-blue-100 hover:bg-blue-500 hover:text-white transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="block px-3 py-2 rounded-md text-base font-medium bg-blue-700 hover:bg-blue-800 transition-colors"
                    onClick={closeMobileMenu}
                  >
                    Sign Up
                  </Link>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;