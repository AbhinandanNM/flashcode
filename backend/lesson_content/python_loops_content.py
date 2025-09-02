"""
Python Loops lesson content for CodeCrafts MVP.
This file contains the complete lesson structure with theory and questions.
"""

from datetime import datetime

# Lesson theory content
PYTHON_LOOPS_THEORY = """# Python Loops: For and While

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

Now you're ready to practice with loops! Remember: loops are powerful tools for automating repetitive tasks in your programs."""

# Lesson metadata
LESSON_DATA = {
    "language": "python",
    "title": "Python Loops: For and While",
    "theory": PYTHON_LOOPS_THEORY,
    "difficulty": 2,
    "xp_reward": 100,
    "order_index": 1,
    "is_published": True
}

# Question data
QUESTIONS_DATA = [
    # MCQ Questions
    {
        "type": "mcq",
        "question_text": "Which loop is best for iterating over a list of items?",
        "options": ["for loop", "while loop", "do-while loop", "foreach loop"],
        "correct_answer": "for loop",
        "explanation": "For loops are specifically designed for iterating over sequences like lists, making them the best choice for this task.",
        "difficulty": 1,
        "xp_reward": 25
    },
    {
        "type": "mcq",
        "question_text": "What does range(3, 8) generate?",
        "options": ["Numbers 3, 4, 5, 6, 7", "Numbers 3, 4, 5, 6, 7, 8", "Numbers 4, 5, 6, 7", "Numbers 3, 8"],
        "correct_answer": "Numbers 3, 4, 5, 6, 7",
        "explanation": "range(3, 8) generates numbers from 3 (inclusive) to 8 (exclusive), so it produces 3, 4, 5, 6, 7.",
        "difficulty": 2,
        "xp_reward": 30
    },
    {
        "type": "mcq",
        "question_text": "What happens when you use 'break' in a loop?",
        "options": ["Skips the current iteration", "Exits the entire loop", "Restarts the loop", "Pauses the loop"],
        "correct_answer": "Exits the entire loop",
        "explanation": "The 'break' statement immediately terminates the loop and continues with the code after the loop.",
        "difficulty": 2,
        "xp_reward": 25
    },
    
    # Fill-in-the-blank Questions
    {
        "type": "fill_blank",
        "question_text": "Complete the code to print numbers 0 to 4:\nfor i in _____:\n    print(i)",
        "correct_answer": '["range(5)"]',
        "explanation": "range(5) generates numbers from 0 to 4 (5 is exclusive).",
        "difficulty": 1,
        "xp_reward": 25
    },
    {
        "type": "fill_blank",
        "question_text": "Complete the while loop to count from 1 to 5:\ncount = 1\nwhile count _____ 5:\n    print(count)\n    count _____ 1",
        "correct_answer": '["<=", "+="]',
        "explanation": "Use '<=' to include 5 in the count, and '+= 1' to increment the counter.",
        "difficulty": 2,
        "xp_reward": 35
    },
    {
        "type": "fill_blank",
        "question_text": "Fill in the blanks to iterate over a list with indices:\nfruits = ['apple', 'banana']\nfor _____, fruit in _____(fruits):\n    print(f'{_____}: {fruit}')",
        "correct_answer": '["index", "enumerate", "index"]',
        "explanation": "enumerate() returns both the index and value for each item in the list.",
        "difficulty": 3,
        "xp_reward": 40
    },
    
    # Flashcard Questions
    {
        "type": "flashcard",
        "question_text": "What is the purpose of the 'break' statement in loops?",
        "correct_answer": "The 'break' statement immediately exits the loop, stopping all further iterations.",
        "explanation": "Break is used to terminate a loop early when a certain condition is met.",
        "difficulty": 2,
        "xp_reward": 20
    },
    {
        "type": "flashcard",
        "question_text": "What's the difference between 'break' and 'continue' statements?",
        "correct_answer": "'break' exits the entire loop, while 'continue' skips only the current iteration and moves to the next one.",
        "explanation": "Both are loop control statements but with different behaviors - break terminates, continue skips.",
        "difficulty": 3,
        "xp_reward": 30
    },
    {
        "type": "flashcard",
        "question_text": "When should you use a 'for' loop vs a 'while' loop?",
        "correct_answer": "Use 'for' loops when you know the number of iterations or are iterating over a sequence. Use 'while' loops when the number of iterations depends on a condition.",
        "explanation": "For loops are great for definite iteration, while loops are better for indefinite iteration based on conditions.",
        "difficulty": 2,
        "xp_reward": 25
    },
    
    # Code Challenges
    {
        "type": "code",
        "question_text": "Write a Python function that uses a for loop to calculate the sum of all numbers from 1 to n (inclusive). The function should be named 'sum_numbers' and take one parameter 'n'.",
        "correct_answer": """def sum_numbers(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total""",
        "explanation": "This function uses a for loop with range(1, n+1) to iterate from 1 to n inclusive, adding each number to the total.",
        "difficulty": 2,
        "xp_reward": 50
    },
    {
        "type": "code",
        "question_text": "Write a Python function called 'count_vowels' that takes a string as input and uses a for loop to count how many vowels (a, e, i, o, u) it contains. Return the count.",
        "correct_answer": """def count_vowels(text):
    vowels = "aeiouAEIOU"
    count = 0
    for char in text:
        if char in vowels:
            count += 1
    return count""",
        "explanation": "This function iterates through each character in the string and checks if it's a vowel, incrementing the counter when found.",
        "difficulty": 3,
        "xp_reward": 60
    },
    {
        "type": "code",
        "question_text": "Write a Python function called 'find_first_even' that takes a list of numbers and uses a while loop to find and return the first even number. If no even number is found, return None.",
        "correct_answer": """def find_first_even(numbers):
    i = 0
    while i < len(numbers):
        if numbers[i] % 2 == 0:
            return numbers[i]
        i += 1
    return None""",
        "explanation": "This function uses a while loop to iterate through the list, checking each number for evenness using the modulo operator.",
        "difficulty": 3,
        "xp_reward": 70
    },
    {
        "type": "code",
        "question_text": "Write a Python function called 'print_multiplication_table' that takes a number n and uses nested loops to print its multiplication table from 1 to 10.",
        "correct_answer": """def print_multiplication_table(n):
    for i in range(1, 11):
        result = n * i
        print(f"{n} x {i} = {result}")""",
        "explanation": "This function uses a for loop to iterate from 1 to 10, calculating and printing each multiplication result.",
        "difficulty": 3,
        "xp_reward": 65
    },
    {
        "type": "code",
        "question_text": "Write a Python function called 'print_pattern' that takes a number n and uses nested loops to print a triangle pattern. For n=3, it should print:\n*\n**\n***",
        "correct_answer": """def print_pattern(n):
    for i in range(1, n + 1):
        for j in range(i):
            print("*", end="")
        print()""",
        "explanation": "This uses nested for loops - the outer loop controls rows, the inner loop prints stars for each row.",
        "difficulty": 4,
        "xp_reward": 80
    }
]

# Summary statistics
def get_lesson_summary():
    """Get a summary of the lesson content."""
    question_types = {}
    total_xp = LESSON_DATA["xp_reward"]
    
    for question in QUESTIONS_DATA:
        q_type = question["type"]
        question_types[q_type] = question_types.get(q_type, 0) + 1
        total_xp += question["xp_reward"]
    
    return {
        "lesson_title": LESSON_DATA["title"],
        "total_questions": len(QUESTIONS_DATA),
        "question_types": question_types,
        "total_xp": total_xp,
        "difficulty_range": f"{min(q['difficulty'] for q in QUESTIONS_DATA)}-{max(q['difficulty'] for q in QUESTIONS_DATA)}"
    }

if __name__ == "__main__":
    # Print lesson summary when run directly
    summary = get_lesson_summary()
    print("📚 Python Loops Lesson Summary")
    print("=" * 40)
    print(f"Title: {summary['lesson_title']}")
    print(f"Total Questions: {summary['total_questions']}")
    print(f"Total XP Available: {summary['total_xp']}")
    print(f"Difficulty Range: {summary['difficulty_range']}")
    print("\nQuestion Types:")
    for q_type, count in summary['question_types'].items():
        print(f"  - {q_type.upper()}: {count} questions")