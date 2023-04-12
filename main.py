import os
import time

import openai
from langchain.utilities import PythonREPL

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


def pull_out_code(text):
    # This assumes that the code is the first block of code in the text.
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
    try:
        exec(code)
        return locals()
    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    #     code = """
    # x = 42
    # y = 3
    # print(x + y)
    #     """
    code = generate_code("Write a program to print out a chess board in ASCII with the pieces in random positions.")
    # print(f"Got response: {code}")
    code = pull_out_code(code)
    print(f"Got code:")
    for l in code.splitlines():
        print(f"> {l}")

    results = run_code(code)
    if 'error' in results:
        print('Error:', results['error'])
    else:
        print('Results:', results)

    python_repl = PythonREPL()
    python_repl.run(code)
    print('Results:', python_repl.locals)
