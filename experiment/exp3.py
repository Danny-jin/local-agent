import json

# Experiment 3: string -> dict with json.loads

# Case 1: a clean JSON string -> parses into a dict
s1 = '{"tool": "read_file", "args": {"path": "devlog.md"}}'
d = json.loads(s1)
print(type(d))  # <class 'dict'> — parsed successfully, now a real dict
print(d["tool"])  # read_file
print(d["args"]["path"])  # devlog.md

# Case 2: a non-JSON string -> raises an exception
s2 = "Sure, let me read that file for you!"
try:
    json.loads(s2)
except json.JSONDecodeError:
    print("Parse failed! Raw content was:", s2)
