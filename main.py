import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types
from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file
from functions.run_python import run_python_file


def main():
    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    verbose = "--verbose" in sys.argv
    

    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("Error, prompt is not provided.")
        sys.exit(1)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    generate_content(client, messages, verbose)



def generate_content(client, messages, verbose):

    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

    model_name = "gemini-2.0-flash-001"

    schema_get_files_info = types.FunctionDeclaration(
        name="get_files_info",
        description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "directory": types.Schema(
                    type=types.Type.STRING,
                    description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
                ),
            },
        ),
    )

    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Read and show the file's content.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to show, relative to the working directory.",
                ),
            },
            required=["file_path"]
        ),
    )
    
    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Run the Python file.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the Python file to run, relative to the working directory.",
                ),
                "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to the Python file.",
                ),
                    description="Optional arguments to pass to the Python file.",
                ),
            },
            required=["file_path"],
        )
    )

    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Write the given word/s in the file.",
        parameters=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "file_path": types.Schema(
                    type=types.Type.STRING,
                    description="The path to the file to write in, relative to the working directory.",
                ),
                "content": types.Schema(
                    type=types.Type.STRING,
                    description="The content the user asked to write in the file.",
                )
            },
            required=["file_path", "content"]
        ),
    )

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file
        ]
    )

    for i in range(20):
        res = client.models.generate_content(
            model=model_name,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt
            )
        )

        prompt = res.usage_metadata.prompt_token_count
        response = res.usage_metadata.candidates_token_count

        for candidate in res.candidates:
            messages.append(candidate.content)

        if res.function_calls:
            for function_call_part in res.function_calls:
                function_call_result = call_function(function_call_part, verbose)

                try:
                    response = function_call_result.parts[0].function_response.response
                except Exception:
                    raise Exception("Fatal error")

                if verbose:
                    print(f"-> {response.get('result')}")

                messages.append(function_call_result)
            continue
        else:
            print("Response:\n")
            print(res.text)
            break




def call_function(function_call_part, verbose=False):
    name = function_call_part.name
    args = function_call_part.args
    args["working_directory"] = "./calculator"


    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")
    
    function_map = {
        "get_file_content": get_file_content,
        "get_files_info": get_files_info,
        "write_file": write_file,
        "run_python_file": run_python_file,
    }

    func = function_map.get(name)

    if not func:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=name,
                    response={"error": f"Unknown function: {name}"},
                )
            ],
        )

    try:
        function_result = func(**args)
    except Exception as e:
        function_result = f"Error during execution: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=name,
                response={"result": function_result},
            )
        ],
    )




if __name__ == "__main__":
    main()