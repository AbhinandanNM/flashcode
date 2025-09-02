"""
Code validation service for testing submitted code against expected outputs.
This service runs user code safely and compares results with test cases.
"""

import asyncio
import json
import sys
import io
import contextlib
import traceback
from typing import Dict, List, Any, Optional
from datetime import datetime

class CodeValidationResult:
    """Result of code validation including test case results."""
    
    def __init__(self):
        self.is_correct = False
        self.total_tests = 0
        self.passed_tests = 0
        self.test_results = []
        self.execution_error = None
        self.execution_time = 0
        self.output = ""
        
    def add_test_result(self, test_case: Dict, passed: bool, actual_output: str, error: str = None):
        """Add a test case result."""
        self.test_results.append({
            "description": test_case.get("description", f"Test {len(self.test_results) + 1}"),
            "input": test_case.get("input", ""),
            "expected": test_case.get("expected_output", ""),
            "actual": actual_output,
            "passed": passed,
            "error": error
        })
        
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            
        # Update overall correctness
        self.is_correct = self.passed_tests == self.total_tests and self.total_tests > 0

class CodeValidationService:
    """Service for validating submitted code against test cases."""
    
    def __init__(self):
        self.timeout_seconds = 5  # Maximum execution time
        
    async def validate_code(self, code: str, test_cases: List[Dict], language: str = "python") -> CodeValidationResult:
        """
        Validate submitted code against test cases.
        
        Args:
            code: The submitted code to validate
            test_cases: List of test cases with input and expected_output
            language: Programming language (currently only Python supported)
            
        Returns:
            CodeValidationResult with detailed test results
        """
        result = CodeValidationResult()
        start_time = datetime.now()
        
        try:
            if language.lower() != "python":
                result.execution_error = f"Language {language} not supported yet"
                return result
            
            # Basic syntax check
            try:
                compile(code, '<submitted_code>', 'exec')
            except SyntaxError as e:
                result.execution_error = f"Syntax Error: {str(e)}"
                return result
            
            # Run each test case
            for test_case in test_cases:
                test_result = await self._run_single_test(code, test_case)
                result.add_test_result(
                    test_case, 
                    test_result["passed"], 
                    test_result["output"], 
                    test_result.get("error")
                )
            
        except Exception as e:
            result.execution_error = f"Validation error: {str(e)}"
        
        # Calculate execution time
        end_time = datetime.now()
        result.execution_time = int((end_time - start_time).total_seconds() * 1000)
        
        return result
    
    async def _run_single_test(self, code: str, test_case: Dict) -> Dict:
        """Run a single test case against the code."""
        try:
            # Capture stdout
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Create a safe execution environment
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'range': range,
                    'int': int,
                    'float': float,
                    'str': str,
                    'list': list,
                    'dict': dict,
                    'tuple': tuple,
                    'set': set,
                    'bool': bool,
                    'abs': abs,
                    'max': max,
                    'min': min,
                    'sum': sum,
                    'sorted': sorted,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'any': any,
                    'all': all,
                }
            }
            
            # Execute the submitted code
            exec(code, safe_globals)
            
            # Parse test input and execute the function call
            test_input = test_case.get("input", "")
            expected_output = test_case.get("expected_output", "")
            
            # Try to execute the test
            if test_input:
                # If there's input, try to execute it as a function call
                try:
                    exec(f"result = {test_input}", safe_globals)
                    if 'result' in safe_globals:
                        # If function returns a value, print it
                        if safe_globals['result'] is not None:
                            print(safe_globals['result'])
                except:
                    # If direct execution fails, try calling the function
                    exec(test_input, safe_globals)
            else:
                # No input specified, just run the code
                pass
            
            # Get the captured output
            actual_output = captured_output.getvalue().strip()
            
            # Compare with expected output
            passed = actual_output == expected_output.strip()
            
            return {
                "passed": passed,
                "output": actual_output,
                "expected": expected_output
            }
            
        except Exception as e:
            return {
                "passed": False,
                "output": "",
                "error": str(e)
            }
        finally:
            # Restore stdout
            sys.stdout = old_stdout
    
    def _extract_function_name(self, code: str) -> Optional[str]:
        """Extract the main function name from the code."""
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('def '):
                # Extract function name
                func_def = line[4:].split('(')[0].strip()
                return func_def
        return None
    
    async def validate_with_custom_tests(self, code: str, custom_tests: List[str]) -> CodeValidationResult:
        """
        Validate code with custom test expressions.
        
        Args:
            code: The submitted code
            custom_tests: List of test expressions to evaluate
            
        Returns:
            CodeValidationResult
        """
        result = CodeValidationResult()
        
        try:
            # Execute the code in a safe environment
            safe_globals = {'__builtins__': __builtins__}
            exec(code, safe_globals)
            
            # Run each custom test
            for i, test_expr in enumerate(custom_tests):
                try:
                    test_result = eval(test_expr, safe_globals)
                    passed = bool(test_result)
                    
                    result.add_test_result(
                        {"description": f"Custom test {i+1}", "input": test_expr, "expected_output": "True"},
                        passed,
                        str(test_result)
                    )
                except Exception as e:
                    result.add_test_result(
                        {"description": f"Custom test {i+1}", "input": test_expr, "expected_output": "True"},
                        False,
                        "",
                        str(e)
                    )
                    
        except Exception as e:
            result.execution_error = str(e)
        
        return result

# Example usage and testing
async def test_validation_service():
    """Test the code validation service with sample challenges."""
    service = CodeValidationService()
    
    # Test 1: FizzBuzz challenge
    fizzbuzz_code = """def fizz_buzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)"""
    
    fizzbuzz_tests = [
        {
            "input": "fizz_buzz(5)",
            "expected_output": "1\n2\nFizz\n4\nBuzz",
            "description": "FizzBuzz for n=5"
        }
    ]
    
    print("🧪 Testing FizzBuzz validation...")
    result = await service.validate_code(fizzbuzz_code, fizzbuzz_tests)
    print(f"Result: {'✅ PASSED' if result.is_correct else '❌ FAILED'}")
    print(f"Tests: {result.passed_tests}/{result.total_tests}")
    
    if result.test_results:
        for test in result.test_results:
            status = "✅" if test["passed"] else "❌"
            print(f"  {status} {test['description']}")
            if not test["passed"]:
                print(f"    Expected: {repr(test['expected'])}")
                print(f"    Got: {repr(test['actual'])}")
    
    # Test 2: Incorrect code
    print("\n🧪 Testing incorrect code...")
    wrong_code = """def fizz_buzz(n):
    for i in range(1, n):  # Wrong range
        if i % 3 == 0:
            print("Fizz")
        else:
            print(i)"""
    
    result2 = await service.validate_code(wrong_code, fizzbuzz_tests)
    print(f"Result: {'✅ PASSED' if result2.is_correct else '❌ FAILED'}")
    print(f"Tests: {result2.passed_tests}/{result2.total_tests}")

if __name__ == "__main__":
    asyncio.run(test_validation_service())