import os
import subprocess


def run_scripts(directory):
    """
    Get list of all files in directory
    """
    files = os.listdir(directory)

    # Filter only Python files starting with 'run'
    python_files = [file for file in files if file.endswith(
        '.py') and file.startswith('run_wait')]

    # Run each script
    for script in python_files:
        try:
            subprocess.run(['python', script], shell=False, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running {script}: {e}")


if __name__ == "__main__":

    # Get current directory if no input provided
    cur_dir = os.getcwd()
    run_scripts(cur_dir)
