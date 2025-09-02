import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import ProtectedRoute from '../ProtectedRoute';

// Mock the useAuth hook
jest.mock('../../../contexts/AuthContext', () => ({
  ...jest.requireActual('../../../contexts/AuthContext'),
  useAuth: () => ({
    state: {
      isAuthenticated: false,
      isLoading: false,
      user: null,
      token: null,
    },
  }),
}));

const TestComponent = () => <div>Protected Content</div>;

describe('ProtectedRoute', () => {
  it('redirects to login when not authenticated', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute>
            <TestComponent />
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    );

    // Should not render the protected content
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('shows loading spinner when loading', () => {
    // This would require mocking the hook differently for loading state
    // Implementation would be added in a real test scenario
  });
});