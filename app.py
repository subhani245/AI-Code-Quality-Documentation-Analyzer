import streamlit as st
import joblib

from analyzer import analyze_code
from language_detector import detect_language
from complexity_analyzer import estimate_complexity
from feature_extractor import extract_features
from code_runner import run_python_code
from documentation_analyzer import analyze_documentation

from streamlit_ace import st_ace


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI-Assisted Python Code Quality Analyzer",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# LOAD ML MODEL
# ============================================================

@st.cache_resource
def load_model():
    """
    Load the existing machine-learning model.

    Keeping this inside st.cache_resource prevents the model
    from being loaded repeatedly on every Streamlit rerun.
    """
    try:
        return joblib.load("model.pkl")

    except FileNotFoundError:
        st.error(
            "model.pkl was not found. "
            "Please make sure model.pkl is in the project folder."
        )
        return None

    except Exception as error:
        st.error(
            f"Unable to load the ML model: {error}"
        )
        return None


model = load_model()


# ============================================================
# HEADER
# ============================================================

st.title(
    "🤖 AI-Assisted Python Code Quality & Documentation Analyzer"
)

st.caption(
    "Static Analysis + Machine Learning + "
    "Documentation & Type-Hint Analysis"
)

st.divider()


# ============================================================
# INPUT MODE
# ============================================================

st.subheader("📥 Python Code Input")

input_mode = st.radio(
    "Choose input method:",
    [
        "✏️ Code Editor",
        "📁 Upload Python File(s)"
    ],
    horizontal=True
)


# ============================================================
# CODE EDITOR
# ============================================================

code_input = ""

if input_mode == "✏️ Code Editor":

    code_input = st_ace(
        language="python",
        theme="monokai",
        height=350,
        auto_update=True,
        placeholder="Paste your Python code here..."
    )


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_files = []

if input_mode == "📁 Upload Python File(s)":

    uploaded_files = st.file_uploader(
        "Upload one or more Python source files",
        type=["py"],
        accept_multiple_files=True,
        help=(
            "Upload one or more .py files for "
            "code quality and documentation analysis."
        )
    )

    if uploaded_files:

        st.success(
            f"{len(uploaded_files)} Python file(s) selected."
        )

        for uploaded_file in uploaded_files:

            st.write(
                f"📄 **{uploaded_file.name}**"
            )


# ============================================================
# ANALYSIS FUNCTION
# ============================================================

def analyze_single_file(
    code,
    filename="Python Code"
):
    """
    Analyze one Python source file.

    Returns:
        Complete analysis dictionary.
    """

    if not code or not code.strip():

        return None

    # --------------------------------------------------------
    # Detect language
    # --------------------------------------------------------

    try:

        language = detect_language(code)

    except Exception:

        language = "python"

    # --------------------------------------------------------
    # Main analyzer
    # --------------------------------------------------------

    analysis = analyze_code(code)

    # --------------------------------------------------------
    # Documentation analyzer
    # --------------------------------------------------------

    documentation = analyze_documentation(code)

    # --------------------------------------------------------
    # Complexity
    # --------------------------------------------------------

    try:

        complexity = estimate_complexity(code)

    except Exception:

        complexity = "Unable to determine"

    # --------------------------------------------------------
    # ML prediction
    # --------------------------------------------------------

    ml_score = None

    if model is not None:

        try:

            features = extract_features(code)

            ml_score = float(
                model.predict([features])[0]
            )

            # Keep ML score within 0-10
            ml_score = max(
                0.0,
                min(
                    10.0,
                    ml_score
                )
            )

        except Exception as error:

            st.warning(
                f"ML prediction could not be generated "
                f"for {filename}: {error}"
            )

            ml_score = None

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    rule_score = float(
        analysis.get("score", 0)
    )

    if ml_score is not None:

        final_score = round(
            (rule_score + ml_score) / 2,
            2
        )

    else:

        final_score = round(
            rule_score,
            2
        )

    # --------------------------------------------------------
    # Return everything
    # --------------------------------------------------------

    return {

        "filename": filename,

        "language": language,

        "complexity": complexity,

        "analysis": analysis,

        "documentation": documentation,

        "ml_score": ml_score,

        "final_score": final_score,
    }


# ============================================================
# DISPLAY ANALYSIS
# ============================================================

def display_analysis(result):
    """
    Display complete analysis results in Streamlit.
    """

    filename = result["filename"]

    analysis = result["analysis"]

    documentation = result["documentation"]

    metrics = analysis["metrics"]

    quality = analysis["quality"]

    final_score = result["final_score"]

    ml_score = result["ml_score"]

    complexity = result["complexity"]

    # ========================================================
    # FILE TITLE
    # ========================================================

    st.divider()

    st.header(
        f"📄 {filename}"
    )

    # ========================================================
    # TOP METRICS
    # ========================================================

    st.subheader(
        "📊 Code Metrics"
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Functions",
        metrics["functions"]
    )

    col2.metric(
        "Classes",
        metrics["classes"]
    )

    col3.metric(
        "Imports",
        metrics["imports"]
    )

    col4.metric(
        "Lines",
        metrics["lines"]
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Async Functions",
        metrics["async_functions"]
    )

    col2.metric(
        "Loops",
        metrics["loops"]
    )

    col3.metric(
        "Print Statements",
        quality["print_count"]
    )

    col4.metric(
        "Nested Loop Depth",
        quality["nested_loop_depth"]
    )

    # ========================================================
    # QUALITY SCORE
    # ========================================================

    st.subheader(
        "🎯 Quality Score"
    )

    score_col1, score_col2, score_col3 = st.columns(3)

    score_col1.metric(
        "Rule-Based Score",
        f"{analysis['score']} / 10"
    )

    if ml_score is not None:

        score_col2.metric(
            "ML Predicted Score",
            f"{round(ml_score, 2)} / 10"
        )

    else:

        score_col2.metric(
            "ML Predicted Score",
            "N/A"
        )

    score_col3.metric(
        "Final Score",
        f"{final_score} / 10"
    )

    st.progress(
        min(
            max(
                final_score / 10,
                0.0
            ),
            1.0
        )
    )

    # ========================================================
    # COMPLEXITY
    # ========================================================

    st.subheader(
        "⏱️ Estimated Time Complexity"
    )

    st.info(
        complexity
    )

    # ========================================================
    # IMPORTS
    # ========================================================

    st.subheader(
        "📦 Imports"
    )

    imports = analysis.get(
        "imports",
        []
    )

    if imports:

        for imported_module in imports:

            st.code(
                imported_module,
                language="text"
            )

    else:

        st.info(
            "No imports detected."
        )

    # ========================================================
    # DOCUMENTATION SUMMARY
    # ========================================================

    st.subheader(
        "📝 Documentation & Type-Hint Analysis"
    )

    statistics = documentation.get(
        "statistics",
        {}
    )

    doc_col1, doc_col2, doc_col3, doc_col4 = st.columns(4)

    doc_col1.metric(
        "Documented Functions",
        statistics.get(
            "documented_functions",
            0
        )
    )

    doc_col2.metric(
        "Missing Function Docs",
        statistics.get(
            "undocumented_functions",
            0
        )
    )

    doc_col3.metric(
        "Documented Classes",
        statistics.get(
            "documented_classes",
            0
        )
    )

    doc_col4.metric(
        "Missing Class Docs",
        statistics.get(
            "undocumented_classes",
            0
        )
    )

    doc_col1, doc_col2, doc_col3 = st.columns(3)

    doc_col1.metric(
        "Missing Parameter Types",
        statistics.get(
            "missing_parameter_type_hints",
            0
        )
    )

    doc_col2.metric(
        "Missing Return Types",
        statistics.get(
            "missing_return_type_hints",
            0
        )
    )

    doc_col3.metric(
        "Total Documentation Issues",
        statistics.get(
            "total_documentation_issues",
            0
        )
    )

    # ========================================================
    # SYNTAX ERROR
    # ========================================================

    syntax_error = analysis.get(
        "syntax_error"
    )

    if syntax_error:

        st.error(
            "❌ Python syntax error detected."
        )

        st.code(
            (
                f"Line: {syntax_error.get('line')}\n"
                f"Column: {syntax_error.get('column')}\n"
                f"Message: {syntax_error.get('message')}\n"
                f"Code: {syntax_error.get('text')}"
            ),
            language="text"
        )

        return

    # ========================================================
    # DOCUMENTATION ISSUES
    # ========================================================

    st.subheader(
        "📚 Documentation Issues"
    )

    missing_docstrings = documentation.get(
        "missing_docstrings",
        []
    )

    missing_type_hints = documentation.get(
        "missing_type_hints",
        []
    )

    missing_return_types = documentation.get(
        "missing_return_types",
        []
    )

    total_doc_issues = (
        len(missing_docstrings)
        + len(missing_type_hints)
        + len(missing_return_types)
    )

    if total_doc_issues == 0:

        st.success(
            "✅ No missing documentation or type-hint issues detected."
        )

    else:

        # ----------------------------------------------------
        # Missing docstrings
        # ----------------------------------------------------

        if missing_docstrings:

            st.markdown(
                "### ❌ Missing Docstrings"
            )

            for issue in missing_docstrings:

                st.error(
                    f"Line {issue['line']}: "
                    f"{issue['message']}"
                )

        # ----------------------------------------------------
        # Missing parameter type hints
        # ----------------------------------------------------

        if missing_type_hints:

            st.markdown(
                "### ⚠️ Missing Parameter Type Hints"
            )

            for issue in missing_type_hints:

                st.warning(
                    f"Line {issue['line']}: "
                    f"{issue['message']}"
                )

        # ----------------------------------------------------
        # Missing return type hints
        # ----------------------------------------------------

        if missing_return_types:

            st.markdown(
                "### ⚠️ Missing Return Type Hints"
            )

            for issue in missing_return_types:

                st.warning(
                    f"Line {issue['line']}: "
                    f"{issue['message']}"
                )

    # ========================================================
    # EXISTING QUALITY ISSUES
    # ========================================================

    st.subheader(
        "⚠️ Detected Code Quality Issues"
    )

    suggestions = analysis.get(
        "suggestions",
        []
    )

    if suggestions:

        for suggestion in suggestions:

            if suggestion == "Code looks clean.":

                st.success(
                    suggestion
                )

            else:

                st.warning(
                    suggestion
                )

    else:

        st.success(
            "No major quality issues detected."
        )

    # ========================================================
    # IMPROVEMENTS
    # ========================================================

    st.subheader(
        "💡 Suggested Improvements"
    )

    improvements = analysis.get(
        "improvements",
        []
    )

    if improvements:

        for improvement in improvements:

            st.success(
                improvement
            )

    else:

        st.info(
            "No improvements required."
        )

    # ========================================================
    # QUALITY DETAILS
    # ========================================================

    with st.expander(
        "🔍 Detailed Quality Metrics"
    ):

        st.write(
            f"**Print statements:** "
            f"{quality['print_count']}"
        )

        st.write(
            f"**Nested loop depth:** "
            f"{quality['nested_loop_depth']}"
        )

        st.write(
            f"**Long lines:** "
            f"{quality['long_line_count']}"
        )

        st.write(
            f"**Bare except blocks:** "
            f"{quality['bare_except_count']}"
        )

        st.write(
            f"**TODO/FIXME comments:** "
            f"{quality['todo_fixme_count']}"
        )

        if quality["bad_variables"]:

            st.write(
                "**Potentially unclear variables:**"
            )

            for variable in quality[
                "bad_variables"
            ]:

                st.write(
                    f"- `{variable}`"
                )

    # ========================================================
    # RAW ANALYSIS
    # ========================================================

    with st.expander(
        "🧪 Full Analysis Data"
    ):

        st.json(
            {
                "metrics": metrics,
                "documentation": documentation,
                "quality": quality,
            }
        )


# ============================================================
# ANALYZE BUTTON
# ============================================================

if st.button(
    "🚀 Analyze Code",
    use_container_width=True
):

    results = []

    # ========================================================
    # EDITOR MODE
    # ========================================================

    if input_mode == "✏️ Code Editor":

        if not code_input or not code_input.strip():

            st.warning(
                "Please enter some Python code to analyze."
            )

            st.stop()

        # ----------------------------------------------------
        # Run Python code
        # ----------------------------------------------------

        output = ""
        error = ""

        try:

            language = detect_language(
                code_input
            )

        except Exception:

            language = "python"

        if language == "python":

            try:

                output, error = run_python_code(
                    code_input
                )

            except Exception as run_error:

                error = str(run_error)

        # ----------------------------------------------------
        # Analyze
        # ----------------------------------------------------

        result = analyze_single_file(
            code_input,
            "Code Editor Input"
        )

        if result:

            results.append(
                result
            )

        # ----------------------------------------------------
        # Display program output
        # ----------------------------------------------------

        if language == "python":

            st.divider()

            st.subheader(
                "▶ Program Output"
            )

            if output:

                st.code(
                    output,
                    language="text"
                )

            else:

                st.info(
                    "Program produced no output."
                )

            if error:

                st.subheader(
                    "⚠ Runtime / Execution Errors"
                )

                st.code(
                    error,
                    language="text"
                )

    # ========================================================
    # FILE UPLOAD MODE
    # ========================================================

    else:

        if not uploaded_files:

            st.warning(
                "Please upload at least one Python (.py) file."
            )

            st.stop()

        progress = st.progress(0)

        total_files = len(
            uploaded_files
        )

        for index, uploaded_file in enumerate(
            uploaded_files,
            start=1
        ):

            try:

                raw_data = uploaded_file.read()

                code = raw_data.decode(
                    "utf-8"
                )

            except UnicodeDecodeError:

                st.error(
                    f"Unable to read "
                    f"{uploaded_file.name}. "
                    f"Please use UTF-8 encoded Python files."
                )

                continue

            except Exception as error:

                st.error(
                    f"Could not read "
                    f"{uploaded_file.name}: {error}"
                )

                continue

            result = analyze_single_file(
                code,
                uploaded_file.name
            )

            if result:

                results.append(
                    result
                )

            progress.progress(
                index / total_files
            )

        progress.empty()

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    if not results:

        st.error(
            "No valid Python code could be analyzed."
        )

        st.stop()

    # ========================================================
    # MULTI-FILE SUMMARY
    # ========================================================

    if len(results) > 1:

        st.divider()

        st.header(
            "📊 Overall Project Summary"
        )

        total_files = len(
            results
        )

        total_functions = sum(
            result["analysis"]["metrics"]["functions"]
            for result in results
        )

        total_classes = sum(
            result["analysis"]["metrics"]["classes"]
            for result in results
        )

        total_imports = sum(
            result["analysis"]["metrics"]["imports"]
            for result in results
        )

        total_lines = sum(
            result["analysis"]["metrics"]["lines"]
            for result in results
        )

        total_doc_issues = sum(
            result["documentation"]["statistics"][
                "total_documentation_issues"
            ]
            for result in results
        )

        total_quality_issues = sum(
            len(
                result["analysis"]["suggestions"]
            )
            for result in results
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Files Analyzed",
            total_files
        )

        col2.metric(
            "Functions",
            total_functions
        )

        col3.metric(
            "Classes",
            total_classes
        )

        col4.metric(
            "Imports",
            total_imports
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total Lines",
            total_lines
        )

        col2.metric(
            "Documentation Issues",
            total_doc_issues
        )

        col3.metric(
            "Quality Findings",
            total_quality_issues
        )

    # ========================================================
    # INDIVIDUAL RESULTS
    # ========================================================

    for result in results:

        display_analysis(
            result
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI-Assisted Python Code Quality & Documentation Analyzer "
    "| AST Analysis + Rule-Based Analysis + Machine Learning"
)