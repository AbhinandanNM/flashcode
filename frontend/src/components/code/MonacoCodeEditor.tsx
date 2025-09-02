import React, { useState, useRef, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import * as monaco from 'monaco-editor';
import DebuggingHints from './DebuggingHints';

interface MonacoCodeEditorProps {
  language: 'python' | 'cpp';
  value: string;
  onChange: (value: string) => void;
  onRun?: () => void;
  isRunning?: boolean;
  disabled?: boolean;
  height?: string;
  theme?: 'vs-dark' | 'light';
  showRunButton?: boolean;
  showDebuggingHints?: boolean;
  executionResult?: {
    output?: string;
    error?: string;
    status?: string;
    execution_time?: number;
  } | null;
}

const MonacoCodeEditor: React.FC<MonacoCodeEditorProps> = ({
  language,
  value,
  onChange,
  onRun,
  isRunning = false,
  disabled = false,
  height = '300px',
  theme = 'vs-dark',
  showRunButton = true,
  showDebuggingHints = true,
  executionResult,
}) => {
  const editorRef = useRef<monaco.editor.IStandaloneCodeEditor | null>(null);
  const [isEditorReady, setIsEditorReady] = useState(false);

  const handleEditorDidMount = (editor: monaco.editor.IStandaloneCodeEditor) => {
    editorRef.current = editor;
    setIsEditorReady(true);

    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: language === 'python' ? 4 : 2,
      insertSpaces: true,
      wordWrap: 'on',
      lineNumbers: 'on',
      glyphMargin: true,
      folding: true,
      lineDecorationsWidth: 10,
      lineNumbersMinChars: 3,
    });

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      if (onRun && !isRunning && !disabled) {
        onRun();
      }
    });
  };

  const handleEditorChange = (newValue: string | undefined) => {
    if (newValue !== undefined && !disabled) {
      onChange(newValue);
    }
  };

  const getLanguageDisplayName = () => {
    switch (language) {
      case 'python':
        return '🐍 Python';
      case 'cpp':
        return '⚡ C++';
      default:
        return language;
    }
  };

  const getMonacoLanguage = () => {
    switch (language) {
      case 'python':
        return 'python';
      case 'cpp':
        return 'cpp';
      default:
        return 'plaintext';
    }
  };

  const formatExecutionTime = (time?: number) => {
    if (!time) return '';
    if (time < 1000) return `${time}ms`;
    return `${(time / 1000).toFixed(2)}s`;
  };

  return (
    <div className="space-y-4">
      <div className="border border-gray-300 rounded-lg overflow-hidden bg-white">
      {/* Editor Header */}
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-gray-700">Code Editor</span>
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
            language === 'python' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'
          }`}>
            {getLanguageDisplayName()}
          </span>
          {executionResult?.execution_time && (
            <span className="text-xs text-gray-500">
              {formatExecutionTime(executionResult.execution_time)}
            </span>
          )}
        </div>
        
        {showRunButton && onRun && (
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500">Ctrl+Enter to run</span>
            <button
              onClick={onRun}
              disabled={isRunning || disabled || !value.trim()}
              className={`flex items-center space-x-2 px-3 py-1.5 rounded text-sm font-medium transition-colors duration-200 ${
                isRunning || disabled || !value.trim()
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-green-600 hover:bg-green-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2'
              }`}
            >
              {isRunning ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Running...</span>
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h.01M19 10a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Run</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>

      {/* Monaco Editor */}
      <div style={{ height }}>
        <Editor
          height="100%"
          language={getMonacoLanguage()}
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme={theme}
          options={{
            readOnly: disabled,
            contextmenu: !disabled,
            quickSuggestions: !disabled,
            suggestOnTriggerCharacters: !disabled,
            acceptSuggestionOnEnter: disabled ? 'off' : 'on',
            tabCompletion: disabled ? 'off' : 'on',
            wordBasedSuggestions: !disabled,
            parameterHints: { enabled: !disabled },
            autoIndent: 'full',
            formatOnPaste: true,
            formatOnType: true,
          }}
          loading={
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500">Loading editor...</div>
            </div>
          }
        />
      </div>

      {/* Execution Result */}
      {executionResult && (
        <div className="border-t border-gray-200">
          <div className="bg-gray-50 px-4 py-2 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Output</span>
              <div className="flex items-center space-x-2">
                {executionResult.status && (
                  <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                    executionResult.status === 'success' ? 'bg-green-100 text-green-800' :
                    executionResult.status === 'error' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {executionResult.status}
                  </span>
                )}
                {executionResult.execution_time && (
                  <span className="text-xs text-gray-500">
                    {formatExecutionTime(executionResult.execution_time)}
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="p-4 bg-gray-900 text-green-400 font-mono text-sm max-h-48 overflow-y-auto">
            {executionResult.error ? (
              <div className="text-red-400">
                <div className="font-medium mb-1 text-red-300">Error:</div>
                <pre className="whitespace-pre-wrap text-red-400">{executionResult.error}</pre>
              </div>
            ) : (
              <pre className="whitespace-pre-wrap">
                {executionResult.output || '(No output)'}
              </pre>
            )}
          </div>
        </div>
      )}

      {/* Editor Status Bar */}
      <div className="bg-gray-50 px-4 py-2 border-t border-gray-200 text-xs text-gray-600 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <span>Lines: {value.split('\n').length}</span>
          <span>Characters: {value.length}</span>
        </div>
        <div className="flex items-center space-x-2">
          {disabled && (
            <span className="text-orange-600 font-medium">Read Only</span>
          )}
          <span className="capitalize">{getMonacoLanguage()}</span>
        </div>
      </div>
      
      {/* Debugging Hints */}
      {showDebuggingHints && (executionResult?.error || value.trim()) && (
        <DebuggingHints
          error={executionResult?.error}
          code={value}
          language={language}
        />
      )}
    </div>
  );
};

export default MonacoCodeEditor;