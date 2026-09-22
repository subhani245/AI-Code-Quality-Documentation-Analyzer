"""
AI-Assisted Python Code Quality Analyzer

This module performs static analysis of Python source code.

Existing functionality preserved:
- Bad variable name detection
- Print statement detection
- Nested loop detection
- Long code detection
- Quality score
- Suggestions
- Improvements

New functionality:
- Python AST-based analysis
- Function counting
- Class counting
- Import counting
- Async function counting
- Missing docstring detection
- Missing type-hint detection
- Missing return type detection
- Basic quality metrics
- Syntax-error handling
"""

import ast
from typing import Any, Dict, List, Optional

from rules import rules


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _safe_get_source_segment(
    code: str,
    node: ast.AST
) -> str:
    """
    Safely return the source segment belonging to an AST node.

    Args:
        code: Complete Python source code.
        node: AST node.

    Returns:
        Source segment as a string, or an empty string if unavailable.
    """
    try:
        segment = ast.get_source_segment(code, node)
        return segment if segment else ""
    except Exception:
        return ""


def _get_function_name(node: ast.AST) -> str:
    """Return a readable function name."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return node.name

    return "<unknown>"


def _has_docstring(node: ast.AST) -> bool:
    """
    Check whether an AST node has a docstring.

    Only functions, async functions and classes are considered.
    """
    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        ),
    ):
        return ast.get_docstring(node) is not None

    return False


def _annotation_to_string(annotation: Optional[ast.AST]) -> Optional[str]:
    """
    Convert a type annotation AST node into readable text.

    Example:
        int
        str
        list[int]
        Optional[str]
    """
    if annotation is None:
        return None

    try:
        return ast.unparse(annotation)
    except Exception:
        return "<annotation>"


def _count_imports(tree: ast.AST) -> int:
    """Count import and from-import statements."""
    count = 0

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            count += 1

    return count


def _get_import_names(tree: ast.AST) -> List[str]:
    """Return readable names of imported modules."""
    imports = []

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""

            for alias in node.names:
                if alias.name == "*":
                    imports.append(f"from {module} import *")
                else:
                    imports.append(f"from {module} import {alias.name}")

    return imports


def _count_functions(tree: ast.AST) -> int:
    """Count normal and asynchronous functions."""
    return sum(
        isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        )
        for node in ast.walk(tree)
    )


def _count_classes(tree: ast.AST) -> int:
    """Count class definitions."""
    return sum(
        isinstance(node, ast.ClassDef)
        for node in ast.walk(tree)
    )


def _count_async_functions(tree: ast.AST) -> int:
    """Count async functions."""
    return sum(
        isinstance(node, ast.AsyncFunctionDef)
        for node in ast.walk(tree)
    )


def _count_loops(tree: ast.AST) -> int:
    """Count for and while loops."""
    return sum(
        isinstance(node, (ast.For, ast.AsyncFor, ast.While))
        for node in ast.walk(tree)
    )


def _count_print_calls(tree: ast.AST) -> int:
    """
    Count actual print() function calls using AST.

    This is more reliable than code.count("print(").
    """
    count = 0

    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):
                if node.func.id == "print":
                    count += 1

    return count


def _find_bad_variable_names(tree: ast.AST) -> List[str]:
    """
    Find variables whose names are listed in rules.py.

    Only actual variable assignments are considered.
    """
    bad_names = set(rules.get("bad_variable_names", []))
    found = set()

    for node in ast.walk(tree):

        # x = ...
        if isinstance(node, ast.Assign):

            for target in node.targets:

                if isinstance(target, ast.Name):
                    if target.id in bad_names:
                        found.add(target.id)

                elif isinstance(target, (ast.Tuple, ast.List)):

                    for element in target.elts:

                        if isinstance(element, ast.Name):
                            if element.id in bad_names:
                                found.add(element.id)

        # x: int = ...
        elif isinstance(node, ast.AnnAssign):

            if isinstance(node.target, ast.Name):
                if node.target.id in bad_names:
                    found.add(node.target.id)

        # for x in ...
        elif isinstance(node, (ast.For, ast.AsyncFor)):

            target = node.target

            if isinstance(target, ast.Name):
                if target.id in bad_names:
                    found.add(target.id)

    return sorted(found)


def _find_nested_loops(tree: ast.AST) -> int:
    """
    Find the maximum loop nesting depth.

    Returns:
        Maximum number of nested loops.
    """

    loop_types = (
        ast.For,
        ast.AsyncFor,
        ast.While,
    )

    max_depth = 0

    def visit(node: ast.AST, current_depth: int = 0) -> None:
        nonlocal max_depth

        if isinstance(node, loop_types):
            current_depth += 1
            max_depth = max(max_depth, current_depth)

        for child in ast.iter_child_nodes(node):
            visit(child, current_depth)

    visit(tree)

    return max_depth


# ---------------------------------------------------------------------------
# Documentation and type-hint analysis
# ---------------------------------------------------------------------------

def _analyze_documentation(
    tree: ast.AST
) -> Dict[str, Any]:
    """
    Analyze documentation and type hints.

    Checks:
    - Missing function docstrings
    - Missing class docstrings
    - Missing parameter type hints
    - Missing return type hints
    - Missing *args / **kwargs annotations
    """

    missing_docstrings: List[Dict[str, Any]] = []
    missing_type_hints: List[Dict[str, Any]] = []
    missing_return_types: List[Dict[str, Any]] = []

    documented_functions = 0
    undocumented_functions = 0

    documented_classes = 0
    undocumented_classes = 0

    for node in ast.walk(tree):

        # ---------------------------------------------------------------
        # Functions
        # ---------------------------------------------------------------

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):

            function_name = _get_function_name(node)

            if _has_docstring(node):
                documented_functions += 1
            else:
                undocumented_functions += 1

                missing_docstrings.append(
                    {
                        "type": "function",
                        "name": function_name,
                        "line": getattr(node, "lineno", None),
                        "message": (
                            f"Function '{function_name}' "
                            "is missing a docstring."
                        ),
                    }
                )

            # -----------------------------------------------------------
            # Normal parameters
            # -----------------------------------------------------------

            all_arguments = []

            all_arguments.extend(node.args.posonlyargs)
            all_arguments.extend(node.args.args)
            all_arguments.extend(node.args.kwonlyargs)

            # *args
            if node.args.vararg is not None:
                all_arguments.append(node.args.vararg)

            # **kwargs
            if node.args.kwarg is not None:
                all_arguments.append(node.args.kwarg)

            for argument in all_arguments:

                # self and cls normally don't need annotations
                if argument.arg in {"self", "cls"}:
                    continue

                if argument.annotation is None:

                    missing_type_hints.append(
                        {
                            "function": function_name,
                            "parameter": argument.arg,
                            "line": getattr(
                                argument,
                                "lineno",
                                getattr(node, "lineno", None)
                            ),
                            "message": (
                                f"Parameter '{argument.arg}' in "
                                f"function '{function_name}' "
                                "is missing a type hint."
                            ),
                        }
                    )

            # -----------------------------------------------------------
            # Return type
            # -----------------------------------------------------------

            if node.returns is None:

                missing_return_types.append(
                    {
                        "function": function_name,
                        "line": getattr(node, "lineno", None),
                        "message": (
                            f"Function '{function_name}' "
                            "is missing a return type hint."
                        ),
                    }
                )

        # ---------------------------------------------------------------
        # Classes
        # ---------------------------------------------------------------

        elif isinstance(node, ast.ClassDef):

            class_name = node.name

            if _has_docstring(node):
                documented_classes += 1
            else:
                undocumented_classes += 1

                missing_docstrings.append(
                    {
                        "type": "class",
                        "name": class_name,
                        "line": getattr(node, "lineno", None),
                        "message": (
                            f"Class '{class_name}' "
                            "is missing a docstring."
                        ),
                    }
                )

    total_docstring_issues = len(missing_docstrings)
    total_type_hint_issues = (
        len(missing_type_hints)
        + len(missing_return_types)
    )

    return {
        "missing_docstrings": missing_docstrings,
        "missing_type_hints": missing_type_hints,
        "missing_return_types": missing_return_types,

        "missing_docstring_count": total_docstring_issues,
        "missing_type_hint_count": total_type_hint_issues,

        "missing_parameter_type_hint_count": len(
            missing_type_hints
        ),

        "missing_return_type_count": len(
            missing_return_types
        ),

        "documented_functions": documented_functions,
        "undocumented_functions": undocumented_functions,

        "documented_classes": documented_classes,
        "undocumented_classes": undocumented_classes,
    }


# ---------------------------------------------------------------------------
# Existing quality analysis
# ---------------------------------------------------------------------------

def _analyze_existing_quality_rules(
    code: str,
    tree: ast.AST,
) -> Dict[str, Any]:
    """
    Run the existing quality rules from the original project.

    This preserves the original functionality while making the checks
    more reliable where possible.
    """

    suggestions: List[str] = []
    improvements: List[str] = []

    score = 10.0

    lines = code.splitlines()

    # ------------------------------------------------------------------
    # Bad variable names
    # ------------------------------------------------------------------

    bad_variables = _find_bad_variable_names(tree)

    for variable in bad_variables:

        suggestions.append(
            f"Avoid using unclear variable name '{variable}'."
        )

        improvements.append(
            f"Rename '{variable}' to something meaningful."
        )

        score -= 1

    # ------------------------------------------------------------------
    # Print statements
    # ------------------------------------------------------------------

    print_count = _count_print_calls(tree)

    if print_count > 3:

        suggestions.append(
            "Too many debug print statements detected."
        )

        improvements.append(
            "Reduce print usage or replace it with proper logging."
        )

        score -= 2

    elif print_count > 1:

        suggestions.append(
            "Multiple print statements detected."
        )

        improvements.append(
            "Consider minimizing debug prints."
        )

        score -= 1

    # A single print is intentionally allowed,
    # preserving your original behavior.

    # ------------------------------------------------------------------
    # Nested loops
    # ------------------------------------------------------------------

    max_loop_depth = _find_nested_loops(tree)

    if max_loop_depth >= 2:

        suggestions.append(
            "Nested loops detected."
        )

        improvements.append(
            "Try reducing nested loops using better logic, "
            "built-in functions, or more efficient data structures."
        )

        score -= 2

    # ------------------------------------------------------------------
    # Long code
    # ------------------------------------------------------------------

    if len(lines) > 25:

        suggestions.append(
            "Code block is long."
        )

        improvements.append(
            "Split the code into smaller functions or modules."
        )

        score -= 1

    # ------------------------------------------------------------------
    # Long lines
    # ------------------------------------------------------------------

    long_line_numbers = []

    max_line_length = rules.get(
        "max_line_length",
        88
    )

    for number, line in enumerate(
        lines,
        start=1
    ):

        if len(line) > max_line_length:

            long_line_numbers.append(number)

    if long_line_numbers:

        suggestions.append(
            f"{len(long_line_numbers)} line(s) exceed "
            f"{max_line_length} characters."
        )

        improvements.append(
            "Break long lines into smaller readable expressions."
        )

        score -= min(
            1,
            len(long_line_numbers) * 0.1
        )

    # ------------------------------------------------------------------
    # Bare except
    # ------------------------------------------------------------------

    bare_except_count = 0

    for node in ast.walk(tree):

        if isinstance(node, ast.ExceptHandler):

            if node.type is None:
                bare_except_count += 1

    if bare_except_count > 0:

        suggestions.append(
            "Bare except block detected."
        )

        improvements.append(
            "Catch specific exception types instead of using "
            "a bare except."
        )

        score -= 1

    # ------------------------------------------------------------------
    # TODO/FIXME
    # ------------------------------------------------------------------

    todo_count = 0

    for line in lines:

        upper_line = line.upper()

        if "TODO" in upper_line:
            todo_count += 1

        if "FIXME" in upper_line:
            todo_count += 1

    if todo_count > 0:

        suggestions.append(
            f"{todo_count} TODO/FIXME comment(s) detected."
        )

        improvements.append(
            "Review TODO/FIXME comments and resolve them before release."
        )

    # ------------------------------------------------------------------
    # Missing documentation
    # ------------------------------------------------------------------

    documentation = _analyze_documentation(tree)

    missing_doc_count = documentation[
        "missing_docstring_count"
    ]

    if missing_doc_count > 0:

        suggestions.append(
            f"{missing_doc_count} missing docstring issue(s) detected."
        )

        improvements.append(
            "Add clear docstrings to functions and classes."
        )

        score -= min(
            2,
            missing_doc_count * 0.5
        )

    # ------------------------------------------------------------------
    # Missing type hints
    # ------------------------------------------------------------------

    missing_type_count = documentation[
        "missing_type_hint_count"
    ]

    if missing_type_count > 0:

        suggestions.append(
            f"{missing_type_count} missing type hint issue(s) detected."
        )

        improvements.append(
            "Add parameter and return type hints to improve "
            "readability and maintainability."
        )

        score -= min(
            2,
            missing_type_count * 0.25
        )

    # ------------------------------------------------------------------
    # Score safety
    # ------------------------------------------------------------------

    score = max(
        0.0,
        min(
            10.0,
            round(score, 2)
        )
    )

    return {
        "score": score,
        "suggestions": suggestions,
        "improvements": improvements,

        "print_count": print_count,
        "bad_variables": bad_variables,

        "nested_loop_depth": max_loop_depth,
        "long_line_count": len(long_line_numbers),
        "long_line_numbers": long_line_numbers,

        "bare_except_count": bare_except_count,
        "todo_fixme_count": todo_count,
    }


# ---------------------------------------------------------------------------
# Main public function
# ---------------------------------------------------------------------------

def analyze_code(code: str) -> Dict[str, Any]:
    """
    Analyze Python source code.

    This is the main function that should be called from app.py.

    Args:
        code:
            Python source code as a string.

    Returns:
        Dictionary containing:
            - score
            - suggestions
            - improvements
            - metrics
            - documentation
            - quality

    Example:
        result = analyze_code(code)

        print(result["metrics"]["functions"])
        print(result["documentation"]["missing_docstring_count"])
    """

    if not isinstance(code, str):

        raise TypeError(
            "code must be provided as a string."
        )

    if not code.strip():

        return {
            "score": 10.0,

            "suggestions": [
                "No Python code was provided."
            ],

            "improvements": [
                "Provide a Python source file or enter Python code."
            ],

            "metrics": {
                "lines": 0,
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "async_functions": 0,
                "loops": 0,
            },

            "imports": [],

            "documentation": {
                "missing_docstrings": [],
                "missing_type_hints": [],
                "missing_return_types": [],

                "missing_docstring_count": 0,
                "missing_type_hint_count": 0,
                "missing_parameter_type_hint_count": 0,
                "missing_return_type_count": 0,

                "documented_functions": 0,
                "undocumented_functions": 0,

                "documented_classes": 0,
                "undocumented_classes": 0,
            },

            "quality": {
                "print_count": 0,
                "bad_variables": [],
                "nested_loop_depth": 0,
                "long_line_count": 0,
                "long_line_numbers": [],
                "bare_except_count": 0,
                "todo_fixme_count": 0,
            },

            "syntax_error": None,
        }

    # ------------------------------------------------------------------
    # Parse Python source code
    # ------------------------------------------------------------------

    try:

        tree = ast.parse(code)

    except SyntaxError as error:

        return {
            "score": 0.0,

            "suggestions": [
                "Python syntax error detected."
            ],

            "improvements": [
                "Fix the syntax error before running "
                "quality analysis."
            ],

            "metrics": {
                "lines": len(code.splitlines()),
                "functions": 0,
                "classes": 0,
                "imports": 0,
                "async_functions": 0,
                "loops": 0,
            },

            "imports": [],

            "documentation": {
                "missing_docstrings": [],
                "missing_type_hints": [],
                "missing_return_types": [],

                "missing_docstring_count": 0,
                "missing_type_hint_count": 0,
                "missing_parameter_type_hint_count": 0,
                "missing_return_type_count": 0,

                "documented_functions": 0,
                "undocumented_functions": 0,

                "documented_classes": 0,
                "undocumented_classes": 0,
            },

            "quality": {
                "print_count": 0,
                "bad_variables": [],
                "nested_loop_depth": 0,
                "long_line_count": 0,
                "long_line_numbers": [],
                "bare_except_count": 0,
                "todo_fixme_count": 0,
            },

            "syntax_error": {
                "message": error.msg,
                "line": error.lineno,
                "column": error.offset,
                "text": error.text.strip()
                if error.text
                else "",
            },
        }

    # ------------------------------------------------------------------
    # AST metrics
    # ------------------------------------------------------------------

    line_count = len(code.splitlines())

    function_count = _count_functions(tree)

    class_count = _count_classes(tree)

    import_count = _count_imports(tree)

    async_function_count = _count_async_functions(tree)

    loop_count = _count_loops(tree)

    import_names = _get_import_names(tree)

    # ------------------------------------------------------------------
    # Documentation
    # ------------------------------------------------------------------

    documentation = _analyze_documentation(tree)

    # ------------------------------------------------------------------
    # Existing quality rules
    # ------------------------------------------------------------------

    quality = _analyze_existing_quality_rules(
        code,
        tree
    )

    suggestions = quality["suggestions"]

    improvements = quality["improvements"]

    # ------------------------------------------------------------------
    # No issues case
    # ------------------------------------------------------------------

    if not suggestions:

        suggestions.append(
            "Code looks clean."
        )

        improvements.append(
            "No major improvements required based on the "
            "configured rules."
        )

    # ------------------------------------------------------------------
    # Final result
    # ------------------------------------------------------------------

    result = {

        "score": quality["score"],

        "suggestions": suggestions,

        "improvements": improvements,

        "metrics": {

            "lines": line_count,

            "functions": function_count,

            "classes": class_count,

            "imports": import_count,

            "async_functions": async_function_count,

            "loops": loop_count,
        },

        "imports": import_names,

        "documentation": documentation,

        "quality": {

            "print_count": quality["print_count"],

            "bad_variables": quality["bad_variables"],

            "nested_loop_depth": quality[
                "nested_loop_depth"
            ],

            "long_line_count": quality[
                "long_line_count"
            ],

            "long_line_numbers": quality[
                "long_line_numbers"
            ],

            "bare_except_count": quality[
                "bare_except_count"
            ],

            "todo_fixme_count": quality[
                "todo_fixme_count"
            ],
        },

        "syntax_error": None,
    }

    return result


# ---------------------------------------------------------------------------
# Backward-compatible helper
# ---------------------------------------------------------------------------

def analyze_code_legacy(code: str):
    """
    Backward-compatible version of the original function.

    Returns:
        score, suggestions, improvements

    This can be used if older code in app.py expects the original
    three-value return format.
    """

    result = analyze_code(code)

    return (
        result["score"],
        result["suggestions"],
        result["improvements"],
    )


# ---------------------------------------------------------------------------
# Simple command-line test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    sample_code = """
import os
from math import sqrt

def calculate(a, b):
    print(a)
    return a + b

class Calculator:

    def multiply(self, x, y):
        return x * y
"""

    analysis = analyze_code(sample_code)

    print("\n========== CODE METRICS ==========")

    print(
        "Lines:",
        analysis["metrics"]["lines"]
    )

    print(
        "Functions:",
        analysis["metrics"]["functions"]
    )

    print(
        "Classes:",
        analysis["metrics"]["classes"]
    )

    print(
        "Imports:",
        analysis["metrics"]["imports"]
    )

    print(
        "Loops:",
        analysis["metrics"]["loops"]
    )

    print("\n========== DOCUMENTATION ==========")

    print(
        "Missing docstrings:",
        analysis["documentation"][
            "missing_docstring_count"
        ]
    )

    print(
        "Missing type hints:",
        analysis["documentation"][
            "missing_type_hint_count"
        ]
    )

    print(
        "Missing return types:",
        analysis["documentation"][
            "missing_return_type_count"
        ]
    )

    print("\n========== QUALITY ==========")

    print(
        "Score:",
        analysis["score"],
        "/ 10"
    )

    for suggestion in analysis["suggestions"]:
        print("-", suggestion)