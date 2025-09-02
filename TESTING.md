# CodeCrafts MVP - Testing Documentation

This document provides comprehensive information about the testing strategy, setup, and execution for the CodeCrafts MVP application.

## Testing Strategy

Our testing approach follows the testing pyramid principle:

```
    /\
   /  \    E2E Tests (Few)
  /____\   
 /      \   Integration Tests (Some)
/__________\ Unit Tests (Many)
```

### Test Types

1. **Unit Tests**: Test individual components, functions, and services in isolation
2. **Integration Tests**: Test interactions between different parts of the system
3. **End-to-End Tests**: Test complete user workflows from frontend to backend
4. **API Tests**: Test REST API endpoints with various scenarios
5. **Database Tests**: Test data models, relationships, and database operations

## Frontend Testing

### Setup

The frontend uses Jest and React Testing Library for testing:

```bash
cd frontend
npm install
```

### Test Structure

```
frontend/src/
├── __tests__/              # End-to-end user flow tests
├── components/
│   └── **/__tests__/       # Component unit tests
├── hooks/
│   └── __tests__/          # Custom hook tests
├── services/
│   └── __tests__/          # Service layer tests
├── utils/
│   ├── testUtils.tsx       # Testing utilities and helpers
│   └── __tests__/          # Utility function tests
├── mocks/                  # Mock data and MSW handlers
│   ├── handlers.ts         # API mock handlers
│   └── server.ts           # MSW server setup
├── setupTests.ts           # Jest setup configuration
└── jest.config.js          # Jest configuration
```

### Running Frontend Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- ErrorBoundary.test.tsx

# Run tests in watch mode
npm test -- --watch

# Run comprehensive test suite
node run-tests.js
```

### Test Categories

#### 1. Component Tests
- **Error Boundary**: Tests error handling and recovery
- **Loading Spinner**: Tests loading states and variants
- **Error Display**: Tests error message display and dismissal
- **Form Components**: Tests form validation and user interactions

#### 2. Hook Tests
- **useApi**: Tests API integration, loading states, and error handling
- **useAuth**: Tests authentication state management
- **Custom Hooks**: Tests business logic in custom hooks

#### 3. Service Tests
- **API Services**: Tests service layer methods and error handling
- **Mock Integration**: Tests with MSW (Mock Service Worker)

#### 4. User Flow Tests
- **Authentication Flow**: Login, registration, logout
- **Learning Flow**: Browsing lessons, answering questions, tracking progress
- **Code Editor Flow**: Writing and executing code
- **Gamification Flow**: XP tracking, achievements, leaderboard

### Mock Service Worker (MSW)

We use MSW to mock API calls in tests:

```typescript
// Example mock handler
rest.get('/api/lessons', (req, res, ctx) => {
  return res(ctx.json(mockLessons));
});
```

### Test Utilities

The `testUtils.tsx` file provides:
- Custom render functions with providers
- Mock data generators
- Common test helpers
- User event simulation utilities

## Backend Testing

### Setup

The backend uses pytest for testing:

```bash
cd backend
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio
```

### Test Structure

```
backend/
├── test_*.py               # Test files
├── conftest.py             # Pytest configuration and fixtures
├── run_tests.py            # Comprehensive test runner
└── test_data/              # Test data files (if needed)
```

### Running Backend Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest test_auth.py

# Run specific test class
pytest test_auth.py::TestAuthEndpoints

# Run comprehensive test suite
python run_tests.py
```

### Test Categories

#### 1. API Endpoint Tests (`test_api_endpoints.py`)
- Authentication endpoints (login, register, user info)
- Lesson management endpoints
- Question and answer submission
- Code execution endpoints
- Gamification endpoints
- Duel system endpoints
- Error handling and validation

#### 2. Database Integration Tests (`test_database_integration.py`)
- Model creation and validation
- Relationships between models
- Data integrity constraints
- Query performance
- Service layer integration

#### 3. Service Layer Tests
- Business logic validation
- External service integration
- Error handling and recovery

#### 4. Model Tests (`test_models.py`)
- Database model validation
- Field constraints and defaults
- Model methods and properties

### Test Fixtures

Common fixtures in `conftest.py`:
- `db_session`: Fresh database session for each test
- `client`: FastAPI test client
- `authenticated_client`: Pre-authenticated test client
- Sample data fixtures for users, lessons, questions, etc.

### Database Testing

Tests use SQLite in-memory database for speed and isolation:

```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
```

Each test gets a fresh database to ensure isolation.

## Integration Testing

### Full Stack Integration

Integration tests verify the complete flow from frontend to backend:

1. **User Authentication**: Complete login/registration flow
2. **Lesson Completion**: From lesson selection to progress tracking
3. **Code Execution**: From code writing to result display
4. **Gamification**: XP awarding and achievement unlocking

### API Integration

Tests verify API contracts between frontend and backend:
- Request/response formats
- Error handling
- Authentication requirements
- Data validation

## Test Data Management

### Frontend Mock Data

Located in `frontend/src/mocks/handlers.ts`:
- Consistent mock responses
- Error scenario simulation
- Realistic data structures

### Backend Test Data

Generated through fixtures in `conftest.py`:
- Database seeding for tests
- Consistent test scenarios
- Cleanup after tests

## Coverage Requirements

### Minimum Coverage Targets

- **Frontend**: 80% line coverage
- **Backend**: 85% line coverage
- **Critical Paths**: 95% coverage (auth, payments, data integrity)

### Coverage Reports

```bash
# Frontend coverage
npm run test:coverage
open coverage/lcov-report/index.html

# Backend coverage
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd frontend && npm ci
      - name: Run tests
        run: cd frontend && npm run test:ci
      
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: cd backend && pip install -r requirements.txt
      - name: Run tests
        run: cd backend && python run_tests.py
```

## Performance Testing

### Database Performance

Tests in `test_database_integration.py::TestDatabasePerformance`:
- Query execution time limits
- Large dataset handling
- Index usage verification

### API Performance

- Response time assertions
- Concurrent request handling
- Memory usage monitoring

## Security Testing

### Authentication Security

- JWT token validation
- Password hashing verification
- Session management

### Input Validation

- SQL injection prevention
- XSS protection
- Input sanitization

### API Security

- Rate limiting (when implemented)
- CORS configuration
- Error message security

## Test Environment Setup

### Local Development

1. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm test
   ```

2. **Backend Setup**:
   ```bash
   cd backend
   pip install -r requirements.txt
   pytest
   ```

### Docker Testing

```bash
# Run tests in Docker environment
docker-compose -f docker-compose.test.yml up --build
```

## Debugging Tests

### Frontend Debugging

```bash
# Run tests in debug mode
npm test -- --verbose --no-coverage

# Debug specific test
npm test -- --testNamePattern="should handle login"
```

### Backend Debugging

```bash
# Run with verbose output
pytest -v -s

# Debug specific test
pytest -v -s test_auth.py::test_login_success

# Use pdb for debugging
pytest --pdb
```

## Best Practices

### Writing Tests

1. **Arrange, Act, Assert**: Structure tests clearly
2. **Descriptive Names**: Test names should describe the scenario
3. **Single Responsibility**: One assertion per test when possible
4. **Test Edge Cases**: Include error scenarios and boundary conditions
5. **Mock External Dependencies**: Isolate units under test

### Test Maintenance

1. **Keep Tests Fast**: Unit tests should run in milliseconds
2. **Avoid Test Dependencies**: Tests should be independent
3. **Regular Cleanup**: Remove obsolete tests
4. **Update with Code Changes**: Keep tests in sync with implementation

### Code Coverage

1. **Focus on Critical Paths**: Prioritize high-risk areas
2. **Quality over Quantity**: 100% coverage doesn't guarantee quality
3. **Test Behavior, Not Implementation**: Focus on what the code does
4. **Review Coverage Reports**: Identify untested code paths

## Troubleshooting

### Common Issues

1. **Test Timeouts**: Increase timeout for async operations
2. **Mock Issues**: Ensure mocks match actual API contracts
3. **Database Conflicts**: Use proper test isolation
4. **Environment Variables**: Set test-specific configurations

### Getting Help

1. Check test logs for detailed error messages
2. Review test documentation for specific test files
3. Use debugging tools (pdb for Python, debugger for JavaScript)
4. Verify test environment setup

## Future Enhancements

### Planned Improvements

1. **Visual Regression Testing**: Screenshot comparison for UI components
2. **Load Testing**: Performance testing under high load
3. **Accessibility Testing**: Automated a11y testing
4. **Cross-browser Testing**: Automated browser compatibility testing
5. **Mobile Testing**: Responsive design validation

### Test Automation

1. **Pre-commit Hooks**: Run tests before commits
2. **Automated Test Generation**: Generate tests from API schemas
3. **Test Data Management**: Automated test data generation
4. **Parallel Test Execution**: Speed up test suite execution

---

This testing documentation ensures comprehensive coverage of the CodeCrafts MVP application, providing confidence in code quality and system reliability.