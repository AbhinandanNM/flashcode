#!/usr/bin/env python3
"""
Production data setup script for CodeCrafts MVP
Creates initial data, admin users, and sample content for production deployment
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Lesson, Question
from auth import get_password_hash
import json
from datetime import datetime

def get_database_url():
    """Get database URL from environment variables"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://codecrafts:password@localhost:5432/codecrafts_prod"
    )

def create_admin_user(session):
    """Create admin user if it doesn't exist"""
    admin_email = os.getenv("ADMIN_EMAIL", "admin@codecrafts.app")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
    
    # Check if admin user already exists
    existing_admin = session.query(User).filter(User.email == admin_email).first()
    if existing_admin:
        print(f"Admin user {admin_email} already exists")
        return existing_admin
    
    # Create admin user
    admin_user = User(
        username="admin",
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        is_active=True,
        is_admin=True,
        total_xp=0,
        level=1,
        streak=0
    )
    
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)
    
    print(f"Created admin user: {admin_email}")
    return admin_user

def create_sample_lessons(session):
    """Create sample lessons for production"""
    
    # Check if lessons already exist
    existing_lessons = session.query(Lesson).count()
    if existing_lessons > 0:
        print(f"Found {existing_lessons} existing lessons, skipping sample creation")
        return
    
    sample_lessons = [
        {
            "title": "Python Basics: Variables and Data Types",
            "description": "Learn about Python variables, strings, numbers, and basic data types",
            "language": "python",
            "difficulty": 1,
            "xp_reward": 100,
            "estimated_time": 30,
            "content": {
                "theory": """
# Python Variables and Data Types

Python is a dynamically typed language, which means you don't need to declare variable types explicitly.

## Variables
Variables in Python are created when you assign a value to them:
```python
name = "Alice"
age = 25
height = 5.6
is_student = True
```

## Data Types
- **Strings**: Text data enclosed in quotes
- **Integers**: Whole numbers
- **Floats**: Decimal numbers
- **Booleans**: True or False values
                """,
                "examples": [
                    "name = 'CodeCrafts'",
                    "score = 100",
                    "average = 85.5",
                    "is_complete = False"
                ]
            }
        },
        {
            "title": "Python Control Flow: If Statements",
            "description": "Master conditional logic with if, elif, and else statements",
            "language": "python",
            "difficulty": 1,
            "xp_reward": 120,
            "estimated_time": 35,
            "content": {
                "theory": """
# Conditional Statements

Control the flow of your program with conditional statements.

## If Statements
```python
if condition:
    # code to execute if condition is True
    pass
elif another_condition:
    # code to execute if another_condition is True
    pass
else:
    # code to execute if no conditions are True
    pass
```

## Comparison Operators
- `==` equal to
- `!=` not equal to
- `<` less than
- `>` greater than
- `<=` less than or equal to
- `>=` greater than or equal to
                """,
                "examples": [
                    "if score >= 90:\n    grade = 'A'",
                    "if age >= 18:\n    print('Adult')\nelse:\n    print('Minor')",
                    "if x > 0 and x < 10:\n    print('Single digit')"
                ]
            }
        },
        {
            "title": "Python Loops: For and While",
            "description": "Learn to repeat code efficiently with for and while loops",
            "language": "python",
            "difficulty": 2,
            "xp_reward": 150,
            "estimated_time": 45,
            "content": {
                "theory": """
# Loops in Python

Loops allow you to repeat code multiple times.

## For Loops
Used to iterate over sequences:
```python
for item in sequence:
    # code to repeat
    pass
```

## While Loops
Repeat while a condition is True:
```python
while condition:
    # code to repeat
    # don't forget to update the condition!
    pass
```

## Range Function
Generate sequences of numbers:
```python
range(5)        # 0, 1, 2, 3, 4
range(1, 6)     # 1, 2, 3, 4, 5
range(0, 10, 2) # 0, 2, 4, 6, 8
```
                """,
                "examples": [
                    "for i in range(5):\n    print(i)",
                    "for name in ['Alice', 'Bob', 'Charlie']:\n    print(f'Hello, {name}!')",
                    "count = 0\nwhile count < 3:\n    print(count)\n    count += 1"
                ]
            }
        },
        {
            "title": "Python Functions: Define and Call",
            "description": "Create reusable code blocks with functions and parameters",
            "language": "python",
            "difficulty": 2,
            "xp_reward": 180,
            "estimated_time": 50,
            "content": {
                "theory": """
# Functions in Python

Functions are reusable blocks of code that perform specific tasks.

## Defining Functions
```python
def function_name(parameters):
    \"\"\"Optional docstring\"\"\"
    # function body
    return value  # optional
```

## Calling Functions
```python
result = function_name(arguments)
```

## Parameters and Arguments
- **Parameters**: Variables in the function definition
- **Arguments**: Values passed when calling the function

## Return Values
Functions can return values using the `return` statement.
                """,
                "examples": [
                    "def greet(name):\n    return f'Hello, {name}!'",
                    "def add(a, b):\n    return a + b",
                    "def calculate_area(length, width):\n    return length * width"
                ]
            }
        }
    ]
    
    created_lessons = []
    for lesson_data in sample_lessons:
        lesson = Lesson(**lesson_data)
        session.add(lesson)
        session.commit()
        session.refresh(lesson)
        created_lessons.append(lesson)
        print(f"Created lesson: {lesson.title}")
    
    return created_lessons

def create_sample_questions(session, lessons):
    """Create sample questions for the lessons"""
    
    # Check if questions already exist
    existing_questions = session.query(Question).count()
    if existing_questions > 0:
        print(f"Found {existing_questions} existing questions, skipping sample creation")
        return
    
    questions_data = [
        # Python Basics questions
        {
            "lesson_id": lessons[0].id,
            "type": "mcq",
            "difficulty": 1,
            "question": "Which of the following is the correct way to create a variable in Python?",
            "options": ["var name = 'Alice'", "name = 'Alice'", "string name = 'Alice'", "declare name = 'Alice'"],
            "correct_answer": "name = 'Alice'",
            "explanation": "In Python, variables are created by simply assigning a value using the = operator.",
            "xp_reward": 15
        },
        {
            "lesson_id": lessons[0].id,
            "type": "fill_blank",
            "difficulty": 1,
            "question": "Complete the code to create a variable 'age' with value 25: age ___ 25",
            "correct_answer": "=",
            "explanation": "The assignment operator = is used to assign values to variables in Python.",
            "xp_reward": 10
        },
        # If Statements questions
        {
            "lesson_id": lessons[1].id,
            "type": "mcq",
            "difficulty": 1,
            "question": "What will be printed by this code?\n```python\nscore = 85\nif score >= 80:\n    print('Great!')\nelse:\n    print('Good effort!')\n```",
            "options": ["Great!", "Good effort!", "Nothing", "Error"],
            "correct_answer": "Great!",
            "explanation": "Since score (85) is greater than or equal to 80, the condition is True and 'Great!' is printed.",
            "xp_reward": 15
        },
        # Loops questions
        {
            "lesson_id": lessons[2].id,
            "type": "code",
            "difficulty": 2,
            "question": "Write a for loop that prints numbers from 1 to 5 (inclusive).",
            "test_cases": [
                {"input": "", "expected_output": "1\n2\n3\n4\n5\n"}
            ],
            "solution": "for i in range(1, 6):\n    print(i)",
            "xp_reward": 25
        },
        # Functions questions
        {
            "lesson_id": lessons[3].id,
            "type": "code",
            "difficulty": 2,
            "question": "Write a function called 'multiply' that takes two parameters and returns their product.",
            "test_cases": [
                {"input": "3, 4", "expected_output": "12"},
                {"input": "5, 6", "expected_output": "30"},
                {"input": "2, 7", "expected_output": "14"}
            ],
            "solution": "def multiply(a, b):\n    return a * b",
            "xp_reward": 30
        }
    ]
    
    created_questions = []
    for question_data in questions_data:
        question = Question(**question_data)
        session.add(question)
        session.commit()
        session.refresh(question)
        created_questions.append(question)
        print(f"Created question for lesson {question.lesson_id}: {question.question[:50]}...")
    
    return created_questions

def setup_database_indexes(session):
    """Create database indexes for better performance"""
    try:
        # These would typically be handled by Alembic migrations
        # but we can ensure they exist here
        session.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        session.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);")
        session.execute("CREATE INDEX IF NOT EXISTS idx_lessons_language ON lessons(language);")
        session.execute("CREATE INDEX IF NOT EXISTS idx_lessons_difficulty ON lessons(difficulty);")
        session.execute("CREATE INDEX IF NOT EXISTS idx_questions_lesson_id ON questions(lesson_id);")
        session.execute("CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);")
        session.execute("CREATE INDEX IF NOT EXISTS idx_question_attempts_user_id ON question_attempts(user_id);")
        session.commit()
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes (they may already exist): {e}")
        session.rollback()

def main():
    """Main setup function"""
    print("Setting up production data for CodeCrafts...")
    
    # Create database connection
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = SessionLocal()
    
    try:
        # Setup database indexes
        setup_database_indexes(session)
        
        # Create admin user
        admin_user = create_admin_user(session)
        
        # Create sample lessons
        lessons = create_sample_lessons(session)
        
        # Create sample questions
        if lessons:
            questions = create_sample_questions(session, lessons)
            print(f"Created {len(questions)} sample questions")
        
        print("Production data setup completed successfully!")
        
    except Exception as e:
        print(f"Error during setup: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()