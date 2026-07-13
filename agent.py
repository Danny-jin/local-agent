import ollama
import json

system_prompt = """You can use the following tool:
- read_file(path: str) -> returns the content of the file

When you need the tool, output ONLY one line of JSON, nothing else:
{"tool": "read_file", "args": {"path": "..."}}

After you receive the tool result, if you can answer, output ONLY:
{"final": "your final answer"}
"""

user_task = "Summarize the file at /Users/jinzhiyuan/local-agent/devlog.md"


def run_tool(name, args):
    """W1-b: fake tool — always returns a hardcoded string, ignores args.
    (Why fake? If something breaks today, we know it's the loop/parser,
    not file I/O. The real tool comes in W1-c.)"""
    if name == "read_file":
        return "This is a fake file. It says: recursion is a function calling itself."
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
        print("Parse failed. Raw model output above — valuable failure data, log it in devlog.")
        break
