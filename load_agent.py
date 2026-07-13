import ollama
import os

# resp = ollama.chat(
#     model="qwen3.5:9b",
#     messages=[{"role": "user", "content": "explain recursion in one sentence"}],
#     think=False,
# )
system_prompt = """You could use the following tool: read_file(path: str) -> to return
the content of the file. When you need to use the tool, only output a single line
of json, no other words needed: {"tool": "read_file", "args": {"path": "..."}}
After getting the result of the tool, if you can give the answer, output:
{"final": "your final answer"}
"""

user_task = "Summarize the file at: /Users/jinzhiyuan/local-agent/devlog.md"

message = [system_prompt, user_task]


def read_file(path: str):
    # return "This is a fake file content about recursion."
    with open(path, "r") as file:
        content = file.read()
        return content


def try_parse(out):
    if "tool" in out:
        if out["tool"] == "read_file":
            return read_file(out["args"]["path"])
    return "No tool has been used"


history = []
out = ollama.chat(
    model="qwen3.5:9b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_task},
    ],
    think=False,
)
print(out)
message.append(try_parse(out))

final_output = ollama.chat(
    model="qwen3.5:9b",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message[-1]},
    ],
    think=False,
)

print(final_output["message"]["content"])
# use_tool = True
# for step in range(5):
#     while use_tool:
#         out = ollama.chat(
#             model="qwen3.5:9b", messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_task},
#         ],
#         think=False,
#         )
#         history.append(out)
#         use_tool = False


# print(resp["message"]["content"])
