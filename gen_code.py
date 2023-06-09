import io
# Import some common libraries to be used by generated code
import random  # noqa
import sys
import time
from unittest.mock import patch

import matplotlib  # noqa
import numpy  # noqa
import openai
import pandas  # noqa
import pygame  # noqa

globals_dict = {'__name__': '__main__'}


def generate_code(prompt="", model="gpt-3.5-turbo", temperature=0.0, max_tokens=1024, system_description="You write code. You do not write anything that isn't code.", messages=None):
    code = ""
    while code == "":
        start_time = time.perf_counter()
        response = openai.ChatCompletion.create(
            # https://openai.com/blog/introducing-chatgpt-and-whisper-apis
            model=model,
            messages=messages if messages is not None else [
                {"role": "system", "content": system_description},
                {"role": "user", "content": "You are a coding API. You write code with no explanation except comments in the code. You write functional code, and then write a small amount of code to use the function(s) you wrote. After printing out the code, please end. \n\nTo start with, please write a \"Hello world\" program in Python"},
                {"role": "assistant", "content": "```\ndef say_hello():\tprint(\"Hello, World!\")  # I understand that all comments go here\n\nsay_hello()\n```"},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            n=1,
        )
        code = response.choices[0].message.content.strip()
        temperature += 0.2  # If we iterate, get more random
        if code == "":
            print("Got empty code, trying again")
    duration = time.perf_counter() - start_time
    # print(f"Duration: {duration:.2f} seconds: {answers[0][:20]}")
    return code


def edit_code(code, prompt, model="code-davinci-edit-001"):
    if model == "code-davinci-edit-001":
        for _ in range(5):
            try:
                response = openai.Edit.create(model="code-davinci-edit-001", input=code, instruction=prompt)
                return response.choices[0].text
            except openai.error.APIError as e:
                print("Got error from OpenAI:", e)
                time.sleep(1)
    else:
        # Assume it's GPT 3 or 4
        prompt = f"I ran this code:\n\n```\n{code}\n```\n\n{prompt}"
        return pull_out_code(generate_code(prompt, model=model))


def try_fix_code(code, error, model="code-davinci-edit-001"):
    # TODO Should maybe incorporate the line number of the error too
    prompt = f"I got this error:\n\n{error}\n\nPlease fix the code so that it runs without error."
    return edit_code(code, prompt, model)


def try_incorporate_user_feedback(code, feedback, model="code-davinci-edit-001"):
    prompt = f"{feedback}. Please incorporate this feedback into the code."
    return edit_code(code, prompt, model)


def pull_out_code(text):
    # This assumes that the code is the first block of code in the text. # TODO Need to do a better job pulling it out, but hopefully the prompt will make it easy.
    lines = text.splitlines()
    code = ""
    found_code = False
    for line in lines:
        if line.startswith('```'):
            if found_code:
                break
            found_code = True
            continue
        if found_code:
            code += line + "\n"
    return code


def run_code(code):
    def simulate_user_input(input_string, func):
        with patch('builtins.input', return_value=input_string):
            return func()

    try:
        # Redirect stdout to a string buffer
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf

        print("\033[94m\033[1m")  # Blue
        simulate_user_input("5", lambda: exec(code, globals_dict))
        print("\033[0m\033[0m")

        # Restore stdout and get the output
        sys.stdout = old_stdout
        output = buf.getvalue()
        return output, locals()
    except Exception as e:
        return "", {'error': str(e)}


def add_test(code):
    prompt = f"I have this code that I'd like to add tests to:\n\n{code}\n\nPlease add a test or tests for the code. Do not use a testing library, just def functions."
    tests = generate_code(prompt)
    tests = pull_out_code(tests)
    print(f"\nGot tests: \n{tests}")
    # Run test and see if it passes
    print("\nRunning tests:")
    output, results = run_code(code + "\n\n" + tests)
    print(output)
    # print(results)
    # # Determine whether tests passed or failed
    if 'error' in results or "AssertionError" in output:
        print('Tests failed, trying to fix them')
    #     # Tests failed, so try to fix them
    #     tests = try_fix_code(tests, results['error'])
    #     print(f"Got fixed tests: {tests}")
    #     results = run_code(code + "\n\n" + tests)
    #     print(results)
    else:
        print('Tests passed')


def print_code(code):
    print(f"Got code:")
    for l in code.splitlines():
        print(f"> {l}")
