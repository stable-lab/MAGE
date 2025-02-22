import re


def add_lineno(file_content: str) -> str:
    lines = file_content.split("\n")
    ret = ""
    for i, line in enumerate(lines):
        ret += f"{i+1}: {line}\n"
    return ret


def reformat_json_string(output: str) -> str:
    # in gemini, the output has markdown surrounding the json string
    # like ```json ... ```
    # we need to remove the markdown
    # remove by using regex between ```json and ```
    pattern = r"```json(.*?)```"
    try:
        match = re.search(pattern, output, re.DOTALL)
        return match.group(1).strip()
    # if not match, it also works
    except AttributeError:
        return output
