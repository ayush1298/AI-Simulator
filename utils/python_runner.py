import subprocess
import tempfile
import os
import sys

def run_python_code(code: str) -> (str, str):
    """
    Analyzes dependencies, installs them, and executes Python code in a secure temporary environment.

    Args:
        code: The Python code to execute.

    Returns:
        A tuple containing the standard output and standard error.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # 1. Write the generated code to a file
        file_path = os.path.join(temp_dir, "main.py")
        with open(file_path, "w") as f:
            f.write(code)

        try:
            # 2. Use pipreqs to generate requirements.txt
            subprocess.run(
                ["pipreqs", "--force", temp_dir],
                capture_output=True, text=True, timeout=30
            )

            # 3. Install the dependencies from requirements.txt
            requirements_path = os.path.join(temp_dir, "requirements.txt")
            if os.path.exists(requirements_path):
                install_process = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", requirements_path],
                    capture_output=True, text=True, timeout=120
                )
                if install_process.returncode != 0:
                    return "", f"Error installing dependencies:\n{install_process.stderr}"

            # 4. Run the actual script
            run_process = subprocess.run(
                [sys.executable, file_path],
                capture_output=True, text=True, timeout=60
            )
            return run_process.stdout, run_process.stderr

        except subprocess.TimeoutExpired:
            return "", "Execution timed out."
        except Exception as e:
            return "", f"An unexpected error occurred during execution: {e}"