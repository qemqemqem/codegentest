# IMPORTANT!
# Run `pip install openai langchain numpy pandas matplotlib pygame` to install these libraries
# You also need to set a OPENAI_API_KEY environment variable to your OpenAI API key

import os

import openai
from langchain import OpenAI

# Set up your API key for OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

from gen_code import *

if __name__ == '__main__':
    task_gen_llm = OpenAI(temperature=1.0)
    task = task_gen_llm("I'm learning to program videogames in pygame. Please give me a simple programming task.")
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
