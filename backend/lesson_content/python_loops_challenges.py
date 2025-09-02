"""
Advanced Python Loops code challenges for CodeCrafts MVP.
These challenges provide progressive difficulty with expected output validation.
"""

# Advanced code challenges with test cases
ADVANCED_CODE_CHALLENGES = [
    {
        "type": "code",
        "question_text": """Write a Python function called 'fizz_buzz' that takes a number n and prints the FizzBuzz sequence from 1 to n.

Rules:
- Print "Fizz" for multiples of 3
- Print "Buzz" for multiples of 5  
- Print "FizzBuzz" for multiples of both 3 and 5
- Print the number itself for all other cases

Example: fizz_buzz(15) should print:
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz""",
        "correct_answer": """def fizz_buzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)""",
        "explanation": "This classic programming challenge uses modulo operators to check divisibility and conditional logic to determine output.",
        "difficulty": 3,
        "xp_reward": 75,
        "test_cases": [
            {
                "input": "5",
                "expected_output": "1\n2\nFizz\n4\nBuzz",
                "description": "Basic FizzBuzz for n=5"
            },
            {
                "input": "15",
                "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz",
                "description": "FizzBuzz including FizzBuzz case"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Write a Python function called 'prime_numbers' that takes a number n and returns a list of all prime numbers from 2 to n (inclusive).

A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.

Example: prime_numbers(10) should return [2, 3, 5, 7]""",
        "correct_answer": """def prime_numbers(n):
    if n < 2:
        return []
    
    primes = []
    for num in range(2, n + 1):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    
    return primes""",
        "explanation": "This function uses nested loops to check each number for primality by testing divisibility up to its square root.",
        "difficulty": 4,
        "xp_reward": 90,
        "test_cases": [
            {
                "input": "10",
                "expected_output": "[2, 3, 5, 7]",
                "description": "Prime numbers up to 10"
            },
            {
                "input": "20",
                "expected_output": "[2, 3, 5, 7, 11, 13, 17, 19]",
                "description": "Prime numbers up to 20"
            },
            {
                "input": "1",
                "expected_output": "[]",
                "description": "No primes below 2"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Write a Python function called 'fibonacci_sequence' that takes a number n and returns the first n numbers in the Fibonacci sequence.

The Fibonacci sequence starts with 0 and 1, and each subsequent number is the sum of the two preceding ones.

Example: fibonacci_sequence(8) should return [0, 1, 1, 2, 3, 5, 8, 13]""",
        "correct_answer": """def fibonacci_sequence(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    
    return fib""",
        "explanation": "This function builds the Fibonacci sequence iteratively using a loop, which is more efficient than recursion.",
        "difficulty": 3,
        "xp_reward": 70,
        "test_cases": [
            {
                "input": "8",
                "expected_output": "[0, 1, 1, 2, 3, 5, 8, 13]",
                "description": "First 8 Fibonacci numbers"
            },
            {
                "input": "1",
                "expected_output": "[0]",
                "description": "Single Fibonacci number"
            },
            {
                "input": "0",
                "expected_output": "[]",
                "description": "Empty sequence for n=0"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Write a Python function called 'number_pyramid' that takes a number n and prints a pyramid pattern using numbers.

For n=4, it should print:
   1
  121
 12321
1234321

Each row contains numbers from 1 up to the row number, then back down to 1.""",
        "correct_answer": """def number_pyramid(n):
    for i in range(1, n + 1):
        # Print leading spaces
        for j in range(n - i):
            print(" ", end="")
        
        # Print ascending numbers
        for j in range(1, i + 1):
            print(j, end="")
        
        # Print descending numbers
        for j in range(i - 1, 0, -1):
            print(j, end="")
        
        print()  # New line after each row""",
        "explanation": "This function uses nested loops to create a symmetric number pyramid with proper spacing.",
        "difficulty": 4,
        "xp_reward": 85,
        "test_cases": [
            {
                "input": "3",
                "expected_output": "  1\n 121\n12321",
                "description": "3-row number pyramid"
            },
            {
                "input": "4",
                "expected_output": "   1\n  121\n 12321\n1234321",
                "description": "4-row number pyramid"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Write a Python function called 'word_frequency' that takes a string of text and returns a dictionary with the frequency of each word.

The function should:
- Convert text to lowercase
- Remove punctuation (.,!?;:)
- Split by spaces
- Count occurrences of each word

Example: word_frequency("Hello world! Hello Python.") should return {'hello': 2, 'world': 1, 'python': 1}""",
        "correct_answer": """def word_frequency(text):
    # Convert to lowercase and remove punctuation
    punctuation = ".,!?;:"
    for p in punctuation:
        text = text.replace(p, "")
    
    text = text.lower()
    words = text.split()
    
    # Count word frequencies
    frequency = {}
    for word in words:
        if word in frequency:
            frequency[word] += 1
        else:
            frequency[word] = 1
    
    return frequency""",
        "explanation": "This function processes text by cleaning it, splitting into words, and using a loop to count frequencies in a dictionary.",
        "difficulty": 3,
        "xp_reward": 80,
        "test_cases": [
            {
                "input": "\"Hello world! Hello Python.\"",
                "expected_output": "{'hello': 2, 'world': 1, 'python': 1}",
                "description": "Basic word frequency counting"
            },
            {
                "input": "\"Python is great. Python is fun!\"",
                "expected_output": "{'python': 2, 'is': 2, 'great': 1, 'fun': 1}",
                "description": "Multiple repeated words"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Write a Python function called 'matrix_spiral' that takes a 2D matrix (list of lists) and returns a list containing all elements in spiral order (clockwise from outside to inside).

Example: 
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
matrix_spiral(matrix) should return [1, 2, 3, 6, 9, 8, 7, 4, 5]""",
        "correct_answer": """def matrix_spiral(matrix):
    if not matrix or not matrix[0]:
        return []
    
    result = []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    
    while top <= bottom and left <= right:
        # Traverse right
        for col in range(left, right + 1):
            result.append(matrix[top][col])
        top += 1
        
        # Traverse down
        for row in range(top, bottom + 1):
            result.append(matrix[row][right])
        right -= 1
        
        # Traverse left (if we still have rows)
        if top <= bottom:
            for col in range(right, left - 1, -1):
                result.append(matrix[bottom][col])
            bottom -= 1
        
        # Traverse up (if we still have columns)
        if left <= right:
            for row in range(bottom, top - 1, -1):
                result.append(matrix[row][left])
            left += 1
    
    return result""",
        "explanation": "This advanced algorithm uses four loops to traverse the matrix in spiral order, adjusting boundaries after each direction.",
        "difficulty": 5,
        "xp_reward": 120,
        "test_cases": [
            {
                "input": "[[1, 2, 3], [4, 5, 6], [7, 8, 9]]",
                "expected_output": "[1, 2, 3, 6, 9, 8, 7, 4, 5]",
                "description": "3x3 matrix spiral"
            },
            {
                "input": "[[1, 2], [3, 4]]",
                "expected_output": "[1, 2, 4, 3]",
                "description": "2x2 matrix spiral"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Write a Python function called 'pascal_triangle' that takes a number n and returns the first n rows of Pascal's triangle as a list of lists.

Pascal's triangle: each number is the sum of the two numbers above it.
Row 0: [1]
Row 1: [1, 1]  
Row 2: [1, 2, 1]
Row 3: [1, 3, 3, 1]

Example: pascal_triangle(4) should return [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1]]""",
        "correct_answer": """def pascal_triangle(n):
    if n <= 0:
        return []
    
    triangle = []
    
    for i in range(n):
        row = [1]  # First element is always 1
        
        # Calculate middle elements
        if i > 0:
            for j in range(1, i):
                row.append(triangle[i-1][j-1] + triangle[i-1][j])
            row.append(1)  # Last element is always 1
        
        triangle.append(row)
    
    return triangle""",
        "explanation": "This function builds Pascal's triangle row by row, using the previous row to calculate each new row's values.",
        "difficulty": 4,
        "xp_reward": 95,
        "test_cases": [
            {
                "input": "4",
                "expected_output": "[[1], [1, 1], [1, 2, 1], [1, 3, 3, 1]]",
                "description": "First 4 rows of Pascal's triangle"
            },
            {
                "input": "1",
                "expected_output": "[[1]]",
                "description": "Single row Pascal's triangle"
            },
            {
                "input": "0",
                "expected_output": "[]",
                "description": "Empty triangle for n=0"
            }
        ]
    }
]

# Debugging exercises - common loop errors
DEBUGGING_CHALLENGES = [
    {
        "type": "code",
        "question_text": """Debug this code that should print numbers 1 to 5, but has an error:

```python
def print_numbers():
    i = 1
    while i <= 5:
        print(i)
        # Missing something here...
```

Fix the code so it prints 1, 2, 3, 4, 5 (each on a new line) and doesn't run forever.""",
        "correct_answer": """def print_numbers():
    i = 1
    while i <= 5:
        print(i)
        i += 1  # Increment i to avoid infinite loop""",
        "explanation": "The original code was missing the increment statement, causing an infinite loop. Always ensure while loop conditions can eventually become false.",
        "difficulty": 2,
        "xp_reward": 40,
        "test_cases": [
            {
                "input": "",
                "expected_output": "1\n2\n3\n4\n5",
                "description": "Print numbers 1 to 5"
            }
        ]
    },
    
    {
        "type": "code",
        "question_text": """Debug this code that should find the sum of even numbers from 1 to 10, but has logical errors:

```python
def sum_even_numbers():
    total = 0
    for i in range(1, 10):  # Error 1: range issue
        if i % 2 == 1:      # Error 2: wrong condition
            total += i
    return total
```

Fix the code to correctly sum even numbers from 1 to 10 (inclusive).""",
        "correct_answer": """def sum_even_numbers():
    total = 0
    for i in range(1, 11):  # Include 10 with range(1, 11)
        if i % 2 == 0:      # Check for even numbers (remainder 0)
            total += i
    return total""",
        "explanation": "Fixed two errors: range(1, 11) to include 10, and i % 2 == 0 to check for even numbers instead of odd.",
        "difficulty": 3,
        "xp_reward": 50,
        "test_cases": [
            {
                "input": "",
                "expected_output": "30",
                "description": "Sum of even numbers 2+4+6+8+10 = 30"
            }
        ]
    }
]

# Progressive difficulty exercises
PROGRESSIVE_EXERCISES = [
    {
        "title": "Beginner: Basic Counting",
        "type": "code",
        "question_text": "Write a function 'count_up' that takes a number n and prints all numbers from 1 to n.",
        "correct_answer": """def count_up(n):
    for i in range(1, n + 1):
        print(i)""",
        "difficulty": 1,
        "xp_reward": 30
    },
    
    {
        "title": "Intermediate: List Processing",
        "type": "code", 
        "question_text": "Write a function 'filter_positive' that takes a list of numbers and returns a new list containing only the positive numbers.",
        "correct_answer": """def filter_positive(numbers):
    positive = []
    for num in numbers:
        if num > 0:
            positive.append(num)
    return positive""",
        "difficulty": 2,
        "xp_reward": 45
    },
    
    {
        "title": "Advanced: Algorithm Implementation",
        "type": "code",
        "question_text": "Write a function 'binary_search' that takes a sorted list and a target value, returns the index of the target or -1 if not found.",
        "correct_answer": """def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1""",
        "difficulty": 4,
        "xp_reward": 100
    }
]

def get_all_challenges():
    """Get all code challenges combined."""
    return ADVANCED_CODE_CHALLENGES + DEBUGGING_CHALLENGES + PROGRESSIVE_EXERCISES

def get_challenges_summary():
    """Get summary statistics for all challenges."""
    all_challenges = get_all_challenges()
    
    total_xp = sum(challenge.get('xp_reward', 0) for challenge in all_challenges)
    difficulty_counts = {}
    
    for challenge in all_challenges:
        diff = challenge.get('difficulty', 1)
        difficulty_counts[diff] = difficulty_counts.get(diff, 0) + 1
    
    return {
        "total_challenges": len(all_challenges),
        "total_xp": total_xp,
        "difficulty_distribution": difficulty_counts,
        "categories": {
            "advanced": len(ADVANCED_CODE_CHALLENGES),
            "debugging": len(DEBUGGING_CHALLENGES), 
            "progressive": len(PROGRESSIVE_EXERCISES)
        }
    }

if __name__ == "__main__":
    summary = get_challenges_summary()
    print("🚀 Python Loops Code Challenges Summary")
    print("=" * 45)
    print(f"Total Challenges: {summary['total_challenges']}")
    print(f"Total XP Available: {summary['total_xp']}")
    print(f"\nCategories:")
    for category, count in summary['categories'].items():
        print(f"  - {category.title()}: {count} challenges")
    print(f"\nDifficulty Distribution:")
    for difficulty, count in sorted(summary['difficulty_distribution'].items()):
        level = ["", "Beginner", "Easy", "Medium", "Hard", "Expert"][difficulty]
        print(f"  - Level {difficulty} ({level}): {count} challenges")