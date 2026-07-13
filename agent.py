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
    """今天用假工具：不管收到什么，都返回写死的内容。
    （为什么用假的？这样出问题时能确定是循环坏了，不是文件读取坏了。真工具周三换。）"""
    if name == "read_file":
        return "This is a fake file. It says: recursion is a function calling itself."
    return f"Error: tool '{name}' does not exist."


def try_parse(text):
    """把模型的文本变成三种结果之一:
    ("tool", dict) / ("final", str) / ("fail", 原始文本)"""
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        return ("fail", text)
    # TODO 1: 如果 d 里有 "tool" 这个 key → return ("tool", d)
    #         如果 d 里有 "final" 这个 key → return ("final", d["final"])
    #         都没有 → return ("fail", text)
    #         提示: 判断 dict 里有没有某个 key 的写法是  if "tool" in d:
    if "tool" in d:
        return ("tool", d)
    if "final" in d:
        return ("final", d["final"])
    return ("fail", text)


messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_task},
]

for step in range(5):  # 最多传 5 轮纸条，防止死循环
    print(f"\n===== 第 {step + 1} 轮 =====")

    resp = ollama.chat(model="qwen3.5:9b", messages=messages, think=False)

    # TODO 2: 从 resp 里取出模型说的话（一个字符串），存到变量 text
    #         提示: 实验 1 的第二个 print
    text = resp["message"]["content"]

    print("模型说:", text)

    # TODO 3: 把模型这句话追加进 messages，让它下一轮记得自己说过什么
    #         提示: 实验 2 的做法，role 用 "assistant"
    #         messages.append({...})
    messages.append({"role": "assistant", "content": text})
    kind, content = try_parse(text)

    if kind == "tool":
        result = run_tool(content["tool"], content["args"])
        print("工具返回:", result)
        # TODO 4: 把工具结果追加进 messages，让模型下一轮能看到
        #         role 用 "user"，content 写成 f"Tool result: {result}"
        messages.append({"role": "user", "content": f"Tool result:{result}"})

    elif kind == "final":
        print("\n🎉 最终回答:", content)
        break

    else:  # fail
        print("⚠️ 解析失败，模型的原始输出在上面 ↑（这是宝贵的实验数据，记进 devlog）")
        break
