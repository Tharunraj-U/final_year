"""
Code execution service for running and testing user code.
Supports Python, JavaScript, and Java.
"""

import sys
import io
import ast
import json
import os
import tempfile
import subprocess
from typing import Dict, List, Any
from contextlib import redirect_stdout, redirect_stderr


class CodeExecutor:
    """
    Safely executes user code and runs test cases.
    Supports Python, JavaScript, and Java.
    """
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
    
    def _is_stub_code_python(self, code: str, function_name: str) -> bool:
        """Check if Python code is just a stub (only contains pass, return None, etc.)"""
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    body = node.body
                    meaningful_statements = []
                    for stmt in body:
                        # Skip docstrings
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                            continue
                        # Skip pass statements
                        if isinstance(stmt, ast.Pass):
                            continue
                        # Skip 'return None' or bare 'return'
                        if isinstance(stmt, ast.Return) and (stmt.value is None or (isinstance(stmt.value, ast.Constant) and stmt.value.value is None)):
                            continue
                        meaningful_statements.append(stmt)
                    return len(meaningful_statements) == 0
            return False
        except:
            return False
    
    def _is_stub_code_js(self, code: str) -> bool:
        """Check if JavaScript code is just a stub."""
        # Remove comments and whitespace
        lines = []
        for line in code.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                lines.append(stripped)
        
        code_content = ' '.join(lines)
        
        # If the function body is essentially empty
        if '{' in code_content and '}' in code_content:
            # Extract content between first { and last }
            start = code_content.find('{')
            end = code_content.rfind('}')
            body = code_content[start+1:end].strip()
            if not body or body in ['return null;', 'return undefined;', 'return;', '']:
                return True
        
        return False
    
    def _is_stub_code_java(self, code: str) -> bool:
        """Check if Java code is just a stub."""
        # Check for return null pattern
        if 'return null;' in code and code.count('return') == 1:
            return True
        return False
    
    def _is_stub_code(self, code: str, function_name: str, language: str) -> bool:
        """Check if code is just a stub based on language."""
        if language == 'python':
            return self._is_stub_code_python(code, function_name)
        elif language == 'javascript':
            return self._is_stub_code_js(code)
        elif language == 'java':
            return self._is_stub_code_java(code)
        return False
    
    def execute_code(
        self,
        user_code: str,
        test_cases: List[Dict],
        function_name: str = "solution",
        language: str = "python"
    ) -> Dict:
        """
        Execute user code against test cases.
        
        Args:
            user_code: User's code
            test_cases: List of test cases with 'input' and 'expected' keys
            function_name: Name of the function to call
            language: Programming language (python, javascript, java)
        
        Returns:
            Execution results with pass/fail status
        """
        # Check for empty code
        if not user_code or not user_code.strip():
            return {
                'passed': False,
                'passed_count': 0,
                'total_count': len(test_cases),
                'test_results': [{'passed': False, 'error': 'No code provided'}],
                'error': 'Please write your solution before running.'
            }
        
        # Check if code is just a stub
        if self._is_stub_code(user_code, function_name, language):
            return {
                'passed': False,
                'passed_count': 0,
                'total_count': len(test_cases),
                'test_results': [{'passed': False, 'error': 'Function not implemented'}],
                'error': 'Please implement your solution. The function currently only contains a placeholder.'
            }
        
        # Route to appropriate executor
        if language == "python":
            return self._execute_python(user_code, test_cases, function_name)
        elif language == "javascript":
            return self._execute_javascript(user_code, test_cases, function_name)
        elif language == "java":
            return self._execute_java(user_code, test_cases, function_name)
        elif language == "cpp":
            return {
                'passed': False,
                'passed_count': 0,
                'total_count': len(test_cases),
                'test_results': [],
                'error': 'C++ execution is not available on this server. Please use Python, JavaScript, or Java.'
            }
        else:
            return {
                'passed': False,
                'passed_count': 0,
                'total_count': len(test_cases),
                'test_results': [],
                'error': f'Unsupported language: {language}'
            }
    
    def _execute_python(self, user_code: str, test_cases: List[Dict], function_name: str) -> Dict:
        """Execute Python code."""
        results = {
            'passed': False,
            'passed_count': 0,
            'total_count': len(test_cases),
            'test_results': [],
            'error': None,
            'output': ''
        }
        
        namespace = {}
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(user_code, namespace)
            
            if function_name not in namespace:
                callables = [k for k, v in namespace.items() 
                           if callable(v) and not k.startswith('_')]
                if callables:
                    function_name = callables[0]
                else:
                    results['error'] = "No function found. Please define a function."
                    return results
            
            user_function = namespace[function_name]
            
            for i, test in enumerate(test_cases):
                test_result = self._run_python_test(
                    user_function,
                    test.get('input', []),
                    test.get('expected')
                )
                test_result['test_number'] = i + 1
                results['test_results'].append(test_result)
                
                if test_result['passed']:
                    results['passed_count'] += 1
            
            results['passed'] = results['passed_count'] == results['total_count']
            results['output'] = stdout_capture.getvalue()
            
        except SyntaxError as e:
            results['error'] = f"Syntax Error: {e.msg} at line {e.lineno}"
        except Exception as e:
            results['error'] = f"Error: {str(e)}"
            results['output'] = stderr_capture.getvalue()
        
        return results
    
    def _run_python_test(self, func, inputs: Any, expected: Any) -> Dict:
        """Run a single Python test case."""
        result = {
            'passed': False,
            'input': inputs,
            'expected': expected,
            'actual': None,
            'error': None
        }
        
        try:
            if isinstance(inputs, list):
                actual = func(*inputs)
            elif isinstance(inputs, dict):
                actual = func(**inputs)
            else:
                actual = func(inputs)
            
            result['actual'] = actual
            
            if isinstance(expected, (list, set)):
                result['passed'] = (
                    actual == expected or
                    (isinstance(actual, (list, set)) and sorted(map(str, actual)) == sorted(map(str, expected)))
                )
            else:
                result['passed'] = actual == expected
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _execute_javascript(self, user_code: str, test_cases: List[Dict], function_name: str) -> Dict:
        """Execute JavaScript code using Node.js."""
        results = {
            'passed': False,
            'passed_count': 0,
            'total_count': len(test_cases),
            'test_results': [],
            'error': None,
            'output': ''
        }
        
        # Create test runner code
        test_runner = f"""
{user_code}

const testCases = {json.dumps(test_cases)};
const results = [];

for (let i = 0; i < testCases.length; i++) {{
    const test = testCases[i];
    const inputs = test.input || [];
    const expected = test.expected;
    
    try {{
        let actual;
        if (Array.isArray(inputs)) {{
            actual = {function_name}(...inputs);
        }} else {{
            actual = {function_name}(inputs);
        }}
        
        // Compare results
        let passed = false;
        if (Array.isArray(expected) && Array.isArray(actual)) {{
            passed = JSON.stringify(actual.sort()) === JSON.stringify(expected.sort()) ||
                     JSON.stringify(actual) === JSON.stringify(expected);
        }} else {{
            passed = actual === expected || JSON.stringify(actual) === JSON.stringify(expected);
        }}
        
        results.push({{
            test_number: i + 1,
            passed: passed,
            input: inputs,
            expected: expected,
            actual: actual,
            error: null
        }});
    }} catch (e) {{
        results.push({{
            test_number: i + 1,
            passed: false,
            input: inputs,
            expected: expected,
            actual: null,
            error: e.message
        }});
    }}
}}

console.log(JSON.stringify(results));
"""
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                f.write(test_runner)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip()
                    # Parse common JS errors
                    if 'SyntaxError' in error_msg:
                        results['error'] = f"JavaScript Syntax Error: {error_msg.split('SyntaxError:')[-1].strip()[:200]}"
                    elif 'ReferenceError' in error_msg:
                        results['error'] = f"JavaScript Reference Error: {error_msg.split('ReferenceError:')[-1].strip()[:200]}"
                    elif 'TypeError' in error_msg:
                        results['error'] = f"JavaScript Type Error: {error_msg.split('TypeError:')[-1].strip()[:200]}"
                    else:
                        results['error'] = f"JavaScript Error: {error_msg[:200]}"
                    return results
                
                # Parse test results
                output = result.stdout.strip()
                if output:
                    test_results = json.loads(output)
                    results['test_results'] = test_results
                    results['passed_count'] = sum(1 for t in test_results if t.get('passed'))
                    results['passed'] = results['passed_count'] == results['total_count']
                else:
                    results['error'] = "No output from JavaScript execution"
                
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass
                
        except subprocess.TimeoutExpired:
            results['error'] = "Time Limit Exceeded"
        except json.JSONDecodeError as e:
            results['error'] = f"Error parsing JavaScript output: {str(e)}"
        except FileNotFoundError:
            results['error'] = "Node.js is not installed on this server."
        except Exception as e:
            results['error'] = f"JavaScript execution error: {str(e)}"
        
        return results
    
    def _execute_java(self, user_code: str, test_cases: List[Dict], function_name: str) -> Dict:
        """Execute Java code."""
        results = {
            'passed': False,
            'passed_count': 0,
            'total_count': len(test_cases),
            'test_results': [],
            'error': None,
            'output': ''
        }
        
        # For Java, we need to compile and run the code
        # This is a simplified implementation that compiles and validates
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract class name from code
                import re
                class_match = re.search(r'class\s+(\w+)', user_code)
                if not class_match:
                    results['error'] = "Java code must contain a class definition"
                    return results
                
                class_name = class_match.group(1)
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                
                with open(java_file, 'w', encoding='utf-8') as f:
                    f.write(user_code)
                
                # Compile
                compile_result = subprocess.run(
                    ['javac', java_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=temp_dir
                )
                
                if compile_result.returncode != 0:
                    error_msg = compile_result.stderr.strip()
                    results['error'] = f"Java Compilation Error: {error_msg[:300]}"
                    return results
                
                # For full execution, we'd need a test harness
                # For now, indicate successful compilation
                results['output'] = f"Java code compiled successfully!"
                results['error'] = "Note: Java test execution is limited. Compilation passed. AI will analyze your code upon submission."
                results['test_results'] = [
                    {'test_number': i+1, 'passed': False, 'error': 'Java execution limited - compilation OK'} 
                    for i in range(len(test_cases))
                ]
                
        except subprocess.TimeoutExpired:
            results['error'] = "Compilation Time Limit Exceeded"
        except FileNotFoundError:
            results['error'] = "Java compiler (javac) is not available on this server."
        except Exception as e:
            results['error'] = f"Java execution error: {str(e)}"
        
        return results
    
    def validate_code(self, code: str, language: str = "python") -> Dict:
        """Validate code syntax without executing."""
        if language == "python":
            try:
                compile(code, '<string>', 'exec')
                return {'valid': True, 'error': None}
            except SyntaxError as e:
                return {'valid': False, 'error': f"Syntax Error at line {e.lineno}: {e.msg}"}
        
        elif language == "javascript":
            # Use Node.js to check syntax
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                    f.write(code)
                    temp_file = f.name
                
                try:
                    result = subprocess.run(
                        ['node', '--check', temp_file],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode != 0:
                        return {'valid': False, 'error': result.stderr.strip()[:200]}
                    return {'valid': True, 'error': None}
                finally:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
            except:
                return {'valid': True, 'error': None}
        
        elif language == "java":
            if 'class' not in code:
                return {'valid': False, 'error': 'Java code must contain a class definition'}
            return {'valid': True, 'error': None}
        
        return {'valid': True, 'error': None}
