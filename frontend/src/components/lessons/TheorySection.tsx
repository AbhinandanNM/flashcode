import React from 'react';

interface TheorySectionProps {
  title: string;
  content: string;
  language: string;
  difficulty: number;
  xp_reward: number;
  onContinue: () => void;
}

const TheorySection: React.FC<TheorySectionProps> = ({
  title,
  content,
  language,
  difficulty,
  xp_reward,
  onContinue,
}) => {
  const getDifficultyColor = (difficulty: number) => {
    switch (difficulty) {
      case 1: return 'bg-green-100 text-green-800';
      case 2: return 'bg-blue-100 text-blue-800';
      case 3: return 'bg-yellow-100 text-yellow-800';
      case 4: return 'bg-orange-100 text-orange-800';
      case 5: return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getDifficultyText = (difficulty: number) => {
    switch (difficulty) {
      case 1: return 'Beginner';
      case 2: return 'Easy';
      case 3: return 'Medium';
      case 4: return 'Hard';
      case 5: return 'Expert';
      default: return 'Unknown';
    }
  };

  const getLanguageIcon = (language: string) => {
    switch (language.toLowerCase()) {
      case 'python':
        return '🐍';
      case 'cpp':
        return '⚡';
      default:
        return '💻';
    }
  };

  // Format the content to handle basic markdown-like formatting
  const formatContent = (text: string) => {
    return text
      .split('\n')
      .map((line, index) => {
        // Handle code blocks (lines starting with 4+ spaces or tabs)
        if (line.match(/^(\s{4,}|\t)/)) {
          return (
            <pre key={index} className="bg-gray-100 p-3 rounded-md my-2 overflow-x-auto">
              <code className="text-sm font-mono text-gray-800">{line.trim()}</code>
            </pre>
          );
        }
        
        // Handle headers (lines starting with #)
        if (line.startsWith('# ')) {
          return (
            <h2 key={index} className="text-xl font-bold text-gray-900 mt-6 mb-3">
              {line.substring(2)}
            </h2>
          );
        }
        
        if (line.startsWith('## ')) {
          return (
            <h3 key={index} className="text-lg font-semibold text-gray-900 mt-4 mb-2">
              {line.substring(3)}
            </h3>
          );
        }
        
        // Handle inline code (text between backticks)
        const codeRegex = /`([^`]+)`/g;
        const parts = line.split(codeRegex);
        const formattedLine = parts.map((part, partIndex) => {
          if (partIndex % 2 === 1) {
            return (
              <code key={partIndex} className="bg-gray-100 px-1 py-0.5 rounded text-sm font-mono">
                {part}
              </code>
            );
          }
          return part;
        });
        
        // Regular paragraph
        if (line.trim()) {
          return (
            <p key={index} className="text-gray-700 leading-relaxed mb-3">
              {formattedLine}
            </p>
          );
        }
        
        return <br key={index} />;
      });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-3xl">{getLanguageIcon(language)}</span>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
              <div className="flex items-center space-x-4 mt-2">
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(difficulty)}`}>
                  {getDifficultyText(difficulty)}
                </span>
                <span className="text-sm text-gray-600 capitalize">{language}</span>
                <div className="flex items-center space-x-1 text-sm text-gray-600">
                  <span>⭐</span>
                  <span>{xp_reward} XP</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        <div className="prose max-w-none">
          {formatContent(content)}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 p-6">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <span>📚 Theory • Estimated reading time: ~30 seconds</span>
          </div>
          <button
            onClick={onContinue}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Continue to Practice →
          </button>
        </div>
      </div>
    </div>
  );
};

export default TheorySection;