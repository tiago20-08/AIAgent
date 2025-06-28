import os
import subprocess

def run_python_file(working_directory, file_path, args=None):
    working_directory= os.path.abspath(working_directory)
    file = os.path.abspath(os.path.join(working_directory, file_path))

    if not file.startswith(working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(file):
        return f'Error: File "{file_path}" not found.'
    
    if not file.endswith(".py"):
        return f'Error: "{file_path}" is not a Python file.'
    
    try:
        commands = ["python", file]
        if args:
            commands.extend(args)
        res = subprocess.run(commands, capture_output=True, timeout=30, text=True, cwd= working_directory)
        output= []

        if res.stdout.strip():
            output.append("STDOUT:\n" + res.stdout.strip())

        if res.stderr.strip():
            output.append("STDERR:\n" + res.stderr.strip())

        if res.returncode != 0:
            output.append(f"Process exited with code {res.returncode}")

        if not output:
            return "No output produced."
        
        return "\n\n".join(output)

    except Exception as e:
        return f"Error executing Python file: {e}"