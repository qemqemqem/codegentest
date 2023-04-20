# IMPORTANT!
# Run `pip install openai langchain numpy pandas matplotlib pygame` to install these libraries
# You also need to set a OPENAI_API_KEY environment variable to your OpenAI API key
import difflib
import os

import openai
from langchain import OpenAI

from utils.config_loader import Config
from utils.project_saver import save_file, format_file_contents

# This is similar to main.py, but it loads a config and also saves code to a file

# Set up your API key for OpenAI
openai.api_key = os.environ["OPENAI_API_KEY"]

from gen_code import *

if __name__ == '__main__':
    # Load from config file
    config = Config('game_config.txt')
    print(f"Got Config: {config.__dict__}")

    # Create a task to work on
    if config.use_task_gen:
        task_gen_llm = OpenAI(temperature=1.0)
        task = task_gen_llm(config.description)
        print(f"Task: {task.strip()}\n")
    else:
        task = config.description

    # User feedback
    task_done = False

    # Generate code
    code = generate_code(task)
    code = pull_out_code(code)
    print_code(code)

    # Loop until the user thinks it's good
    while not task_done:
        print("\nRunning Code:\n")
        output, locals_from_run = run_code(code)
        print(output)
        error = None
        if 'error' in locals_from_run:
            error = locals_from_run['error']

        if config.auto_debug:
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
                time.sleep(0.5)
                if error is None:
                    print('\nDebugging Success!')

        if config.auto_test:
            # Add tests
            add_test(code)

        # Ask the user how it is
        if config.user_review:
            print('What do you think? (Press enter if good, or type notes if more work is needed)')
            user_input = input()
            if user_input == '':
                task_done = True
            else:
                print("Editing code...")
                new_code = try_incorporate_user_feedback(code, user_input)
                print(f"Got new code: {code}")
                # Compute the difference between the two codes
                diff = difflib.ndiff(code.splitlines(keepends=True), new_code.splitlines(keepends=True))
                print("Diff:" + ''.join(diff))
                code = new_code
        else:
            task_done = True  # If no user review, then we're done after debugging and testing

    # Save file
    save_file(config.name, "main.py", format_file_contents(task, code))
