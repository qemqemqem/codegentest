# noinspection PyUnresolvedReferences
import os
import random
import string
import time

import openai
from langchain import OpenAI

# Set up your API key for OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]


def generate_code(question="", model="gpt-3.5-turbo", n=1, temperature=0.0, max_tokens=256, system_description="You write code. You do not write anything that isn't code.", messages=None):
    start_time = time.perf_counter()
    prompt = f"{question} "
    response = openai.ChatCompletion.create(
        # https://openai.com/blog/introducing-chatgpt-and-whisper-apis
        model=model,
        messages=messages if messages is not None else [
            {"role": "system", "content": system_description},
            {"role": "user", "content": "You are a coding API. You write code with no explanation except comments in the code. After printing out the code, please end. \n\nTo start with, please write a \"Hello world\" program in Python"},
            {"role": "assistant", "content": "```\nprint(\"Hello, World!\")  # I understand that all comments go here\n```"},
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
    print(f"Duration: {duration:.2f} seconds: {answers[0][:20]}")
    if n == 1:
        return answers[0]
    return answers


def edit_code(code, prompt):
    response = openai.Edit.create(model="code-davinci-edit-001", input=code, instruction=prompt)
    return response.choices[0].text


def try_fix_code(code, error):
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
        simulate_user_input("5", lambda: exec(code))
        return locals()
    except Exception as e:
        return {'error': str(e)}


def print_code(code):
    print(f"Got code:")
    for l in code.splitlines():
        print(f"> {l}")


if __name__ == '__main__':
    # code = "a = blork(5)\nprint(a)"
    # code = edit_code(code, "Replace blork with a function that adds 5 to the input")
    # print("Fixed code:", code)
    # exit()

    task_gen_llm = OpenAI(temperature=1.0)
    task = task_gen_llm("I'm a beginner who's learning to code in Python. I'm taking my second class in Python. Give me a simple but whimsical assignment to get started.")
    print(f"Task: {task}")
    code = generate_code(task)
    # print(f"Got response: {code}")
    code = pull_out_code(code)
    print_code(code)
    print("\nRunning Code:\n")

    locals_from_run = run_code(code)
    # print('Locals:', dict(filter(lambda x: not x[0] in ["code", "simulate_user_input", "error"], locals_from_run.items())))
    error = None
    if 'error' in locals_from_run:
        error = locals_from_run['error']

    # Handle errors
    while error is not None:
        print('Got Error, trying to fix:', error)
        code = try_fix_code(code, error)
        print_code(code)
        locals_from_run = run_code(code)
        # print('Locals:', dict(filter(lambda x: not x[0] in ["code", "simulate_user_input", "error"], locals_from_run.items())))
        error = None
        if 'error' in locals_from_run:
            error = locals_from_run['error']

    if error is None:
        print('\nSuccess!')

    # python_repl = PythonREPL()
    # python_repl.run(code)
    # print('Results:', python_repl.locals)
    # if 'error' in python_repl.locals:
    #     print('Error:', python_repl.locals['error'])
