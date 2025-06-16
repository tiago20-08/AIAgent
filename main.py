import os
from dotenv import load_dotenv
from google import genai
import sys
from google.genai import types

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


    res =  client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
    )

    prompt = res.usage_metadata.prompt_token_count
    response = res.usage_metadata.candidates_token_count

    if verbose:
        print(f"Prompt tokens: {prompt}")
        print("--------------------------")
        print(f"Response tokens: {response}")
        print("--------------------------")
    print("Response:\n")
    print(res.text)


if __name__ == "__main__":
    main()