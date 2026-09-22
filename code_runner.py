import subprocess
import tempfile
import os

def run_python_code(code: str):
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as temp:
            temp.write(code)
            temp_file_name = temp.name

        # Run the Python file
        result = subprocess.run(
            ["python", temp_file_name],
            capture_output=True,
            text=True,
            timeout=5  # prevent infinite loops
        )

        # Capture output and errors
        output = result.stdout
        error = result.stderr

        # Clean up temp file
        os.remove(temp_file_name)

        return output, error

    except subprocess.TimeoutExpired:
        return "", "Error: Code execution timed out (possible infinite loop)"

    except Exception as e:
        return "", f"Error: {str(e)}"