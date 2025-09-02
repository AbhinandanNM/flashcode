# CodeCrafts Backend

This is the FastAPI backend for the CodeCrafts educational programming platform.

## Structure

- `main.py` - FastAPI application entry point
- `config.py` - Application configuration and settings
- `database.py` - Database connection and session management
- `models.py` - SQLAlchemy database models
- `alembic/` - Database migration files
- `init_db.py` - Database initialization script
- `test_models.py` - Model testing script

## Database Models

The backend implements the following models:

### User
- User authentication and profile information
- XP tracking and streak management
- Relationships to progress, attempts, and duels

### Lesson
- Programming lesson content and metadata
- Support for Python and C++ languages
- Difficulty levels and XP rewards

### Question
- Different question types: MCQ, fill-blank, flashcard, code
- Linked to lessons with difficulty and XP rewards
- JSON options for multiple choice questions

### Progress
- User progress tracking for lessons
- Spaced repetition scheduling
- Score and attempt tracking

### QuestionAttempt
- Individual question attempt records
- Correctness and timing tracking
- User answer storage

### Duel
- Competitive programming challenges
- Support for human and bot opponents
- Winner determination and status tracking

## Database Support

- **PostgreSQL**: Primary database for production (via Docker)
- **SQLite**: Fallback for development and testing
- **Alembic**: Database migrations and schema management

## Configuration

The application uses environment variables for configuration:

- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT token signing key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `JUDGE0_API_URL`: Code execution service URL
- `JUDGE0_API_KEY`: Code execution service API key

## Running

The backend is designed to run in Docker with the provided docker-compose.yml configuration:

```bash
docker-compose up backend
```

The API will be available at http://localhost:8000

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

Additional endpoints will be implemented in subsequent tasks.