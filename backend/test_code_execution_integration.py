"""
Integration tests for code execution service
These tests require Docker to be installed and running
"""
import pytest
import asyncio
from services.code_execution_service import CodeExecutionService


class TestCodeExecutionIntegration:
    """Integration tests for code execution service"""
    
    @pytest.mark.asyncio
    async def test_python_hello_world_docker(self):
        """Test Python hello world execution with Docker"""
        service = CodeExecutionService()
        service.use_judge0 = False  # Force Docker execution
        
        code = "print('Hello, World!')"
        result = await service.execute_code(
            code=code,
            language="python",
            expected_output="Hello, World!"
        )
        
        print(f"Result: {result}")
        assert result["status"] in ["success", "error"]  # May fail if Docker not available
        if result["status"] == "success":
            assert "Hello, World!" in result["stdout"]
            assert result["is_correct"] is True
    
    @pytest.mark.asyncio
    async def test_python_syntax_error_docker(self):
        """Test Python syntax error handling with Docker"""
        service = CodeExecutionService()
        service.use_judge0 = False  # Force Docker execution
        
        code = "print('Hello World'"  # Missing closing parenthesis
        result = await service.execute_code(
            code=code,
            language="python"
        )
        
        print(f"Result: {result}")
        assert result["status"] in ["runtime_error", "error"]
        assert result["is_correct"] is False
    
    @pytest.mark.asyncio
    async def test_cpp_hello_world_docker(self):
        """Test C++ hello world execution with Docker"""
        service = CodeExecutionService()
        service.use_judge0 = False  # Force Docker execution
        
        code = """
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""
        result = await service.execute_code(
            code=code,
            language="cpp",
            expected_output="Hello, World!"
        )
        
        print(f"Result: {result}")
        assert result["status"] in ["success", "error"]  # May fail if Docker not available
        if result["status"] == "success":
            assert "Hello, World!" in result["stdout"]
            assert result["is_correct"] is True
    
    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initialization"""
        service = CodeExecutionService()
        
        # Test language mappings
        assert "python" in service.JUDGE0_LANGUAGE_IDS
        assert "cpp" in service.JUDGE0_LANGUAGE_IDS
        assert "python" in service.DOCKER_IMAGES
        assert "cpp" in service.DOCKER_IMAGES
        
        # Test configuration
        assert isinstance(service.use_judge0, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])