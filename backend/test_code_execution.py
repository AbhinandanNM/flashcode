import pytest
import asyncio
import uuid
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import Base, get_db
from models import User, Question, Lesson, QuestionAttempt, LanguageEnum, QuestionTypeEnum
from middleware import get_current_active_user
from services.code_execution_service import CodeExecutionService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_code_execution.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Test user for authentication
test_user = None

def override_get_current_user():
    return test_user

app.dependency_overrides[get_current_active_user] = override_get_current_user


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Set up and tear down database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def setup_test_data(db_session):
    """Set up test data"""
    global test_user
    
    # Generate unique username to avoid conflicts
    unique_id = str(uuid.uuid4())[:8]
    
    # Create test user
    test_user = User(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        password_hash="hashed_password",
        xp=100
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    # Create test lesson
    lesson = Lesson(
        language=LanguageEnum.PYTHON,
        title="Test Lesson",
        theory="Test theory",
        difficulty=1,
        xp_reward=10,
        order_index=1
    )
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(lesson)
    
    # Create test code question
    question = Question(
        lesson_id=lesson.id,
        type=QuestionTypeEnum.CODE,
        question_text="Write a function that returns 'Hello, World!'",
        correct_answer="Hello, World!",
        explanation="This is a simple hello world function",
        difficulty=1,
        xp_reward=5
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    
    return {
        "user": test_user,
        "lesson": lesson,
        "question": question
    }


class TestCodeExecutionService:
    """Test the CodeExecutionService class"""
    
    def test_init_with_judge0(self):
        """Test service initialization with Judge0 configuration"""
        with patch('services.code_execution_service.settings') as mock_settings:
            mock_settings.judge0_api_url = "https://api.judge0.com"
            mock_settings.judge0_api_key = "test_key"
            
            service = CodeExecutionService()
            assert service.use_judge0 is True
            assert service.judge0_url == "https://api.judge0.com"
            assert service.judge0_key == "test_key"
    
    def test_init_without_judge0(self):
        """Test service initialization without Judge0 configuration"""
        with patch('services.code_execution_service.settings') as mock_settings:
            mock_settings.judge0_api_url = None
            mock_settings.judge0_api_key = None
            
            service = CodeExecutionService()
            assert service.use_judge0 is False
    
    @pytest.mark.asyncio
    async def test_execute_code_with_judge0_success(self):
        """Test successful code execution with Judge0"""
        service = CodeExecutionService()
        service.use_judge0 = True
        service.judge0_url = "https://api.judge0.com"
        
        # Mock Judge0 API responses
        mock_submit_response = Mock()
        mock_submit_response.status_code = 201
        mock_submit_response.json.return_value = {"token": "test_token"}
        
        mock_result_response = Mock()
        mock_result_response.status_code = 200
        mock_result_response.json.return_value = {
            "status": {"id": 3},  # Accepted
            "stdout": "Hello, World!",
            "stderr": "",
            "time": "0.001",
            "memory": 1024
        }
        
        with patch('requests.post', return_value=mock_submit_response), \
             patch('requests.get', return_value=mock_result_response):
            
            result = await service.execute_code(
                code="print('Hello, World!')",
                language="python",
                expected_output="Hello, World!"
            )
            
            assert result["status"] == "success"
            assert result["stdout"] == "Hello, World!"
            assert result["is_correct"] is True
    
    @pytest.mark.asyncio
    async def test_execute_code_with_docker_success(self):
        """Test successful code execution with Docker"""
        service = CodeExecutionService()
        service.use_judge0 = False
        
        # Mock successful subprocess execution
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b"Hello, World!\n", b""))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', return_value=(b"Hello, World!\n", b"")), \
             patch('tempfile.TemporaryDirectory') as mock_tempdir:
            
            mock_tempdir.return_value.__enter__.return_value = "/tmp/test"
            
            with patch('builtins.open', create=True) as mock_open:
                result = await service.execute_code(
                    code="print('Hello, World!')",
                    language="python",
                    expected_output="Hello, World!"
                )
                
                assert result["status"] == "success"
                assert result["stdout"] == "Hello, World!\n"
                assert result["is_correct"] is True
    
    @pytest.mark.asyncio
    async def test_execute_code_timeout(self):
        """Test code execution timeout"""
        service = CodeExecutionService()
        service.use_judge0 = False
        
        with patch('asyncio.create_subprocess_exec'), \
             patch('asyncio.wait_for', side_effect=asyncio.TimeoutError), \
             patch('tempfile.TemporaryDirectory') as mock_tempdir:
            
            mock_tempdir.return_value.__enter__.return_value = "/tmp/test"
            
            with patch('builtins.open', create=True):
                result = await service.execute_code(
                    code="while True: pass",  # Infinite loop
                    language="python"
                )
                
                assert result["status"] == "timeout"
                assert "timeout" in result["stderr"].lower()
    
    @pytest.mark.asyncio
    async def test_execute_code_unsupported_language(self):
        """Test execution with unsupported language"""
        service = CodeExecutionService()
        
        with pytest.raises(Exception) as exc_info:
            await service.execute_code(
                code="console.log('Hello');",
                language="javascript"
            )
        
        assert "Unsupported language" in str(exc_info.value)


class TestCodeExecutionRoutes:
    """Test the code execution API routes"""
    
    def test_execute_code_endpoint(self, setup_test_data):
        """Test the /execute/run endpoint"""
        with patch('services.code_execution_service.code_execution_service.execute_code') as mock_execute:
            mock_execute.return_value = {
                "status": "success",
                "stdout": "Hello, World!",
                "stderr": "",
                "execution_time": 0.001,
                "is_correct": True,
                "error": None
            }
            
            response = client.post("/execute/run", json={
                "code": "print('Hello, World!')",
                "language": "python",
                "expected_output": "Hello, World!"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["stdout"] == "Hello, World!"
            assert data["is_correct"] is True
    
    def test_execute_code_invalid_language(self, setup_test_data):
        """Test code execution with invalid language"""
        response = client.post("/execute/run", json={
            "code": "console.log('Hello');",
            "language": "javascript"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_execute_code_empty_code(self, setup_test_data):
        """Test code execution with empty code"""
        response = client.post("/execute/run", json={
            "code": "",
            "language": "python"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_submit_code_solution_success(self, setup_test_data, db_session):
        """Test successful code solution submission"""
        test_data = setup_test_data
        
        with patch('services.code_execution_service.code_execution_service.execute_code') as mock_execute:
            mock_execute.return_value = {
                "status": "success",
                "stdout": "Hello, World!",
                "stderr": "",
                "execution_time": 0.001,
                "is_correct": True,
                "error": None
            }
            
            response = client.post("/execute/submit", json={
                "question_id": test_data["question"].id,
                "code": "print('Hello, World!')",
                "language": "python",
                "time_taken": 30
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_correct"] is True
            assert data["xp_awarded"] == 5  # Question XP reward
            
            # Verify attempt was saved
            attempt = db_session.query(QuestionAttempt).filter(
                QuestionAttempt.user_id == test_data["user"].id,
                QuestionAttempt.question_id == test_data["question"].id
            ).first()
            assert attempt is not None
            assert attempt.is_correct is True
            assert attempt.time_taken == 30
    
    def test_submit_code_solution_incorrect(self, setup_test_data, db_session):
        """Test incorrect code solution submission"""
        test_data = setup_test_data
        
        with patch('services.code_execution_service.code_execution_service.execute_code') as mock_execute:
            mock_execute.return_value = {
                "status": "success",
                "stdout": "Wrong output",
                "stderr": "",
                "execution_time": 0.001,
                "is_correct": False,
                "error": None
            }
            
            response = client.post("/execute/submit", json={
                "question_id": test_data["question"].id,
                "code": "print('Wrong output')",
                "language": "python",
                "time_taken": 45
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["is_correct"] is False
            assert data["xp_awarded"] == 0  # No XP for incorrect answer
            
            # Verify attempt was saved
            attempt = db_session.query(QuestionAttempt).filter(
                QuestionAttempt.user_id == test_data["user"].id,
                QuestionAttempt.question_id == test_data["question"].id
            ).first()
            assert attempt is not None
            assert attempt.is_correct is False
    
    def test_submit_code_nonexistent_question(self, setup_test_data):
        """Test code submission for nonexistent question"""
        response = client.post("/execute/submit", json={
            "question_id": 99999,
            "code": "print('Hello, World!')",
            "language": "python"
        })
        
        assert response.status_code == 404
    
    def test_submit_code_non_code_question(self, setup_test_data, db_session):
        """Test code submission for non-code question"""
        test_data = setup_test_data
        
        # Create MCQ question
        mcq_question = Question(
            lesson_id=test_data["lesson"].id,
            type=QuestionTypeEnum.MCQ,
            question_text="What is 2+2?",
            options={"a": "3", "b": "4", "c": "5"},
            correct_answer="b",
            difficulty=1,
            xp_reward=3
        )
        db_session.add(mcq_question)
        db_session.commit()
        
        response = client.post("/execute/submit", json={
            "question_id": mcq_question.id,
            "code": "print('Hello, World!')",
            "language": "python"
        })
        
        assert response.status_code == 400
        assert "only for code questions" in response.json()["detail"]
    
    def test_get_supported_languages(self, setup_test_data):
        """Test getting supported languages"""
        response = client.get("/execute/languages")
        
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) >= 2
        
        # Check for Python and C++
        language_ids = [lang["id"] for lang in data["languages"]]
        assert "python" in language_ids
        assert "cpp" in language_ids
    
    def test_get_execution_service_status(self, setup_test_data):
        """Test getting execution service status"""
        response = client.get("/execute/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "code_execution"
        assert data["status"] == "healthy"
        assert "judge0_enabled" in data
        assert "docker_fallback" in data
        assert "supported_languages" in data


class TestCodeExecutionValidation:
    """Test input validation for code execution"""
    
    def test_code_too_long(self, setup_test_data):
        """Test validation for code that's too long"""
        long_code = "print('Hello')\n" * 1000  # > 10KB
        
        response = client.post("/execute/run", json={
            "code": long_code,
            "language": "python"
        })
        
        assert response.status_code == 422
    
    def test_negative_time_taken(self, setup_test_data):
        """Test validation for negative time taken"""
        test_data = setup_test_data
        
        response = client.post("/execute/submit", json={
            "question_id": test_data["question"].id,
            "code": "print('Hello')",
            "language": "python",
            "time_taken": -5
        })
        
        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__])