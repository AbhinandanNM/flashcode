import React from 'react';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders } from '../utils/testUtils';
import App from '../App';
import { server } from '../mocks/server';
import { rest } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

describe('User Flows', () => {
  beforeEach(() => {
    mockLocalStorage.getItem.mockReturnValue(null);
    jest.clearAllMocks();
  });

  describe('Authentication Flow', () => {
    it('allows user to login successfully', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/login'] });

      // Fill in login form
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const loginButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(loginButton);

      // Should redirect to home page after successful login
      await waitFor(() => {
        expect(screen.getByText(/welcome/i)).toBeInTheDocument();
      });
    });

    it('shows error for invalid credentials', async () => {
      const user = userEvent.setup();
      
      // Mock failed login
      server.use(
        rest.post(`${API_BASE_URL}/auth/login`, (req, res, ctx) => {
          return res(
            ctx.status(401),
            ctx.json({ message: 'Invalid credentials' })
          );
        })
      );

      renderWithProviders(<App />, { initialEntries: ['/login'] });

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const loginButton = screen.getByRole('button', { name: /sign in/i });

      await user.type(emailInput, 'wrong@example.com');
      await user.type(passwordInput, 'wrongpassword');
      await user.click(loginButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });

    it('allows user to register successfully', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/register'] });

      const usernameInput = screen.getByLabelText(/username/i);
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const registerButton = screen.getByRole('button', { name: /create account/i });

      await user.type(usernameInput, 'testuser');
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(registerButton);

      await waitFor(() => {
        expect(screen.getByText(/welcome/i)).toBeInTheDocument();
      });
    });
  });

  describe('Learning Flow', () => {
    beforeEach(() => {
      // Mock authenticated user
      mockLocalStorage.getItem.mockReturnValue('mock-jwt-token');
    });

    it('allows user to browse and start a lesson', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/lessons'] });

      // Wait for lessons to load
      await waitFor(() => {
        expect(screen.getByText('Python Basics')).toBeInTheDocument();
      });

      // Click on a lesson
      const lessonCard = screen.getByText('Python Basics');
      await user.click(lessonCard);

      // Should navigate to lesson detail page
      await waitFor(() => {
        expect(screen.getByText(/start lesson/i)).toBeInTheDocument();
      });

      // Start the lesson
      const startButton = screen.getByText(/start lesson/i);
      await user.click(startButton);

      // Should show lesson content
      await waitFor(() => {
        expect(screen.getByText(/lesson content/i)).toBeInTheDocument();
      });
    });

    it('allows user to answer questions and track progress', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/lessons/1'] });

      // Wait for lesson to load and start it
      await waitFor(() => {
        expect(screen.getByText(/start lesson/i)).toBeInTheDocument();
      });

      const startButton = screen.getByText(/start lesson/i);
      await user.click(startButton);

      // Should show first question
      await waitFor(() => {
        expect(screen.getByText(/what is the correct way/i)).toBeInTheDocument();
      });

      // Select correct answer
      const correctOption = screen.getByText('x = 5');
      await user.click(correctOption);

      // Submit answer
      const submitButton = screen.getByText(/submit/i);
      await user.click(submitButton);

      // Should show feedback
      await waitFor(() => {
        expect(screen.getByText(/correct/i)).toBeInTheDocument();
      });
    });

    it('tracks XP and level progression', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/profile'] });

      // Should show user stats
      await waitFor(() => {
        expect(screen.getByText(/1250/)).toBeInTheDocument(); // XP
        expect(screen.getByText(/level 5/i)).toBeInTheDocument();
      });
    });
  });

  describe('Code Editor Flow', () => {
    beforeEach(() => {
      mockLocalStorage.getItem.mockReturnValue('mock-jwt-token');
    });

    it('allows user to write and execute code', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/code-editor'] });

      // Wait for editor to load
      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      // Type code
      const editor = screen.getByRole('textbox');
      await user.type(editor, 'print("Hello, World!")');

      // Run code
      const runButton = screen.getByText(/run/i);
      await user.click(runButton);

      // Should show output
      await waitFor(() => {
        expect(screen.getByText(/hello, world/i)).toBeInTheDocument();
      });
    });

    it('validates code against test cases', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/practice'] });

      // Wait for practice page to load
      await waitFor(() => {
        expect(screen.getByText(/write a function/i)).toBeInTheDocument();
      });

      // Write solution
      const editor = screen.getByRole('textbox');
      await user.type(editor, 'def solution(n):\n    return n * 3');

      // Submit solution
      const submitButton = screen.getByText(/submit/i);
      await user.click(submitButton);

      // Should show validation results
      await waitFor(() => {
        expect(screen.getByText(/all tests passed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Gamification Flow', () => {
    beforeEach(() => {
      mockLocalStorage.getItem.mockReturnValue('mock-jwt-token');
    });

    it('displays leaderboard and user ranking', async () => {
      renderWithProviders(<App />, { initialEntries: ['/leaderboard'] });

      await waitFor(() => {
        expect(screen.getByText(/leaderboard/i)).toBeInTheDocument();
        expect(screen.getByText('testuser')).toBeInTheDocument();
        expect(screen.getByText('#1')).toBeInTheDocument();
      });
    });

    it('shows achievements and badges', async () => {
      renderWithProviders(<App />, { initialEntries: ['/profile'] });

      await waitFor(() => {
        expect(screen.getByText(/achievements/i)).toBeInTheDocument();
        expect(screen.getByText(/first steps/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling Flow', () => {
    it('handles network errors gracefully', async () => {
      // Mock network error
      server.use(
        rest.get(`${API_BASE_URL}/lessons`, (req, res, ctx) => {
          return res.networkError('Network error');
        })
      );

      renderWithProviders(<App />, { initialEntries: ['/lessons'] });

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    it('shows appropriate error messages for different error types', async () => {
      // Mock 404 error
      server.use(
        rest.get(`${API_BASE_URL}/lessons/999`, (req, res, ctx) => {
          return res(ctx.status(404), ctx.json({ message: 'Lesson not found' }));
        })
      );

      renderWithProviders(<App />, { initialEntries: ['/lessons/999'] });

      await waitFor(() => {
        expect(screen.getByText(/lesson not found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Mobile Responsiveness', () => {
    beforeEach(() => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      Object.defineProperty(window, 'innerHeight', {
        writable: true,
        configurable: true,
        value: 667,
      });
    });

    it('adapts navigation for mobile devices', async () => {
      renderWithProviders(<App />, { initialEntries: ['/'] });

      // Should show mobile menu button
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
      });
    });

    it('optimizes code editor for touch devices', async () => {
      const user = userEvent.setup();
      
      renderWithProviders(<App />, { initialEntries: ['/code-editor'] });

      await waitFor(() => {
        expect(screen.getByRole('textbox')).toBeInTheDocument();
      });

      // Should have touch-friendly controls
      expect(screen.getByText(/run/i)).toHaveClass('touch-friendly');
    });
  });
});