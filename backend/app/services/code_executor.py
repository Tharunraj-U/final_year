"""
Code execution service for running and testing user code.
Supports Python, JavaScript, Java, C, and C++.
"""

import sys
import io
import ast
import json
import os
import tempfile
import subprocess
import re
from typing import Dict, List, Any
from contextlib import redirect_stdout, redirect_stderr


class CodeExecutor:
    """
    Safely executes user code and runs test cases.
    Supports Python, JavaScript, Java, C, and C++.
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
        if 'return null;' in code and code.count('return') == 1:
            return True
        return False
    
    def _is_stub_code_c_cpp(self, code: str) -> bool:
        """Check if C/C++ code is just a stub."""
        lines = [l.strip() for l in code.split('\n') if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('#')]
        body_lines = [l for l in lines if l not in ['{', '}', '};', 'return 0;', 'return NULL;', 'return nullptr;', '']]
        # If very few meaningful lines, it's likely a stub
        if len(body_lines) <= 3:
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
        elif language in ('c', 'cpp'):
            return self._is_stub_code_c_cpp(code)
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
            return self._execute_cpp(user_code, test_cases, function_name)
        elif language == "c":
            return self._execute_c(user_code, test_cases, function_name)
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
        """Execute Java code with full test case execution."""
        results = {
            'passed': False,
            'passed_count': 0,
            'total_count': len(test_cases),
            'test_results': [],
            'error': None,
            'output': ''
        }
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract class name from user code
                class_match = re.search(r'class\s+(\w+)', user_code)
                if not class_match:
                    results['error'] = "Java code must contain a class definition"
                    return results
                
                class_name = class_match.group(1)
                
                # Build a test runner class
                test_cases_json = json.dumps(test_cases).replace('\\', '\\\\').replace('"', '\\"')
                
                runner_code = f'''
import java.util.*;
import java.lang.reflect.*;
import org.json.simple.*;
import org.json.simple.parser.*;

{user_code}

public class TestRunner {{
    public static void main(String[] args) {{
        String testCasesJson = "{test_cases_json}";
        try {{
            JSONParser parser = new JSONParser();
            JSONArray tests = (JSONArray) parser.parse(testCasesJson);
            JSONArray results = new JSONArray();
            
            {class_name} solution = new {class_name}();
            
            for (int i = 0; i < tests.size(); i++) {{
                JSONObject test = (JSONObject) tests.get(i);
                JSONObject result = new JSONObject();
                result.put("test_number", (long)(i + 1));
                
                try {{
                    Object input = test.get("input");
                    Object expected = test.get("expected");
                    
                    // Find the solution method
                    Method method = null;
                    for (Method m : {class_name}.class.getDeclaredMethods()) {{
                        if (m.getName().equals("{function_name}")) {{
                            method = m;
                            break;
                        }}
                    }}
                    
                    if (method == null) {{
                        result.put("passed", false);
                        result.put("error", "Method {function_name} not found");
                        results.add(result);
                        continue;
                    }}
                    
                    Object actual = null;
                    if (input instanceof JSONArray) {{
                        JSONArray inputArr = (JSONArray) input;
                        Object[] params = new Object[inputArr.size()];
                        Class<?>[] paramTypes = method.getParameterTypes();
                        for (int j = 0; j < inputArr.size(); j++) {{
                            params[j] = convertParam(inputArr.get(j), paramTypes.length > j ? paramTypes[j] : Object.class);
                        }}
                        actual = method.invoke(solution, params);
                    }} else {{
                        actual = method.invoke(solution, convertParam(input, method.getParameterTypes()[0]));
                    }}
                    
                    boolean passed = compareResults(actual, expected);
                    result.put("passed", passed);
                    result.put("expected", String.valueOf(expected));
                    result.put("actual", String.valueOf(actual));
                    result.put("input", String.valueOf(input));
                    
                }} catch (Exception e) {{
                    result.put("passed", false);
                    result.put("error", e.getCause() != null ? e.getCause().getMessage() : e.getMessage());
                }}
                results.add(result);
            }}
            
            System.out.println(results.toJSONString());
            
        }} catch (Exception e) {{
            System.err.println("Runner error: " + e.getMessage());
            System.exit(1);
        }}
    }}
    
    static Object convertParam(Object val, Class<?> targetType) {{
        if (val == null) return null;
        if (val instanceof Long) {{
            long v = (Long) val;
            if (targetType == int.class || targetType == Integer.class) return (int) v;
            return v;
        }}
        if (val instanceof Double) {{
            double v = (Double) val;
            if (targetType == float.class || targetType == Float.class) return (float) v;
            return v;
        }}
        if (val instanceof JSONArray) {{
            JSONArray arr = (JSONArray) val;
            if (targetType == int[].class) {{
                int[] r = new int[arr.size()];
                for (int i = 0; i < arr.size(); i++) r[i] = ((Long) arr.get(i)).intValue();
                return r;
            }}
            if (targetType == String[].class) {{
                String[] r = new String[arr.size()];
                for (int i = 0; i < arr.size(); i++) r[i] = String.valueOf(arr.get(i));
                return r;
            }}
            List<Object> list = new ArrayList<>();
            for (Object o : arr) list.add(o);
            return list;
        }}
        if (val instanceof String && targetType == char.class) return ((String) val).charAt(0);
        return val;
    }}
    
    static boolean compareResults(Object actual, Object expected) {{
        if (actual == null && expected == null) return true;
        if (actual == null || expected == null) return false;
        // Number comparison
        if (actual instanceof Number && expected instanceof Number) {{
            return ((Number) actual).doubleValue() == ((Number) expected).doubleValue();
        }}
        // Array comparison
        if (actual instanceof int[]) {{
            if (expected instanceof JSONArray) {{
                int[] arr = (int[]) actual;
                JSONArray exp = (JSONArray) expected;
                if (arr.length != exp.size()) return false;
                for (int i = 0; i < arr.length; i++) {{
                    if (arr[i] != ((Long) exp.get(i)).intValue()) return false;
                }}
                return true;
            }}
        }}
        return String.valueOf(actual).equals(String.valueOf(expected));
    }}
}}
'''
                # Try simple approach first: compile user code with inline test runner using subprocess
                # Write user code as Solution.java
                solution_file = os.path.join(temp_dir, f"{class_name}.java")
                with open(solution_file, 'w', encoding='utf-8') as f:
                    f.write(user_code)
                
                # Compile user code
                compile_result = subprocess.run(
                    ['javac', solution_file],
                    capture_output=True, text=True,
                    timeout=self.timeout, cwd=temp_dir
                )
                
                if compile_result.returncode != 0:
                    error_msg = compile_result.stderr.strip()
                    results['error'] = f"Compilation Error: {error_msg[:300]}"
                    return results
                
                # Now run test cases via a simple subprocess approach
                # Build a minimal test script that calls the function
                self._run_java_tests_simple(results, user_code, test_cases, function_name, class_name, temp_dir)
                
        except subprocess.TimeoutExpired:
            results['error'] = "Time Limit Exceeded"
        except FileNotFoundError:
            results['error'] = "Java compiler (javac) is not available. Please install JDK."
        except Exception as e:
            results['error'] = f"Java execution error: {str(e)}"
        
        return results
    
    def _run_java_tests_simple(self, results: Dict, user_code: str, test_cases: List[Dict], 
                                function_name: str, class_name: str, temp_dir: str):
        """Run Java tests using a generated test runner."""
        # Generate a simple Main.java that calls the solution
        test_calls = []
        for i, tc in enumerate(test_cases):
            inp = tc.get('input', [])
            expected = tc.get('expected')
            if isinstance(inp, list):
                args_str = ', '.join(self._java_literal(a) for a in inp)
            else:
                args_str = self._java_literal(inp)
            
            test_calls.append(f'''
        try {{
            Object actual = sol.{function_name}({args_str});
            String actualStr = arrayToString(actual);
            String expectedStr = {json.dumps(json.dumps(expected))};
            boolean passed = compareResult(actualStr, expectedStr);
            System.out.println("RESULT:" + (i+1) + ":" + (passed ? "PASS" : "FAIL") + ":" + actualStr + ":" + expectedStr);
        }} catch (Exception e) {{
            System.out.println("RESULT:" + (i+1) + ":ERROR:" + e.getMessage() + ":_");
        }}'''.replace('(i+1)', str(i+1)))
        
        main_code = f'''
import java.util.*;

public class Main {{
    public static void main(String[] args) {{
        {class_name} sol = new {class_name}();
        {"".join(test_calls)}
    }}
    
    static String arrayToString(Object obj) {{
        if (obj == null) return "null";
        if (obj instanceof int[]) return Arrays.toString((int[]) obj);
        if (obj instanceof long[]) return Arrays.toString((long[]) obj);
        if (obj instanceof double[]) return Arrays.toString((double[]) obj);
        if (obj instanceof String[]) return Arrays.toString((String[]) obj);
        if (obj instanceof boolean[]) return Arrays.toString((boolean[]) obj);
        if (obj instanceof Object[]) return Arrays.deepToString((Object[]) obj);
        if (obj instanceof List) return obj.toString();
        return String.valueOf(obj);
    }}
    
    static boolean compareResult(String actual, String expected) {{
        if (actual == null || expected == null) return false;
        // Normalize for comparison
        String a = actual.trim().replaceAll("\\\\s+", "");
        String e = expected.trim().replaceAll("\\\\s+", "");
        if (a.equals(e)) return true;
        // Try numeric comparison
        try {{
            double av = Double.parseDouble(a);
            double ev = Double.parseDouble(e);
            return Math.abs(av - ev) < 1e-9;
        }} catch (NumberFormatException ex) {{}}
        return false;
    }}
}}
'''
        
        main_file = os.path.join(temp_dir, "Main.java")
        with open(main_file, 'w', encoding='utf-8') as f:
            f.write(main_code)
        
        # Compile Main.java
        compile_r = subprocess.run(
            ['javac', '-cp', temp_dir, main_file],
            capture_output=True, text=True,
            timeout=self.timeout, cwd=temp_dir
        )
        
        if compile_r.returncode != 0:
            results['error'] = f"Test Runner Compilation Error: {compile_r.stderr.strip()[:300]}"
            return
        
        # Run
        run_r = subprocess.run(
            ['java', '-cp', temp_dir, 'Main'],
            capture_output=True, text=True,
            timeout=self.timeout, cwd=temp_dir
        )
        
        if run_r.returncode != 0 and not run_r.stdout:
            results['error'] = f"Runtime Error: {run_r.stderr.strip()[:300]}"
            return
        
        # Parse results
        for line in run_r.stdout.strip().split('\n'):
            if line.startswith('RESULT:'):
                parts = line.split(':', 4)
                if len(parts) >= 5:
                    test_num = int(parts[1])
                    status = parts[2]
                    actual = parts[3]
                    expected = parts[4]
                    
                    passed = status == 'PASS'
                    test_result = {
                        'test_number': test_num,
                        'passed': passed,
                        'actual': actual,
                        'expected': expected,
                        'error': parts[3] if status == 'ERROR' else None
                    }
                    results['test_results'].append(test_result)
                    if passed:
                        results['passed_count'] += 1
        
        results['passed'] = results['passed_count'] == results['total_count']
    
    def _java_literal(self, value) -> str:
        """Convert a Python value to a Java literal string."""
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            if abs(value) > 2147483647:
                return f"{value}L"
            return str(value)
        if isinstance(value, float):
            return f"{value}"
        if isinstance(value, str):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        if isinstance(value, list):
            if all(isinstance(v, int) for v in value):
                return "new int[]{" + ", ".join(str(v) for v in value) + "}"
            if all(isinstance(v, str) for v in value):
                return "new String[]{" + ", ".join(f'"{v}"' for v in value) + "}"
            return "new Object[]{" + ", ".join(self._java_literal(v) for v in value) + "}"
        return str(value)
    
    def _execute_c(self, user_code: str, test_cases: List[Dict], function_name: str) -> Dict:
        """Execute C code with test case execution."""
        return self._execute_c_cpp_common(user_code, test_cases, function_name, language='c')
    
    def _execute_cpp(self, user_code: str, test_cases: List[Dict], function_name: str) -> Dict:
        """Execute C++ code with test case execution."""
        return self._execute_c_cpp_common(user_code, test_cases, function_name, language='cpp')
    
    def _execute_c_cpp_common(self, user_code: str, test_cases: List[Dict], function_name: str, language: str = 'cpp') -> Dict:
        """Execute C or C++ code with test cases."""
        results = {
            'passed': False,
            'passed_count': 0,
            'total_count': len(test_cases),
            'test_results': [],
            'error': None,
            'output': ''
        }
        
        is_cpp = language == 'cpp'
        ext = '.cpp' if is_cpp else '.c'
        compiler = 'g++' if is_cpp else 'gcc'
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Build test harness
                includes = '#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#include <math.h>\n'
                if is_cpp:
                    includes += '#include <iostream>\n#include <vector>\n#include <string>\n#include <algorithm>\n#include <map>\n#include <set>\n#include <unordered_map>\n#include <unordered_set>\n#include <stack>\n#include <queue>\n#include <climits>\nusing namespace std;\n'
                
                # Generate test calls
                test_calls = []
                for i, tc in enumerate(test_cases):
                    inp = tc.get('input', [])
                    expected = tc.get('expected')
                    
                    if isinstance(inp, list) and len(inp) > 0:
                        # Generate the function call with arguments
                        call_args, setup_code = self._c_cpp_build_args(inp, i, is_cpp)
                    else:
                        call_args = self._c_cpp_literal(inp, is_cpp)
                        setup_code = ""
                    
                    expected_str = json.dumps(expected) if not isinstance(expected, str) else expected
                    
                    test_calls.append(f'''
    {{
        {setup_code}
        // Test {i+1}
        auto result_{i} = {function_name}({call_args});
        char actual_buf[512];
        {self._c_cpp_sprint_result(f'result_{i}', expected, is_cpp)}
        const char* expected_str = {json.dumps(str(expected))};
        int passed = (strcmp(actual_buf, expected_str) == 0);
        printf("RESULT:{i+1}:%s:%s:%s\\n", passed ? "PASS" : "FAIL", actual_buf, expected_str);
    }}''') if is_cpp else test_calls.append(f'''
    {{
        {setup_code}
        /* Test {i+1} */
        char actual_buf[512];
        {self._c_generate_test(function_name, inp, expected, i)}
        char* expected_str = {json.dumps(str(expected))};
        int passed = (strcmp(actual_buf, expected_str) == 0);
        printf("RESULT:{i+1}:%s:%s:%s\\n", passed ? "PASS" : "FAIL", actual_buf, expected_str);
    }}''')
                
                full_code = f'''{includes}

{user_code}

int main() {{
    {"".join(test_calls)}
    return 0;
}}
'''
                
                source_file = os.path.join(temp_dir, f"solution{ext}")
                exe_file = os.path.join(temp_dir, "solution.exe" if os.name == 'nt' else "solution")
                
                with open(source_file, 'w', encoding='utf-8') as f:
                    f.write(full_code)
                
                # Compile
                compile_cmd = [compiler, source_file, '-o', exe_file]
                if is_cpp:
                    compile_cmd.insert(1, '-std=c++17')
                else:
                    compile_cmd.insert(1, '-std=c11')
                compile_cmd.append('-lm')  # Link math library
                
                compile_result = subprocess.run(
                    compile_cmd,
                    capture_output=True, text=True,
                    timeout=self.timeout, cwd=temp_dir
                )
                
                if compile_result.returncode != 0:
                    error_msg = compile_result.stderr.strip()
                    results['error'] = f"Compilation Error: {error_msg[:400]}"
                    return results
                
                # Run
                run_result = subprocess.run(
                    [exe_file],
                    capture_output=True, text=True,
                    timeout=self.timeout, cwd=temp_dir
                )
                
                if run_result.returncode != 0 and not run_result.stdout:
                    results['error'] = f"Runtime Error: {run_result.stderr.strip()[:300]}"
                    return results
                
                # Parse output
                for line in run_result.stdout.strip().split('\n'):
                    if line.startswith('RESULT:'):
                        parts = line.split(':', 4)
                        if len(parts) >= 5:
                            test_num = int(parts[1])
                            status = parts[2]
                            actual = parts[3]
                            expected_val = parts[4]
                            
                            passed = status == 'PASS'
                            test_result = {
                                'test_number': test_num,
                                'passed': passed,
                                'actual': actual,
                                'expected': expected_val,
                                'error': None
                            }
                            results['test_results'].append(test_result)
                            if passed:
                                results['passed_count'] += 1
                
                # Handle cases where some tests didn't produce output (crash)
                if len(results['test_results']) < results['total_count']:
                    for i in range(len(results['test_results']), results['total_count']):
                        results['test_results'].append({
                            'test_number': i + 1,
                            'passed': False,
                            'error': 'Runtime error or crash during this test'
                        })
                
                results['passed'] = results['passed_count'] == results['total_count']
                
        except subprocess.TimeoutExpired:
            results['error'] = "Time Limit Exceeded"
        except FileNotFoundError:
            compiler_name = "g++ (MinGW/GCC)" if is_cpp else "gcc (MinGW/GCC)"
            results['error'] = f"{compiler_name} is not available. Please install a C/C++ compiler."
        except Exception as e:
            results['error'] = f"{'C++' if is_cpp else 'C'} execution error: {str(e)}"
        
        return results
    
    def _c_cpp_literal(self, value, is_cpp: bool = True) -> str:
        """Convert a Python value to a C/C++ literal."""
        if value is None:
            return "NULL" if not is_cpp else "nullptr"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, int):
            return str(value)
        if isinstance(value, float):
            return f"{value}"
        if isinstance(value, str):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            if is_cpp:
                return f'string("{escaped}")'
            return f'"{escaped}"'
        return str(value)
    
    def _c_cpp_build_args(self, inputs: list, test_idx: int, is_cpp: bool) -> tuple:
        """Build C/C++ function call arguments from input list. Returns (args_str, setup_code)."""
        args = []
        setup_lines = []
        
        for j, val in enumerate(inputs):
            if isinstance(val, list):
                if all(isinstance(v, int) for v in val):
                    arr_name = f"arr_{test_idx}_{j}"
                    vals = ", ".join(str(v) for v in val)
                    if is_cpp:
                        setup_lines.append(f"vector<int> {arr_name} = {{{vals}}};")
                        args.append(arr_name)
                    else:
                        setup_lines.append(f"int {arr_name}[] = {{{vals}}};")
                        setup_lines.append(f"int {arr_name}_size = {len(val)};")
                        args.append(arr_name)
                        args.append(f"{arr_name}_size")
                elif all(isinstance(v, str) for v in val):
                    arr_name = f"arr_{test_idx}_{j}"
                    if is_cpp:
                        vals = ", ".join(f'"{v}"' for v in val)
                        setup_lines.append(f'vector<string> {arr_name} = {{{vals}}};')
                        args.append(arr_name)
                    else:
                        vals = ", ".join(f'"{v}"' for v in val)
                        setup_lines.append(f'char* {arr_name}[] = {{{vals}}};')
                        setup_lines.append(f"int {arr_name}_size = {len(val)};")
                        args.append(arr_name)
                        args.append(f"{arr_name}_size")
                else:
                    # Mixed type array - use string representation
                    args.append(self._c_cpp_literal(str(val), is_cpp))
            else:
                args.append(self._c_cpp_literal(val, is_cpp))
        
        return ", ".join(args), "\n        ".join(setup_lines)
    
    def _c_cpp_sprint_result(self, var_name: str, expected, is_cpp: bool) -> str:
        """Generate sprintf/snprintf code to convert a result to string for comparison."""
        if isinstance(expected, bool):
            return f'snprintf(actual_buf, 512, "%s", {var_name} ? "true" : "false");'
        if isinstance(expected, int):
            return f'snprintf(actual_buf, 512, "%d", (int){var_name});'
        if isinstance(expected, float):
            return f'snprintf(actual_buf, 512, "%g", (double){var_name});'
        if isinstance(expected, str):
            if is_cpp:
                return f'snprintf(actual_buf, 512, "%s", {var_name}.c_str());'
            return f'snprintf(actual_buf, 512, "%s", {var_name});'
        if isinstance(expected, list):
            if is_cpp:
                return f'''{{
            std::string s = "[";
            for (size_t i = 0; i < {var_name}.size(); i++) {{
                if (i > 0) s += ", ";
                s += std::to_string({var_name}[i]);
            }}
            s += "]";
            snprintf(actual_buf, 512, "%s", s.c_str());
        }}'''
            return f'snprintf(actual_buf, 512, "%d", {var_name});'
        return f'snprintf(actual_buf, 512, "%d", (int){var_name});'
    
    def _c_generate_test(self, func_name: str, inputs, expected, idx: int) -> str:
        """Generate C test code (non-C++)."""
        if isinstance(inputs, list):
            args_parts = []
            setup = []
            for j, val in enumerate(inputs):
                if isinstance(val, list) and all(isinstance(v, int) for v in val):
                    arr_name = f"arr_{idx}_{j}"
                    vals = ", ".join(str(v) for v in val)
                    setup.append(f"int {arr_name}[] = {{{vals}}};")
                    setup.append(f"int {arr_name}_size = {len(val)};")
                    args_parts.append(arr_name)
                    args_parts.append(f"{arr_name}_size")
                elif isinstance(val, str):
                    escaped = val.replace('\\', '\\\\').replace('"', '\\"')
                    args_parts.append(f'"{escaped}"')
                else:
                    args_parts.append(str(val))
            
            call = f"{func_name}({', '.join(args_parts)})"
        else:
            call = f"{func_name}({self._c_cpp_literal(inputs, False)})"
        
        if isinstance(expected, int):
            return f"int res_{idx} = {call};\nsnprintf(actual_buf, 512, \"%d\", res_{idx});"
        elif isinstance(expected, float):
            return f"double res_{idx} = {call};\nsnprintf(actual_buf, 512, \"%g\", res_{idx});"
        elif isinstance(expected, str):
            return f'char* res_{idx} = {call};\nsnprintf(actual_buf, 512, "%s", res_{idx});'
        elif isinstance(expected, bool):
            return f'int res_{idx} = {call};\nsnprintf(actual_buf, 512, "%s", res_{idx} ? "true" : "false");'
        else:
            return f"int res_{idx} = {call};\nsnprintf(actual_buf, 512, \"%d\", res_{idx});"
    
    def validate_code(self, code: str, language: str = "python") -> Dict:
        """Validate code syntax without executing."""
        if language == "python":
            try:
                compile(code, '<string>', 'exec')
                return {'valid': True, 'error': None}
            except SyntaxError as e:
                return {'valid': False, 'error': f"Syntax Error at line {e.lineno}: {e.msg}"}
        
        elif language == "javascript":
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
                    f.write(code)
                    temp_file = f.name
                try:
                    result = subprocess.run(
                        ['node', '--check', temp_file],
                        capture_output=True, text=True, timeout=5
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
        
        elif language in ("c", "cpp"):
            # Quick syntax check by trying to compile
            ext = '.cpp' if language == 'cpp' else '.c'
            compiler = 'g++' if language == 'cpp' else 'gcc'
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
                    f.write(code)
                    temp_file = f.name
                try:
                    result = subprocess.run(
                        [compiler, '-fsyntax-only', temp_file],
                        capture_output=True, text=True, timeout=5
                    )
                    if result.returncode != 0:
                        return {'valid': False, 'error': result.stderr.strip()[:200]}
                    return {'valid': True, 'error': None}
                finally:
                    try:
                        os.unlink(temp_file)
                    except:
                        pass
            except FileNotFoundError:
                return {'valid': True, 'error': None}  # Compiler not found, skip validation
            except:
                return {'valid': True, 'error': None}
        
        return {'valid': True, 'error': None}
