from agent import read_file
from agent import run_tool

print("1.", read_file("devlog.md")[:80])  # happy path → real content
print("2.", read_file("no_such_file.md"))  # → Error: file not found
print("3.", read_file("experiment"))  # → Error: is a directory
print("4.", read_file("../../etc/passwd"))  # → Error: access denied
print(run_tool("web_search", {"query": "weather"}))
