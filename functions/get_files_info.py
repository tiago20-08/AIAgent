import os

def get_files_info(working_directory, directory=None):
    working_directory = os.path.abspath(working_directory)
    if directory:
        d_path = os.path.abspath(os.path.join(working_directory, directory))
      
        if not d_path.startswith(working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        
        if not os.path.isdir(d_path):
            return f'Error: "{directory}" is not a directory'
    
    else:
        d_path = working_directory

    try:
        ret = ""

        for cont in os.listdir(d_path):
            path = os.path.join(d_path, cont)
            ret += f"- {cont}: file_size={os.path.getsize(path)} bytes, is_dir={os.path.isdir(path)}\n"
        return ret
    except Exception as e:
        return f"Eror listing files: {e}"

    