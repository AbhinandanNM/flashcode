# Authentication Components

This directory contains React components related to user authentication and authorization.

## Components

### ProtectedRoute
A wrapper component that protects routes from unauthorized access. It checks if the user is authenticated and redirects to login if not.

**Usage:**
```tsx
<ProtectedRoute>
  <YourProtectedComponent />
</ProtectedRoute>
```

### UserProfile
Displays user profile information including XP, streak, join date, and last activity.

**Features:**
- Shows user avatar (first letter of username)
- Displays XP with star icon
- Shows current streak with fire icon
- Calculates and displays user level
- Formats join date and last activity

**Usage:**
```tsx
<UserProfile />
```

## Authentication Flow

1. User enters credentials on LoginPage or RegisterPage
2. AuthContext handles API calls to backend
3. JWT token is stored in localStorage
4. User profile is fetched and stored in context
5. ProtectedRoute components check authentication status
6. Navbar displays user info when authenticated

## API Integration

The authentication system integrates with the backend API:
- `POST /auth/login` - User login
- `POST /auth/register` - User registration  
- `GET /auth/profile` - Get user profile
- JWT tokens are automatically included in API requests

## Error Handling

- Form validation on client side
- API error messages displayed to user
- Automatic token validation on app load
- Graceful handling of expired tokens