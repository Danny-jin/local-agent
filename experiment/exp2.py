import ollama

# 第一轮：告诉它一个信息
r1 = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "我叫 Isaac，记住我的名字。"}],
    think=False,
)
print("第一轮回复:", r1["message"]["content"])

# 第二轮 A：只发新问题（错误做法）
r2 = ollama.chat(
    model="qwen3.5:9b",
    messages=[{"role": "user", "content": "我叫什么名字？"}],
    think=False,
)
print("只发新问题:", r2["message"]["content"])

# 第二轮 B：把历史全部带上（正确做法）
r3 = ollama.chat(
    model="qwen3.5:9b",
    messages=[
        {"role": "user", "content": "我叫 Isaac，记住我的名字。"},
        {
            "role": "assistant",
            "content": r1["message"]["content"],
        },  # 模型自己上轮说的话
        {"role": "user", "content": "我叫什么名字？"},
    ],
    think=False,
)
print("带上历史:", r3["message"]["content"])
