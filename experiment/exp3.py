import json

# 情况 1：干净的 JSON 字符串 → 能翻译成 dict
s1 = '{"tool": "read_file", "args": {"path": "devlog.md"}}'
d = json.loads(s1)
print(type(d))  # <class 'dict'>  —— 翻译成功，现在是真 dict 了
print(d["tool"])  # read_file
print(d["args"]["path"])  # devlog.md

# 情况 2：不是 JSON 的字符串 → 翻译会“爆炸”（抛异常）
s2 = "好的，我来帮你读文件！"
try:
    json.loads(s2)
except json.JSONDecodeError:
    print("解析失败！原始内容是:", s2)
