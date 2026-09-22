"""
Python Documentation and Type-Hint Analyzer.

This module independently analyzes Python source code for:

1. Missing function docstrings
2. Missing class docstrings
3. Missing parameter type hints
4. Missing return type hints
5. Documentation statistics

It uses Python's built-in AST module.
"""

import ast
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _get_annotation_name(
    annotation: Optional[ast.AST]
) -> Optional[str]:
    """
    Convert an AST annotation into readable text.

    Examples:
        int
        str
        list[int]
        Optional[str]

    Args:
        annotation: AST annotation node.

    Returns:
        String representation of annotation or None.
    """

    if annotation is None:
        return None

    try:
        return ast.unparse(annotation)

    except Exception:
        return "<annotation>"


def _get_function_parameters(
    node: ast.FunctionDef | ast.AsyncFunctionDef
) -> List[ast.arg]:
    """
    Return all parameters belonging to a function.

    Includes:
    - positional-only arguments
    - normal arguments
    - keyword-only arguments
    - *args
    - **kwargs
    """

    parameters: List[ast.arg] = []

    parameters.extend(node.args.posonlyargs)
    parameters.extend(node.args.args)
    parameters.extend(node.args.kwonlyargs)

    if node.args.vararg is not None:
        parameters.append(node.args.vararg)

    if node.args.kwarg is not None:
        parameters.append(node.args.kwarg)

    return parameters


def _is_documented(
    node: ast.AST
) -> bool:
    """Return True if the AST node has a docstring."""

    return ast.get_docstring(node) is not None


# ---------------------------------------------------------------------------
# Function analysis
# ---------------------------------------------------------------------------

def analyze_function(
    node: ast.FunctionDef | ast.AsyncFunctionDef
) -> Dict[str, Any]:
    """
    Analyze one Python function.

    Returns information about:
    - docstring
    - parameter type hints
    - return type
    """

    missing_parameters: List[Dict[str, Any]] = []

    parameters = _get_function_parameters(node)

    for parameter in parameters:

        # self and cls are conventionally not required
        # to have type annotations.
        if parameter.arg in {"self", "cls"}:
            continue

        if parameter.annotation is None:

            missing_parameters.append(
                {
                    "name": parameter.arg,

                    "line": getattr(
                        parameter,
                        "lineno",
                        getattr(node, "lineno", None)
                    ),

                    "message": (
                        f"Parameter '{parameter.arg}' "
                        f"in function '{node.name}' "
                        "has no type hint."
                    ),
                }
            )

    return {

        "name": node.name,

        "line": getattr(
            node,
            "lineno",
            None
        ),

        "is_async": isinstance(
            node,
            ast.AsyncFunctionDef
        ),

        "has_docstring": _is_documented(node),

        "docstring": ast.get_docstring(node),

        "missing_parameters": missing_parameters,

        "missing_parameter_type_hints": len(
            missing_parameters
        ),

        "has_return_type": (
            node.returns is not None
        ),

        "return_type": _get_annotation_name(
            node.returns
        ),

        "missing_return_type": (
            node.returns is None
        ),
    }


# ---------------------------------------------------------------------------
# Class analysis
# ---------------------------------------------------------------------------

def analyze_class(
    node: ast.ClassDef
) -> Dict[str, Any]:
    """
    Analyze one Python class.

    Checks whether the class has a docstring.
    Also analyzes methods contained in the class.
    """

    methods: List[Dict[str, Any]] = []

    for child in node.body:

        if isinstance(
            child,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            )
        ):

            methods.append(
                analyze_function(child)
            )

    return {

        "name": node.name,

        "line": getattr(
            node,
            "lineno",
            None
        ),

        "has_docstring": _is_documented(node),

        "docstring": ast.get_docstring(node),

        "methods": methods,
    }


# ---------------------------------------------------------------------------
# Main analyzer
# ---------------------------------------------------------------------------

def analyze_documentation(
    code: str
) -> Dict[str, Any]:
    """
    Analyze documentation and type hints in Python code.

    Args:
        code:
            Python source code as a string.

    Returns:
        Dictionary containing complete documentation analysis.
    """

    if not isinstance(code, str):

        raise TypeError(
            "code must be a string."
        )

    if not code.strip():

        return {
            "success": True,
            "syntax_error": None,

            "functions": [],
            "classes": [],

            "missing_docstrings": [],
            "missing_type_hints": [],
            "missing_return_types": [],

            "statistics": {
                "total_functions": 0,
                "documented_functions": 0,
                "undocumented_functions": 0,

                "total_classes": 0,
                "documented_classes": 0,
                "undocumented_classes": 0,

                "missing_parameter_type_hints": 0,
                "missing_return_type_hints": 0,

                "total_documentation_issues": 0,
            },
        }

    # ------------------------------------------------------------------
    # Parse AST
    # ------------------------------------------------------------------

    try:

        tree = ast.parse(code)

    except SyntaxError as error:

        return {
            "success": False,

            "syntax_error": {
                "message": error.msg,

                "line": error.lineno,

                "column": error.offset,

                "text": (
                    error.text.strip()
                    if error.text
                    else ""
                ),
            },

            "functions": [],
            "classes": [],

            "missing_docstrings": [],
            "missing_type_hints": [],
            "missing_return_types": [],

            "statistics": {
                "total_functions": 0,
                "documented_functions": 0,
                "undocumented_functions": 0,

                "total_classes": 0,
                "documented_classes": 0,
                "undocumented_classes": 0,

                "missing_parameter_type_hints": 0,
                "missing_return_type_hints": 0,

                "total_documentation_issues": 0,
            },
        }

    # ------------------------------------------------------------------
    # Containers
    # ------------------------------------------------------------------

    functions: List[Dict[str, Any]] = []

    classes: List[Dict[str, Any]] = []

    missing_docstrings: List[Dict[str, Any]] = []

    missing_type_hints: List[Dict[str, Any]] = []

    missing_return_types: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Analyze all functions and classes
    # ------------------------------------------------------------------

    for node in ast.walk(tree):

        # --------------------------------------------------------------
        # Functions
        # --------------------------------------------------------------

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            )
        ):

            result = analyze_function(node)

            functions.append(result)

            if not result["has_docstring"]:

                missing_docstrings.append(
                    {
                        "type": "function",

                        "name": node.name,

                        "line": node.lineno,

                        "message": (
                            f"Function '{node.name}' "
                            "is missing a docstring."
                        ),
                    }
                )

            for parameter in result[
                "missing_parameters"
            ]:

                missing_type_hints.append(
                    {
                        "type": "parameter",

                        "function": node.name,

                        "parameter": parameter[
                            "name"
                        ],

                        "line": parameter[
                            "line"
                        ],

                        "message": parameter[
                            "message"
                        ],
                    }
                )

            if result["missing_return_type"]:

                missing_return_types.append(
                    {
                        "function": node.name,

                        "line": node.lineno,

                        "message": (
                            f"Function '{node.name}' "
                            "is missing a return type hint."
                        ),
                    }
                )

        # --------------------------------------------------------------
        # Classes
        # --------------------------------------------------------------

        elif isinstance(node, ast.ClassDef):

            result = analyze_class(node)

            classes.append(result)

            if not result["has_docstring"]:

                missing_docstrings.append(
                    {
                        "type": "class",

                        "name": node.name,

                        "line": node.lineno,

                        "message": (
                            f"Class '{node.name}' "
                            "is missing a docstring."
                        ),
                    }
                )

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    total_functions = len(functions)

    documented_functions = sum(
        function["has_docstring"]
        for function in functions
    )

    undocumented_functions = (
        total_functions
        - documented_functions
    )

    total_classes = len(classes)

    documented_classes = sum(
        class_info["has_docstring"]
        for class_info in classes
    )

    undocumented_classes = (
        total_classes
        - documented_classes
    )

    missing_parameter_count = len(
        missing_type_hints
    )

    missing_return_count = len(
        missing_return_types
    )

    total_issues = (
        len(missing_docstrings)
        + missing_parameter_count
        + missing_return_count
    )

    # ------------------------------------------------------------------
    # Return result
    # ------------------------------------------------------------------

    return {

        "success": True,

        "syntax_error": None,

        "functions": functions,

        "classes": classes,

        "missing_docstrings": missing_docstrings,

        "missing_type_hints": missing_type_hints,

        "missing_return_types": missing_return_types,

        "statistics": {

            "total_functions": total_functions,

            "documented_functions": documented_functions,

            "undocumented_functions": undocumented_functions,

            "total_classes": total_classes,

            "documented_classes": documented_classes,

            "undocumented_classes": undocumented_classes,

            "missing_parameter_type_hints": (
                missing_parameter_count
            ),

            "missing_return_type_hints": (
                missing_return_count
            ),

            "total_documentation_issues": (
                total_issues
            ),
        },
    }


# ---------------------------------------------------------------------------
# Pretty-print helper
# ---------------------------------------------------------------------------

def print_documentation_report(
    result: Dict[str, Any]
) -> None:
    """
    Print a human-readable documentation report.
    """

    print("\n" + "=" * 60)

    print(
        "PYTHON DOCUMENTATION & TYPE-HINT REPORT"
    )

    print("=" * 60)

    if not result["success"]:

        error = result["syntax_error"]

        print("\n❌ Syntax Error")

        print(
            f"Line: {error['line']}"
        )

        print(
            f"Message: {error['message']}"
        )

        return

    statistics = result["statistics"]

    print(
        f"\nFunctions: "
        f"{statistics['total_functions']}"
    )

    print(
        f"Documented functions: "
        f"{statistics['documented_functions']}"
    )

    print(
        f"Undocumented functions: "
        f"{statistics['undocumented_functions']}"
    )

    print(
        f"\nClasses: "
        f"{statistics['total_classes']}"
    )

    print(
        f"Documented classes: "
        f"{statistics['documented_classes']}"
    )

    print(
        f"Undocumented classes: "
        f"{statistics['undocumented_classes']}"
    )

    print(
        f"\nMissing parameter type hints: "
        f"{statistics['missing_parameter_type_hints']}"
    )

    print(
        f"Missing return type hints: "
        f"{statistics['missing_return_type_hints']}"
    )

    print(
        f"Total documentation issues: "
        f"{statistics['total_documentation_issues']}"
    )

    # ---------------------------------------------------------------
    # Missing docstrings
    # ---------------------------------------------------------------

    if result["missing_docstrings"]:

        print("\n--- Missing Docstrings ---")

        for issue in result[
            "missing_docstrings"
        ]:

            print(
                f"Line {issue['line']}: "
                f"{issue['message']}"
            )

    # ---------------------------------------------------------------
    # Missing parameter hints
    # ---------------------------------------------------------------

    if result["missing_type_hints"]:

        print(
            "\n--- Missing Parameter Type Hints ---"
        )

        for issue in result[
            "missing_type_hints"
        ]:

            print(
                f"Line {issue['line']}: "
                f"{issue['message']}"
            )

    # ---------------------------------------------------------------
    # Missing return hints
    # ---------------------------------------------------------------

    if result["missing_return_types"]:

        print(
            "\n--- Missing Return Type Hints ---"
        )

        for issue in result[
            "missing_return_types"
        ]:

            print(
                f"Line {issue['line']}: "
                f"{issue['message']}"
            )


# ---------------------------------------------------------------------------
# Direct execution test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    sample_code = """
import os
from math import sqrt


def calculate(a, b):
    return a + b


def documented_function(
    value: int
) -> int:
    \"\"\"Return the supplied integer.\"\"\"
    return value


class Calculator:

    def add(self, x, y):
        return x + y
"""

    report = analyze_documentation(
        sample_code
    )

    print_documentation_report(
        report
    )