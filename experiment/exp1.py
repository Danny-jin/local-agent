import ollama

# Experiment 1: what do ollama.chat's input and output look like?

resp = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "Explain recursion in one sentence"}],
    think=False,
)

print("=== Full response object ===")
print(resp)
print()
print("=== Only the model's reply text ===")
print(resp["message"]["content"])
