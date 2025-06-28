import os

def get_file_content(working_directory, file_path):
    working_directory = os.path.abspath(working_directory)
    file = os.path.join(working_directory, file_path)
    
    if not file.startswith(working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    MAX_CHARS = 10000

    try:
        with open(file, "r") as f:
            file_content_string = f.read(MAX_CHARS + 1)
    except Exception as e:
        return f"Error: {e}"
    
    if len(file_content_string) > MAX_CHARS:
        file_content_string = file_content_string[:MAX_CHARS]
        file_content_string += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
    return file_content_string
