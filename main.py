# IMPORTANT!
# Run `pip install openai langchain numpy pandas matplotlib pygame` to install these libraries

import io
import os
import sys
import time
from unittest.mock import patch

import openai
from langchain import OpenAI

# Set up your API key for OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

# Import some common libraries to be used by generated code
# noinspection PyUnresolvedReferences
import random
# noinspection PyUnresolvedReferences
import numpy
# noinspection PyUnresolvedReferences
import pandas
# noinspection PyUnresolvedReferences
import matplotlib
# noinspection PyUnresolvedReferences
import pygame

globals_dict = {'__name__': '__main__'}


def generate_code(prompt="", model="gpt-3.5-turbo", n=1, temperature=0.0, max_tokens=1024, system_description="You write code. You do not write anything that isn't code.", messages=None):
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
        n=n,
    )
    answers = []
    for i in range(n):
        ans = response.choices[i].message.content.strip()
        answers.append(ans)
    duration = time.perf_counter() - start_time
    # print(f"Duration: {duration:.2f} seconds: {answers[0][:20]}")
    if n == 1:
        return answers[0]
    return answers


def edit_code(code, prompt):
    response = openai.Edit.create(model="code-davinci-edit-001", input=code, instruction=prompt)
    return response.choices[0].text


def try_fix_code(code, error):
    # TODO Should maybe incorporate the line number of the error too
    prompt = f"I ran this code and got this error:\n\n{error}\n\nPlease fix the code so that it runs without error."
    return edit_code(code, prompt)


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


if __name__ == '__main__':
    task_gen_llm = OpenAI(temperature=1.0)
    task = task_gen_llm("I'm a beginner who's learning to code in Python and pygame. Give me a simple and easy assignment to get started learning to make a simple simulation.")
    print(f"Task: {task.strip()}\n")
    code = generate_code(task)
    # print(f"Got response: {code}")
    code = pull_out_code(code)
    print_code(code)
    print("\nRunning Code:\n")

    output, locals_from_run = run_code(code)
    print(output)
    # print('Locals:', dict(filter(lambda x: not x[0] in ["code", "simulate_user_input", "error"], locals_from_run.items())))
    error = None
    if 'error' in locals_from_run:
        error = locals_from_run['error']

    # Handle errors
    while error is not None:
        print('Got Error, trying to fix:', error)
        code = try_fix_code(code, error)
        print_code(code)
        output, locals_from_run = run_code(code)
        print(output)
        error = None
        if 'error' in locals_from_run:
            error = locals_from_run['error']
        # Sleep 500ms
        time.sleep(0.5)

    # Add tests
    add_test(code)

    if error is None:
        print('\nSuccess!')

    # python_repl = PythonREPL()
    # python_repl.run(code)
    # print('Results:', python_repl.locals)
    # if 'error' in python_repl.locals:
    #     print('Error:', python_repl.locals['error'])
