import React from 'react';

interface LessonFiltersProps {
  selectedLanguage: string;
  selectedDifficulty: string;
  onLanguageChange: (language: string) => void;
  onDifficultyChange: (difficulty: string) => void;
}

const LessonFilters: React.FC<LessonFiltersProps> = ({
  selectedLanguage,
  selectedDifficulty,
  onLanguageChange,
  onDifficultyChange,
}) => {
  const languages = [
    { value: '', label: 'All Languages' },
    { value: 'python', label: '🐍 Python' },
    { value: 'cpp', label: '⚡ C++' },
  ];

  const difficulties = [
    { value: '', label: 'All Difficulties' },
    { value: '1', label: 'Beginner' },
    { value: '2', label: 'Easy' },
    { value: '3', label: 'Medium' },
    { value: '4', label: 'Hard' },
    { value: '5', label: 'Expert' },
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Filter Lessons</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Language Filter */}
        <div>
          <label htmlFor="language-filter" className="block text-sm font-medium text-gray-700 mb-2">
            Programming Language
          </label>
          <select
            id="language-filter"
            value={selectedLanguage}
            onChange={(e) => onLanguageChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {languages.map((language) => (
              <option key={language.value} value={language.value}>
                {language.label}
              </option>
            ))}
          </select>
        </div>

        {/* Difficulty Filter */}
        <div>
          <label htmlFor="difficulty-filter" className="block text-sm font-medium text-gray-700 mb-2">
            Difficulty Level
          </label>
          <select
            id="difficulty-filter"
            value={selectedDifficulty}
            onChange={(e) => onDifficultyChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {difficulties.map((difficulty) => (
              <option key={difficulty.value} value={difficulty.value}>
                {difficulty.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default LessonFilters;