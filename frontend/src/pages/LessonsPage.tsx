import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lesson, Progress } from '../types';
import ApiClient from '../utils/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import LessonCard from '../components/lessons/LessonCard';
import LessonFilters from '../components/lessons/LessonFilters';

interface LessonWithProgress extends Lesson {
  progress?: Progress | null;
}

const LessonsPage: React.FC = () => {
  const navigate = useNavigate();
  const [lessons, setLessons] = useState<LessonWithProgress[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');

  useEffect(() => {
    fetchLessons();
  }, [selectedLanguage, selectedDifficulty]);

  const fetchLessons = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query parameters
      const params = new URLSearchParams();
      if (selectedLanguage) params.append('language', selectedLanguage);
      if (selectedDifficulty) params.append('difficulty', selectedDifficulty);
      params.append('include_progress', 'true');

      const response = await ApiClient.get(`/lessons?${params.toString()}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch lessons');
      }

      const data = await response.json();
      setLessons(data);
    } catch (err) {
      console.error('Error fetching lessons:', err);
      setError(err instanceof Error ? err.message : 'Failed to load lessons');
    } finally {
      setLoading(false);
    }
  };

  const handleLessonClick = (lessonId: number) => {
    navigate(`/lessons/${lessonId}`);
  };

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language);
  };

  const handleDifficultyChange = (difficulty: string) => {
    setSelectedDifficulty(difficulty);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 mb-2">
            <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-red-900 mb-2">Error Loading Lessons</h3>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={fetchLessons}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Programming Lessons</h1>
        <p className="text-gray-600">
          Learn programming through interactive lessons and hands-on practice. 
          Each lesson includes theory and practical exercises to reinforce your learning.
        </p>
      </div>

      {/* Filters */}
      <LessonFilters
        selectedLanguage={selectedLanguage}
        selectedDifficulty={selectedDifficulty}
        onLanguageChange={handleLanguageChange}
        onDifficultyChange={handleDifficultyChange}
      />

      {/* Lessons Grid */}
      {lessons.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Lessons Found</h3>
          <p className="text-gray-600 mb-4">
            {selectedLanguage || selectedDifficulty 
              ? 'No lessons match your current filters. Try adjusting your search criteria.'
              : 'No lessons are available at the moment. Check back later!'
            }
          </p>
          {(selectedLanguage || selectedDifficulty) && (
            <button
              onClick={() => {
                setSelectedLanguage('');
                setSelectedDifficulty('');
              }}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              Clear Filters
            </button>
          )}
        </div>
      ) : (
        <>
          {/* Results Summary */}
          <div className="mb-6">
            <p className="text-sm text-gray-600">
              Showing {lessons.length} lesson{lessons.length !== 1 ? 's' : ''}
              {selectedLanguage && (
                <span className="ml-1">
                  in <span className="font-medium capitalize">{selectedLanguage}</span>
                </span>
              )}
              {selectedDifficulty && (
                <span className="ml-1">
                  at <span className="font-medium">
                    {selectedDifficulty === '1' ? 'Beginner' :
                     selectedDifficulty === '2' ? 'Easy' :
                     selectedDifficulty === '3' ? 'Medium' :
                     selectedDifficulty === '4' ? 'Hard' :
                     selectedDifficulty === '5' ? 'Expert' : 'Unknown'} level
                  </span>
                </span>
              )}
            </p>
          </div>

          {/* Lessons Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {lessons.map((lesson) => (
              <LessonCard
                key={lesson.id}
                lesson={lesson}
                progress={lesson.progress}
                onClick={() => handleLessonClick(lesson.id)}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default LessonsPage;