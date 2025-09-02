import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Lesson, Progress } from '../types';
import ApiClient from '../utils/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import TheorySection from '../components/lessons/TheorySection';
import LessonNavigation from '../components/lessons/LessonNavigation';
import ProgressTracker from '../components/lessons/ProgressTracker';

const LessonDetailPage: React.FC = () => {
  const { lessonId } = useParams<{ lessonId: string }>();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allLessons, setAllLessons] = useState<Lesson[]>([]);

  useEffect(() => {
    if (lessonId) {
      fetchLessonData(parseInt(lessonId));
      fetchAllLessons();
    }
  }, [lessonId]);

  const fetchLessonData = async (id: number) => {
    try {
      setLoading(true);
      setError(null);

      // Fetch lesson details
      const lessonResponse = await ApiClient.get(`/lessons/${id}`);
      if (!lessonResponse.ok) {
        throw new Error('Lesson not found');
      }
      const lessonData = await lessonResponse.json();
      setLesson(lessonData);

      // Fetch progress
      try {
        const progressResponse = await ApiClient.get(`/lessons/${id}/progress`);
        if (progressResponse.ok) {
          const progressData = await progressResponse.json();
          setProgress(progressData);
        }
      } catch (progressError) {
        // Progress might not exist yet, which is fine
        console.log('No progress found for lesson:', progressError);
      }

    } catch (err) {
      console.error('Error fetching lesson:', err);
      setError(err instanceof Error ? err.message : 'Failed to load lesson');
    } finally {
      setLoading(false);
    }
  };

  const fetchAllLessons = async () => {
    try {
      const response = await ApiClient.get('/lessons?include_progress=false');
      if (response.ok) {
        const data = await response.json();
        setAllLessons(data);
      }
    } catch (err) {
      console.error('Error fetching all lessons:', err);
    }
  };

  const handleContinueToPractice = async () => {
    if (!lesson) return;

    try {
      // Update progress to in_progress if not already started
      if (!progress || progress.status === 'not_started') {
        const progressData = {
          status: 'in_progress' as const,
          score: 0,
          attempts: 1
        };

        const response = await ApiClient.post(`/lessons/${lesson.id}/progress`, progressData);
        if (response.ok) {
          const updatedProgress = await response.json();
          setProgress(updatedProgress);
        }
      }

      // Navigate to questions (this will be implemented in future tasks)
      navigate(`/lessons/${lesson.id}/practice`);
    } catch (err) {
      console.error('Error updating progress:', err);
      // Still navigate even if progress update fails
      navigate(`/lessons/${lesson.id}/practice`);
    }
  };

  const getCurrentLessonIndex = () => {
    if (!lesson || allLessons.length === 0) return -1;
    return allLessons.findIndex(l => l.id === lesson.id);
  };

  const getPreviousLessonId = () => {
    const currentIndex = getCurrentLessonIndex();
    if (currentIndex > 0) {
      return allLessons[currentIndex - 1].id;
    }
    return undefined;
  };

  const getNextLessonId = () => {
    const currentIndex = getCurrentLessonIndex();
    if (currentIndex >= 0 && currentIndex < allLessons.length - 1) {
      return allLessons[currentIndex + 1].id;
    }
    return undefined;
  };

  const handlePreviousLesson = () => {
    const prevId = getPreviousLessonId();
    if (prevId) {
      navigate(`/lessons/${prevId}`);
    }
  };

  const handleNextLesson = () => {
    const nextId = getNextLessonId();
    if (nextId) {
      navigate(`/lessons/${nextId}`);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <LoadingSpinner />
      </div>
    );
  }

  if (error || !lesson) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 mb-2">
            <svg className="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-red-900 mb-2">Lesson Not Found</h3>
          <p className="text-red-700 mb-4">{error || 'The requested lesson could not be found.'}</p>
          <button
            onClick={() => navigate('/lessons')}
            className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-200"
          >
            Back to Lessons
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Navigation */}
      <div className="mb-6">
        <LessonNavigation
          currentLessonId={lesson.order_index}
          previousLessonId={getPreviousLessonId()}
          nextLessonId={getNextLessonId()}
          onPrevious={getPreviousLessonId() ? handlePreviousLesson : undefined}
          onNext={getNextLessonId() ? handleNextLesson : undefined}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-3">
          <TheorySection
            title={lesson.title}
            content={lesson.theory}
            language={lesson.language}
            difficulty={lesson.difficulty}
            xp_reward={lesson.xp_reward}
            onContinue={handleContinueToPractice}
          />
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <ProgressTracker
            progress={progress}
            lessonTitle={lesson.title}
          />
        </div>
      </div>
    </div>
  );
};

export default LessonDetailPage;