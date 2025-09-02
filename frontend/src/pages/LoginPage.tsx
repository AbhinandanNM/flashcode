import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { useFormValidation, commonValidationRules } from '../hooks/useFormValidation';
import FormInput from '../components/common/FormInput';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorDisplay from '../components/common/ErrorDisplay';

const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState<string | null>(null);
  
  const { login, state } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { showSuccess, showError } = useToast();
  
  const { errors, touched, validateField, setFieldTouched, setFieldError } = useFormValidation({
    email: commonValidationRules.email,
    password: { required: true, minLength: 1 } // Simplified for login
  });

  // Get the intended destination from location state
  const from = (location.state as any)?.from?.pathname || '/lessons';

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    setError(null); // Clear general error when user types
    
    // Validate field and update errors
    const fieldError = validateField(field, value);
    setFieldError(field, fieldError);
  };

  const handleInputBlur = (field: string) => {
    setFieldTouched(field, true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    
    // Mark all fields as touched
    setFieldTouched('email', true);
    setFieldTouched('password', true);
    
    // Validate all fields
    const emailError = validateField('email', formData.email);
    const passwordError = validateField('password', formData.password);
    
    if (emailError || passwordError) {
      setFieldError('email', emailError);
      setFieldError('password', passwordError);
      return;
    }

    try {
      await login(formData.email, formData.password);
      showSuccess('Welcome back!', 'You have successfully signed in.');
      navigate(from, { replace: true });
    } catch (err: any) {
      const errorMessage = err.message || 'Invalid email or password';
      setError(errorMessage);
      showError('Login Failed', errorMessage);
    }
  };

  const isFormValid = !errors.email && !errors.password && formData.email && formData.password;

  return (
    <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-8">
      <div className="text-center mb-8">
        <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-blue-100 mb-4">
          <svg className="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome Back</h1>
        <p className="text-gray-600 mt-2">Sign in to continue your learning journey</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <ErrorDisplay error={error} onDismiss={() => setError(null)} />

        <FormInput
          label="Email Address"
          name="email"
          type="email"
          value={formData.email}
          onChange={(value) => handleInputChange('email', value)}
          onBlur={() => handleInputBlur('email')}
          error={errors.email}
          touched={touched.email}
          placeholder="Enter your email"
          autoComplete="email"
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
          autoComplete="current-password"
          showPasswordToggle
          required
        />

        <button
          type="submit"
          disabled={state.isLoading || !isFormValid}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white py-3 px-4 rounded-md font-semibold transition-colors duration-200 flex items-center justify-center"
        >
          {state.isLoading ? (
            <LoadingSpinner size="sm" color="white" text="Signing In..." />
          ) : (
            'Sign In'
          )}
        </button>
      </form>

      <div className="mt-6 text-center">
        <p className="text-gray-600">
          Don't have an account?{' '}
          <Link to="/register" className="text-blue-600 hover:text-blue-700 font-semibold">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;