import React from 'react';

interface DebuggingHintsProps {
  error?: string;
  code: string;
  language: 'python' | 'cpp';
}

interface Hint {
  type: 'error' | 'warning' | 'suggestion';
  message: string;
  line?: number;
  solution?: string;
}

const DebuggingHints: React.FC<DebuggingHintsProps> = ({ error, code, language }) => {
  const generateHints = (): Hint[] => {
    const hints: Hint[] = [];
    
    if (!error && !code.trim()) {
      return hints;
    }

    // Error-based hints
    if (error) {
      const errorLower = error.toLowerCase();
      
      // Python-specific error hints
      if (language === 'python') {
        if (errorLower.includes('indentationerror') || errorLower.includes('unexpected indent')) {
          hints.push({
            type: 'error',
            message: 'Indentation Error',
            solution: 'Python uses indentation to define code blocks. Make sure your indentation is consistent (use 4 spaces).'
          });
        }
        
        if (errorLower.includes('syntaxerror')) {
          hints.push({
            type: 'error',
            message: 'Syntax Error',
            solution: 'Check for missing colons (:), parentheses, or quotes. Make sure your syntax follows Python rules.'
          });
        }
        
        if (errorLower.includes('nameerror')) {
          hints.push({
            type: 'error',
            message: 'Name Error',
            solution: 'You\'re trying to use a variable or function that hasn\'t been defined. Check your variable names and spelling.'
          });
        }
        
        if (errorLower.includes('typeerror')) {
          hints.push({
            type: 'error',
            message: 'Type Error',
            solution: 'You\'re trying to perform an operation on incompatible types. Check your data types and operations.'
          });
        }
        
        if (errorLower.includes('indexerror')) {
          hints.push({
            type: 'error',
            message: 'Index Error',
            solution: 'You\'re trying to access an index that doesn\'t exist. Check your list/string bounds.'
          });
        }
      }
      
      // C++ specific error hints
      if (language === 'cpp') {
        if (errorLower.includes('expected') && errorLower.includes(';')) {
          hints.push({
            type: 'error',
            message: 'Missing Semicolon',
            solution: 'C++ statements must end with a semicolon (;). Check your code for missing semicolons.'
          });
        }
        
        if (errorLower.includes('undeclared') || errorLower.includes('not declared')) {
          hints.push({
            type: 'error',
            message: 'Undeclared Variable/Function',
            solution: 'You\'re using a variable or function that hasn\'t been declared. Make sure to declare variables before using them.'
          });
        }
        
        if (errorLower.includes('expected') && errorLower.includes('}')) {
          hints.push({
            type: 'error',
            message: 'Missing Closing Brace',
            solution: 'Check that all opening braces { have corresponding closing braces }.'
          });
        }
      }
    }

    // Code analysis hints
    const lines = code.split('\n');
    
    if (language === 'python') {
      // Check for common Python issues
      lines.forEach((line, index) => {
        const trimmedLine = line.trim();
        
        // Check for missing colons
        if (trimmedLine.match(/^(if|elif|else|for|while|def|class|try|except|finally|with)\s.*[^:]$/)) {
          hints.push({
            type: 'warning',
            message: `Line ${index + 1}: Missing colon`,
            line: index + 1,
            solution: 'Python control structures require a colon (:) at the end.'
          });
        }
        
        // Check for print without parentheses (Python 3)
        if (trimmedLine.match(/^print\s+[^(]/)) {
          hints.push({
            type: 'suggestion',
            message: `Line ${index + 1}: Use print() function`,
            line: index + 1,
            solution: 'In Python 3, print is a function and requires parentheses: print("hello")'
          });
        }
      });
    }
    
    if (language === 'cpp') {
      // Check for common C++ issues
      lines.forEach((line, index) => {
        const trimmedLine = line.trim();
        
        // Check for missing semicolons
        if (trimmedLine && !trimmedLine.endsWith(';') && !trimmedLine.endsWith('{') && 
            !trimmedLine.endsWith('}') && !trimmedLine.startsWith('#') && 
            !trimmedLine.startsWith('//') && !trimmedLine.startsWith('/*')) {
          if (trimmedLine.match(/^(int|float|double|char|string|bool|auto)\s+\w+\s*=/) ||
              trimmedLine.match(/^\w+\s*=/) ||
              trimmedLine.match(/^(cout|cin|return)\s/)) {
            hints.push({
              type: 'warning',
              message: `Line ${index + 1}: Missing semicolon`,
              line: index + 1,
              solution: 'C++ statements should end with a semicolon (;)'
            });
          }
        }
      });
    }

    return hints;
  };

  const hints = generateHints();

  if (hints.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="border-b border-gray-200 p-3">
        <h3 className="text-sm font-medium text-gray-900 flex items-center">
          <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Debugging Hints
        </h3>
      </div>
      <div className="p-3 space-y-3">
        {hints.map((hint, index) => (
          <div key={index} className={`p-3 rounded-lg border-l-4 ${
            hint.type === 'error' ? 'bg-red-50 border-red-400' :
            hint.type === 'warning' ? 'bg-yellow-50 border-yellow-400' :
            'bg-blue-50 border-blue-400'
          }`}>
            <div className="flex items-start">
              <div className={`flex-shrink-0 ${
                hint.type === 'error' ? 'text-red-600' :
                hint.type === 'warning' ? 'text-yellow-600' :
                'text-blue-600'
              }`}>
                {hint.type === 'error' ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                ) : hint.type === 'warning' ? (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
              <div className="ml-3 flex-1">
                <h4 className={`text-sm font-medium ${
                  hint.type === 'error' ? 'text-red-800' :
                  hint.type === 'warning' ? 'text-yellow-800' :
                  'text-blue-800'
                }`}>
                  {hint.message}
                </h4>
                {hint.solution && (
                  <p className={`mt-1 text-xs ${
                    hint.type === 'error' ? 'text-red-700' :
                    hint.type === 'warning' ? 'text-yellow-700' :
                    'text-blue-700'
                  }`}>
                    {hint.solution}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DebuggingHints;