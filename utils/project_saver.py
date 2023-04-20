import os


def save_file(project_name, file_name, contents):
    dir_name = project_name.lower().replace(" ", "_")
    # Create directory if it doesn't exist
    if not os.path.exists("saves/" + dir_name):
        os.makedirs("saves/" + dir_name)
    with open("saves/" + dir_name + "/" + file_name, "w") as f:
        f.write(contents)


def format_file_contents(prompt, code):
    fc = ""
    for line in prompt.strip().split("\n"):
        fc += "# " + line + "\n"
    fc += "\n"
    fc += code
    return fc
