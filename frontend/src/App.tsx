import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import ErrorBoundary from './components/common/ErrorBoundary';
import Navbar from './components/layout/Navbar';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import LessonsPage from './pages/LessonsPage';
import LessonDetailPage from './pages/LessonDetailPage';
import PracticePage from './pages/PracticePage';
import CodeEditorPage from './pages/CodeEditorPage';
import LeaderboardPage from './pages/LeaderboardPage';
import DuelsPage from './pages/DuelsPage';
import FlashcardsPage from './pages/FlashcardsPage';
import ProtectedRoute from './components/auth/ProtectedRoute';

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              {/* Protected Routes */}
              <Route 
                path="/lessons" 
                element={
                  <ProtectedRoute>
                    <LessonsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/lessons/:lessonId" 
                element={
                  <ProtectedRoute>
                    <LessonDetailPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/lessons/:lessonId/practice" 
                element={
                  <ProtectedRoute>
                    <PracticePage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/code/:questionId" 
                element={
                  <ProtectedRoute>
                    <CodeEditorPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/flashcards" 
                element={
                  <ProtectedRoute>
                    <FlashcardsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/duels" 
                element={
                  <ProtectedRoute>
                    <DuelsPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/leaderboard" 
                element={
                  <ProtectedRoute>
                    <LeaderboardPage />
                  </ProtectedRoute>
                } 
              />
              <Route 
                path="/profile" 
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                } 
              />
              
              {/* Catch all route */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  </ToastProvider>
</ErrorBoundary>
  );
}

export default App;