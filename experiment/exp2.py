import ollama

# Experiment 2: the model has NO memory — "conversation" only exists
# because the program re-sends the full history every time.

# Round 1: tell it a fact
r1 = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "My name is Isaac. Remember my name."}],
    think=False,
)
print("Round 1 reply:", r1["message"]["content"])

# Round 2 A: send only the new question (wrong way)
r2 = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "What is my name?"}],
    think=False,
)
print("New question only:", r2["message"]["content"])

# Round 2 B: include the full history (right way)
r3 = ollama.chat(
    model="qwen3.5:9b",
    messages=[
        {"role": "user", "content": "My name is Isaac. Remember my name."},
        {
            "role": "assistant",
            "content": r1["message"]["content"],
        },  # the model's own reply from last round
        {"role": "user", "content": "What is my name?"},
    ],
    think=False,
)
print("With history:", r3["message"]["content"])
