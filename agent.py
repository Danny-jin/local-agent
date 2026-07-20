from pathlib import Path
import ollama
import json

system_prompt = """You can use the following tool:
- read_file(path: str) -> returns the content of the file

When you need the tool, output ONLY one line of JSON, nothing else:
{"tool": "read_file", "args": {"path": "..."}}

After you receive the tool result, if you can answer, output ONLY:
{"final": "your final answer"}
"""

user_task = "Use the web_search tool web_search(url) to get the weather today"

ALLOWED_DIR = Path(__file__).parent.resolve()
MAX_CHARS = 3000


def read_file(path_str):
    """Real Tool. Always returns a string; errors come back as 'Error: ,,,'
    so the model can see them and react (never raises)."""

    try:
        p = Path(path_str)
        if not p.is_absolute():
            # Join the path together
            p = ALLOWED_DIR / p
        p = p.resolve()
        if not p.is_relative_to(ALLOWED_DIR):
            return f"Error: access denied, path outside allowed directory {path_str}"
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return f"Error: file not found {path_str}"
    except IsADirectoryError:
        return f"Error: path is a directory, not a file {path_str}"
    except UnicodeDecodeError:
        return f"Error: not a UTF-8 text file: {path_str}"
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + f"\n...[truncated, {len(text)} chars total]"
    return text


def run_tool(name, args):
    """W1-c: dispatch to real tools. Unknown tool names return an Error
    string (never raise) so the model can see the failure and react."""
    if name == "read_file":
        return read_file(args.get("path", ""))
    return f"Error: tool '{name}' does not exist."


def try_parse(text):
    """Parse the model's raw text into one of three outcomes:
    ("tool", dict) / ("final", str) / ("fail", raw_text)"""
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        return ("fail", text)
    if "tool" in d:
        return ("tool", d)
    if "final" in d:
        return ("final", d["final"])
    return ("fail", text)


# only when directly running python agent.py the following will be executed
if __name__ == "__main__":
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_task},
    ]

    for step in range(5):  # step limit: prevents infinite loops
        print(f"\n===== Step {step + 1} =====")

        resp = ollama.chat(model="qwen3.5:9b", messages=messages, think=False)

        text = resp["message"]["content"]
        print("Model says:", text)

        # Append the model's own reply so it remembers what it said next round
        messages.append({"role": "assistant", "content": text})
        kind, content = try_parse(text)

        if kind == "tool":
            result = run_tool(content["tool"], content["args"])
            print("Tool returned:", result)
            # Feed the tool result back so the model sees it next round
            messages.append({"role": "user", "content": f"Tool result: {result}"})

        elif kind == "final":
            print("\nFinal answer:", content)
            break

        else:  # fail
            print(
                "Parse failed. Raw model output above — valuable failure data, log it in devlog."
            )
            break
