#!/usr/bin/env python3
"""
Script to create sample Python Loops lesson content for the CodeCrafts MVP.
This demonstrates the complete learning flow from theory to practice.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models import Base, Lesson, Question

# Database configuration
DATABASE_URL = "sqlite+aiosqlite:///./codecrafts.db"

async def create_python_loops_lesson():
    """Create the Python Loops lesson with theory and practice questions."""
    
    # Create async engine and session
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Create the Python Loops lesson
        lesson = Lesson(
            language="python",
            title="Python Loops: For and While",
            theory="""# Python Loops: For and While

Loops are fundamental programming constructs that allow you to repeat code multiple times. Python provides two main types of loops: `for` loops and `while` loops.

## For Loops

For loops are used to iterate over sequences (like lists, strings, or ranges).

### Basic Syntax
```python
for item in sequence:
    # Code to execute for each item
    print(item)
```

### Examples

**Iterating over a list:**
```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(f"I like {fruit}")
```

**Using range() function:**
```python
for i in range(5):
    print(f"Number: {i}")
# Prints numbers 0 through 4
```

**Range with start and stop:**
```python
for i in range(2, 8):
    print(i)
# Prints numbers 2 through 7
```

## While Loops

While loops continue executing as long as a condition is true.

### Basic Syntax
```python
while condition:
    # Code to execute while condition is true
    # Don't forget to update the condition!
```

### Examples

**Basic counting:**
```python
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1  # Important: update the counter!
```

**User input loop:**
```python
user_input = ""
while user_input != "quit":
    user_input = input("Enter 'quit' to exit: ")
    print(f"You entered: {user_input}")
```

## Loop Control Statements

### Break Statement
The `break` statement exits the loop immediately:
```python
for i in range(10):
    if i == 5:
        break
    print(i)
# Prints 0, 1, 2, 3, 4
```

### Continue Statement
The `continue` statement skips the rest of the current iteration:
```python
for i in range(5):
    if i == 2:
        continue
    print(i)
# Prints 0, 1, 3, 4 (skips 2)
```

## Best Practices

1. **Use for loops** when you know how many times to iterate
2. **Use while loops** when the number of iterations depends on a condition
3. **Always ensure while loops have a way to terminate** to avoid infinite loops
4. **Use meaningful variable names** in your loops
5. **Consider using enumerate()** when you need both index and value

### Enumerate Example
```python
fruits = ["apple", "banana", "cherry"]
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")
```

Now you're ready to practice with loops! Remember: loops are powerful tools for automating repetitive tasks in your programs.""",
            difficulty=2,  # Easy-Medium level
            xp_reward=100,
            order_index=1,
            is_published=True,
            created_at=datetime.utcnow()
        )
        
        session.add(lesson)
        await session.flush()  # Get the lesson ID
        
        # Create practice questions for the lesson
        questions = [
            # MCQ Question 1
            Question(
                lesson_id=lesson.id,
                type="mcq",
                question_text="Which loop is best for iterating over a list of items?",
                options=["for loop", "while loop", "do-while loop", "foreach loop"],
                correct_answer="for loop",
                explanation="For loops are specifically designed for iterating over sequences like lists, making them the best choice for this task.",
                difficulty=1,
                xp_reward=25
            ),
            
            # MCQ Question 2
            Question(
                lesson_id=lesson.id,
                type="mcq",
                question_text="What does range(3, 8) generate?",
                options=["Numbers 3, 4, 5, 6, 7", "Numbers 3, 4, 5, 6, 7, 8", "Numbers 4, 5, 6, 7", "Numbers 3, 8"],
                correct_answer="Numbers 3, 4, 5, 6, 7",
                explanation="range(3, 8) generates numbers from 3 (inclusive) to 8 (exclusive), so it produces 3, 4, 5, 6, 7.",
                difficulty=2,
                xp_reward=30
            ),
            
            # Fill-in-the-blank Question 1
            Question(
                lesson_id=lesson.id,
                type="fill_blank",
                question_text="Complete the code to print numbers 0 to 4:\nfor i in _____:\n    print(i)",
                correct_answer='["range(5)"]',
                explanation="range(5) generates numbers from 0 to 4 (5 is exclusive).",
                difficulty=1,
                xp_reward=25
            ),
            
            # Fill-in-the-blank Question 2
            Question(
                lesson_id=lesson.id,
                type="fill_blank",
                question_text="Complete the while loop to count from 1 to 5:\ncount = 1\nwhile count _____ 5:\n    print(count)\n    count _____ 1",
                correct_answer='["<=", "+="]',
                explanation="Use '<=' to include 5 in the count, and '+= 1' to increment the counter.",
                difficulty=2,
                xp_reward=35
            ),
            
            # Flashcard Question 1
            Question(
                lesson_id=lesson.id,
                type="flashcard",
                question_text="What is the purpose of the 'break' statement in loops?",
                correct_answer="The 'break' statement immediately exits the loop, stopping all further iterations.",
                explanation="Break is used to terminate a loop early when a certain condition is met.",
                difficulty=2,
                xp_reward=20
            ),
            
            # Flashcard Question 2
            Question(
                lesson_id=lesson.id,
                type="flashcard",
                question_text="What's the difference between 'break' and 'continue' statements?",
                correct_answer="'break' exits the entire loop, while 'continue' skips only the current iteration and moves to the next one.",
                explanation="Both are loop control statements but with different behaviors - break terminates, continue skips.",
                difficulty=3,
                xp_reward=30
            ),
            
            # Code Challenge 1
            Question(
                lesson_id=lesson.id,
                type="code",
                question_text="Write a Python function that uses a for loop to calculate the sum of all numbers from 1 to n (inclusive). The function should be named 'sum_numbers' and take one parameter 'n'.",
                correct_answer="""def sum_numbers(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total""",
                explanation="This function uses a for loop with range(1, n+1) to iterate from 1 to n inclusive, adding each number to the total.",
                difficulty=2,
                xp_reward=50
            ),
            
            # Code Challenge 2
            Question(
                lesson_id=lesson.id,
                type="code",
                question_text="Write a Python function called 'count_vowels' that takes a string as input and uses a for loop to count how many vowels (a, e, i, o, u) it contains. Return the count.",
                correct_answer="""def count_vowels(text):
    vowels = "aeiouAEIOU"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count""",
                explanation="This function iterates through each character in the string and checks if it's a vowel, incrementing the counter when found.",
                difficulty=3,
                xp_reward=60
            ),
            
            # Code Challenge 3
            Question(
                lesson_id=lesson.id,
                type="code",
                question_text="Write a Python function called 'find_first_even' that takes a list of numbers and uses a while loop to find and return the first even number. If no even number is found, return None.",
                correct_answer="""def find_first_even(numbers):
    i = 0
    while i < len(numbers):
        if numbers[i] % 2 == 0:
            return numbers[i]
        i += 1
    return None""",
                explanation="This function uses a while loop to iterate through the list, checking each number for evenness using the modulo operator.",
                difficulty=3,
                xp_reward=70
            ),
            
            # Advanced Code Challenge
            Question(
                lesson_id=lesson.id,
                type="code",
                question_text="Write a Python function called 'print_pattern' that takes a number n and uses nested loops to print a triangle pattern. For n=3, it should print:\n*\n**\n***",
                correct_answer="""def print_pattern(n):
    for i in range(1, n + 1):
        for j in range(i):
            print("*", end="")
        print()""",
                explanation="This uses nested for loops - the outer loop controls rows, the inner loop prints stars for each row.",
                difficulty=4,
                xp_reward=80
            )
        ]
        
        # Add all questions to the session
        for question in questions:
            session.add(question)
        
        # Commit all changes
        await session.commit()
        
        print(f"✅ Successfully created Python Loops lesson with {len(questions)} questions!")
        print(f"📚 Lesson ID: {lesson.id}")
        print(f"🎯 Total XP available: {lesson.xp_reward + sum(q.xp_reward for q in questions)}")
        
        # Print summary
        question_types = {}
        for question in questions:
            question_types[question.type] = question_types.get(question.type, 0) + 1
        
        print("\n📊 Question breakdown:")
        for q_type, count in question_types.items():
            print(f"  - {q_type}: {count} questions")

async def main():
    """Main function to run the lesson creation."""
    try:
        await create_python_loops_lesson()
        print("\n🎉 Python Loops lesson created successfully!")
        print("You can now test the complete learning flow in the application.")
    except Exception as e:
        print(f"❌ Error creating lesson: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())