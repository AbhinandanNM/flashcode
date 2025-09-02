"""
Demo script for code execution service
This demonstrates the code execution functionality without requiring Docker or Judge0
"""
import asyncio
from unittest.mock import patch, AsyncMock, Mock
from services.code_execution_service import CodeExecutionService


async def demo_judge0_execution():
    """Demo Judge0 API execution (mocked)"""
    print("=== Demo: Judge0 API Code Execution ===")
    
    service = CodeExecutionService()
    service.use_judge0 = True
    service.judge0_url = "https://api.judge0.com"
    
    # Mock Judge0 API responses
    mock_submit_response = Mock()
    mock_submit_response.status_code = 201
    mock_submit_response.json.return_value = {"token": "demo_token_123"}
    
    mock_result_response = Mock()
    mock_result_response.status_code = 200
    mock_result_response.json.return_value = {
        "status": {"id": 3},  # Accepted
        "stdout": "Hello, World!\n",
        "stderr": "",
        "time": "0.001",
        "memory": 1024
    }
    
    with patch('requests.post', return_value=mock_submit_response), \
         patch('requests.get', return_value=mock_result_response):
        
        print("Executing Python code: print('Hello, World!')")
        result = await service.execute_code(
            code="print('Hello, World!')",
            language="python",
            expected_output="Hello, World!"
        )
        
        print(f"Status: {result['status']}")
        print(f"Output: {result['stdout']}")
        print(f"Execution Time: {result['execution_time']}s")
        print(f"Is Correct: {result['is_correct']}")
        print()


async def demo_docker_execution():
    """Demo Docker execution (mocked)"""
    print("=== Demo: Docker Sandbox Code Execution ===")
    
    service = CodeExecutionService()
    service.use_judge0 = False
    
    # Mock successful subprocess execution
    mock_process = Mock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(b"Hello, World!\n", b""))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
         patch('asyncio.wait_for', return_value=(b"Hello, World!\n", b"")), \
         patch('tempfile.TemporaryDirectory') as mock_tempdir, \
         patch('builtins.open', create=True):
        
        mock_tempdir.return_value.__enter__.return_value = "/tmp/demo"
        
        print("Executing Python code: print('Hello, World!')")
        result = await service.execute_code(
            code="print('Hello, World!')",
            language="python",
            expected_output="Hello, World!"
        )
        
        print(f"Status: {result['status']}")
        print(f"Output: {result['stdout']}")
        print(f"Execution Time: {result['execution_time']:.3f}s")
        print(f"Is Correct: {result['is_correct']}")
        print()


async def demo_cpp_execution():
    """Demo C++ execution (mocked)"""
    print("=== Demo: C++ Code Execution ===")
    
    service = CodeExecutionService()
    service.use_judge0 = False
    
    # Mock successful C++ compilation and execution
    mock_process = Mock()
    mock_process.returncode = 0
    mock_process.communicate = AsyncMock(return_value=(b"Hello from C++!\n", b""))
    
    cpp_code = """
#include <iostream>
int main() {
    std::cout << "Hello from C++!" << std::endl;
    return 0;
}
"""
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
         patch('asyncio.wait_for', return_value=(b"Hello from C++!\n", b"")), \
         patch('tempfile.TemporaryDirectory') as mock_tempdir, \
         patch('builtins.open', create=True):
        
        mock_tempdir.return_value.__enter__.return_value = "/tmp/demo"
        
        print("Executing C++ code:")
        print(cpp_code)
        result = await service.execute_code(
            code=cpp_code,
            language="cpp",
            expected_output="Hello from C++!"
        )
        
        print(f"Status: {result['status']}")
        print(f"Output: {result['stdout']}")
        print(f"Execution Time: {result['execution_time']:.3f}s")
        print(f"Is Correct: {result['is_correct']}")
        print()


async def demo_error_handling():
    """Demo error handling"""
    print("=== Demo: Error Handling ===")
    
    service = CodeExecutionService()
    service.use_judge0 = False
    
    # Mock runtime error
    mock_process = Mock()
    mock_process.returncode = 1
    mock_process.communicate = AsyncMock(return_value=(b"", b"SyntaxError: invalid syntax\n"))
    
    with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
         patch('asyncio.wait_for', return_value=(b"", b"SyntaxError: invalid syntax\n")), \
         patch('tempfile.TemporaryDirectory') as mock_tempdir, \
         patch('builtins.open', create=True):
        
        mock_tempdir.return_value.__enter__.return_value = "/tmp/demo"
        
        print("Executing Python code with syntax error: print('Hello World'")
        result = await service.execute_code(
            code="print('Hello World'",  # Missing closing quote
            language="python"
        )
        
        print(f"Status: {result['status']}")
        print(f"Error: {result['error']}")
        print(f"Is Correct: {result['is_correct']}")
        print()


async def main():
    """Run all demos"""
    print("Code Execution Service Demo")
    print("=" * 50)
    print()
    
    await demo_judge0_execution()
    await demo_docker_execution()
    await demo_cpp_execution()
    await demo_error_handling()
    
    print("Demo completed successfully!")
    print("The code execution service supports:")
    print("- Judge0 API integration for cloud execution")
    print("- Docker sandbox fallback for local execution")
    print("- Python and C++ language support")
    print("- Comprehensive error handling and timeouts")
    print("- Security sandboxing with resource limits")


if __name__ == "__main__":
    asyncio.run(main())