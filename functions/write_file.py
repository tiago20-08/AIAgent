import os

def write_file(working_directory, file_path, content):
    working_directory = os.path.abspath(working_directory)
    file = os.path.join(working_directory, file_path)
    
    if not file.startswith(working_directory):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    
    try:
        if not os.path.exists(file):
            os.makedirs(os.path.dirname(file), exist_ok=True)
    except Exception as e:
        return f"Error, cannot make directory: {e}"
    
    try:
        with open(file, "w") as f:
            f.write(content)
    except Exception as e:
        return f"Error writing to file: {e}"
    
    return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'