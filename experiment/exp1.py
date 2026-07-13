import ollama

resp = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "用一句话解释递归"}],
    think=False,
)

print("=== 整个响应对象 ===")
print(resp)
print()
print("=== 只有模型说的话 ===")
print(resp["message"]["content"])
