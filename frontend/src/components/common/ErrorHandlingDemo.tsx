import React, { useState } from 'react';
import { useToast } from '../../contexts/ToastContext';
import ErrorDisplay from './ErrorDisplay';
import LoadingSpinner from './LoadingSpinner';
import FormInput from './FormInput';
import { useFormValidation, commonValidationRules } from '../../hooks/useFormValidation';

const ErrorHandlingDemo: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: ''
  });
  
  const { showSuccess, showError, showWarning, showInfo } = useToast();
  
  const { errors, touched, validateField, setFieldTouched, setFieldError } = useFormValidation({
    email: commonValidationRules.email,
    password: commonValidationRules.password,
    username: commonValidationRules.username
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    const fieldError = validateField(field, value);
    setFieldError(field, fieldError);
  };

  const handleInputBlur = (field: string) => {
    setFieldTouched(field, true);
  };

  const simulateApiError = () => {
    setError('Failed to connect to server. Please check your internet connection.');
  };

  const simulateLoading = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 3000);
  };

  const throwError = () => {
    throw new Error('This is a test error to demonstrate error boundary');
  };

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Error Handling Demo</h2>
        
        {/* Toast Notifications */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Toast Notifications</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => showSuccess('Success!', 'Operation completed successfully.')}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
              Show Success
            </button>
            <button
              onClick={() => showError('Error!', 'Something went wrong.')}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Show Error
            </button>
            <button
              onClick={() => showWarning('Warning!', 'Please be careful.')}
              className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
            >
              Show Warning
            </button>
            <button
              onClick={() => showInfo('Info', 'Here is some information.')}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Show Info
            </button>
          </div>
        </div>

        {/* Error Display */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Error Display</h3>
          <ErrorDisplay error={error} onDismiss={() => setError(null)} />
          <button
            onClick={simulateApiError}
            className="mt-4 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Simulate API Error
          </button>
        </div>

        {/* Loading States */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Loading States</h3>
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <LoadingSpinner size="sm" />
              <LoadingSpinner size="md" />
              <LoadingSpinner size="lg" />
              <LoadingSpinner size="xl" />
            </div>
            <LoadingSpinner text="Loading data..." />
            <button
              onClick={simulateLoading}
              disabled={loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50 flex items-center"
            >
              {loading ? <LoadingSpinner size="sm" color="white" text="Loading..." /> : 'Simulate Loading'}
            </button>
          </div>
        </div>

        {/* Form Validation */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Form Validation</h3>
          <div className="space-y-4">
            <FormInput
              label="Email"
              name="email"
              type="email"
              value={formData.email}
              onChange={(value) => handleInputChange('email', value)}
              onBlur={() => handleInputBlur('email')}
              error={errors.email}
              touched={touched.email}
              placeholder="Enter your email"
              required
            />
            
            <FormInput
              label="Username"
              name="username"
              type="text"
              value={formData.username}
              onChange={(value) => handleInputChange('username', value)}
              onBlur={() => handleInputBlur('username')}
              error={errors.username}
              touched={touched.username}
              placeholder="Enter your username"
              required
            />
            
            <FormInput
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={(value) => handleInputChange('password', value)}
              onBlur={() => handleInputBlur('password')}
              error={errors.password}
              touched={touched.password}
              placeholder="Enter your password"
              showPasswordToggle
              required
            />
          </div>
        </div>

        {/* Error Boundary Test */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Error Boundary</h3>
          <button
            onClick={throwError}
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
          >
            Throw Error (Test Error Boundary)
          </button>
          <p className="text-sm text-gray-600 mt-2">
            This will trigger the error boundary and show the error fallback UI.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ErrorHandlingDemo;