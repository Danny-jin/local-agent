import ollama

resp = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "explain recursion in one sentence"}],
    think=False,
)
print(resp["message"]["content"])
