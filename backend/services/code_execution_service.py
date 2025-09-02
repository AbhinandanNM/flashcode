import asyncio
import json
import tempfile
import os
import subprocess
import time
from typing import Dict, Any, Optional
import requests
from fastapi import HTTPException
from config import settings


class CodeExecutionService:
    """Service for executing code using Judge0 API or local Docker sandbox"""
    
    # Language ID mappings for Judge0 API
    JUDGE0_LANGUAGE_IDS = {
        "python": 71,  # Python 3.8.1
        "cpp": 54,     # C++ (GCC 9.2.0)
    }
    
    # Docker image mappings for local execution
    DOCKER_IMAGES = {
        "python": "python:3.9-alpine",
        "cpp": "gcc:9"
    }
    
    def __init__(self):
        self.judge0_url = settings.judge0_api_url
        self.judge0_key = settings.judge0_api_key
        self.use_judge0 = bool(self.judge0_url)
    
    async def execute_code(
        self, 
        code: str, 
        language: str, 
        input_data: str = "", 
        expected_output: str = None
    ) -> Dict[str, Any]:
        """
        Execute code using Judge0 API or local Docker sandbox
        
        Args:
            code: Source code to execute
            language: Programming language (python, cpp)
            input_data: Input data for the program
            expected_output: Expected output for validation
            
        Returns:
            Dict containing execution results
        """
        if self.use_judge0:
            return await self._execute_with_judge0(code, language, input_data, expected_output)
        else:
            return await self._execute_with_docker(code, language, input_data, expected_output)
    
    async def _execute_with_judge0(
        self, 
        code: str, 
        language: str, 
        input_data: str, 
        expected_output: str = None
    ) -> Dict[str, Any]:
        """Execute code using Judge0 API"""
        try:
            language_id = self.JUDGE0_LANGUAGE_IDS.get(language)
            if not language_id:
                raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
            
            # Submit code for execution
            submission_data = {
                "source_code": code,
                "language_id": language_id,
                "stdin": input_data,
                "expected_output": expected_output
            }
            
            headers = {}
            if self.judge0_key:
                headers["X-RapidAPI-Key"] = self.judge0_key
                headers["X-RapidAPI-Host"] = "judge0-ce.p.rapidapi.com"
            
            # Submit the code
            submit_response = requests.post(
                f"{self.judge0_url}/submissions",
                json=submission_data,
                headers=headers,
                timeout=10
            )
            
            if submit_response.status_code != 201:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to submit code to Judge0"
                )
            
            submission = submit_response.json()
            token = submission["token"]
            
            # Poll for results with timeout
            max_attempts = 30  # 30 seconds timeout
            attempt = 0
            
            while attempt < max_attempts:
                result_response = requests.get(
                    f"{self.judge0_url}/submissions/{token}",
                    headers=headers,
                    timeout=10
                )
                
                if result_response.status_code != 200:
                    raise HTTPException(
                        status_code=500, 
                        detail="Failed to get execution results"
                    )
                
                result = result_response.json()
                
                # Check if execution is complete
                if result["status"]["id"] not in [1, 2]:  # Not "In Queue" or "Processing"
                    return self._format_judge0_result(result, expected_output)
                
                await asyncio.sleep(1)
                attempt += 1
            
            raise HTTPException(status_code=408, detail="Code execution timeout")
            
        except requests.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Judge0 API error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")
    
    async def _execute_with_docker(
        self, 
        code: str, 
        language: str, 
        input_data: str, 
        expected_output: str = None
    ) -> Dict[str, Any]:
        """Execute code using local Docker sandbox"""
        try:
            docker_image = self.DOCKER_IMAGES.get(language)
            if not docker_image:
                raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
            
            # Create temporary files
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write source code
                if language == "python":
                    code_file = os.path.join(temp_dir, "main.py")
                    run_command = ["python", "/code/main.py"]
                elif language == "cpp":
                    code_file = os.path.join(temp_dir, "main.cpp")
                    # For C++, we need to compile first
                    run_command = ["sh", "-c", "cd /code && g++ -o main main.cpp && ./main"]
                
                with open(code_file, "w") as f:
                    f.write(code)
                
                # Write input data
                input_file = os.path.join(temp_dir, "input.txt")
                with open(input_file, "w") as f:
                    f.write(input_data)
                
                # Run Docker container
                docker_cmd = [
                    "docker", "run",
                    "--rm",
                    "--network", "none",  # No network access
                    "--memory", "128m",   # Memory limit
                    "--cpus", "0.5",      # CPU limit
                    "--timeout", "10",    # 10 second timeout
                    "-v", f"{temp_dir}:/code:ro",  # Mount code directory as read-only
                    docker_image
                ] + run_command
                
                start_time = time.time()
                
                # Execute with timeout
                try:
                    process = await asyncio.create_subprocess_exec(
                        *docker_cmd,
                        stdin=asyncio.subprocess.PIPE,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(input=input_data.encode()),
                        timeout=15.0  # 15 second timeout
                    )
                    
                    execution_time = time.time() - start_time
                    
                    return self._format_docker_result(
                        stdout.decode(),
                        stderr.decode(),
                        process.returncode,
                        execution_time,
                        expected_output
                    )
                    
                except asyncio.TimeoutError:
                    return {
                        "status": "timeout",
                        "stdout": "",
                        "stderr": "Execution timeout (15 seconds)",
                        "execution_time": 15.0,
                        "is_correct": False,
                        "error": "Time limit exceeded"
                    }
                
        except Exception as e:
            return {
                "status": "error",
                "stdout": "",
                "stderr": str(e),
                "execution_time": 0.0,
                "is_correct": False,
                "error": f"Execution error: {str(e)}"
            }
    
    def _format_judge0_result(self, result: Dict, expected_output: str = None) -> Dict[str, Any]:
        """Format Judge0 API result into standard format"""
        status_id = result["status"]["id"]
        
        # Map Judge0 status codes
        if status_id == 3:  # Accepted
            status = "success"
        elif status_id == 4:  # Wrong Answer
            status = "wrong_answer"
        elif status_id == 5:  # Time Limit Exceeded
            status = "timeout"
        elif status_id == 6:  # Compilation Error
            status = "compilation_error"
        elif status_id == 7:  # Runtime Error (SIGSEGV)
            status = "runtime_error"
        elif status_id == 8:  # Runtime Error (SIGXFSZ)
            status = "runtime_error"
        elif status_id == 9:  # Runtime Error (SIGFPE)
            status = "runtime_error"
        elif status_id == 10:  # Runtime Error (SIGABRT)
            status = "runtime_error"
        elif status_id == 11:  # Runtime Error (NZEC)
            status = "runtime_error"
        elif status_id == 12:  # Runtime Error (Other)
            status = "runtime_error"
        elif status_id == 13:  # Internal Error
            status = "error"
        elif status_id == 14:  # Exec Format Error
            status = "error"
        else:
            status = "error"
        
        stdout = result.get("stdout", "") or ""
        stderr = result.get("stderr", "") or ""
        compile_output = result.get("compile_output", "") or ""
        
        # Check if output matches expected
        is_correct = False
        if expected_output is not None and status == "success":
            is_correct = stdout.strip() == expected_output.strip()
        
        return {
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
            "compile_output": compile_output,
            "execution_time": float(result.get("time", 0) or 0),
            "memory": int(result.get("memory", 0) or 0),
            "is_correct": is_correct,
            "error": stderr or compile_output if status != "success" else None
        }
    
    def _format_docker_result(
        self, 
        stdout: str, 
        stderr: str, 
        return_code: int, 
        execution_time: float,
        expected_output: str = None
    ) -> Dict[str, Any]:
        """Format Docker execution result into standard format"""
        if return_code == 0:
            status = "success"
        elif return_code == 124:  # timeout return code
            status = "timeout"
        else:
            status = "runtime_error"
        
        # Check if output matches expected
        is_correct = False
        if expected_output is not None and status == "success":
            is_correct = stdout.strip() == expected_output.strip()
        
        return {
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
            "execution_time": execution_time,
            "is_correct": is_correct,
            "error": stderr if status != "success" else None
        }


# Global instance
code_execution_service = CodeExecutionService()