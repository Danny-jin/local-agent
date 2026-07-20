"""exp5: format-stability tally — run the same task N times, count outcomes.

Usage (from repo root):  python -m experiment.exp5_stability

For each run: fresh conversation, same loop as agent.py, three possible outcomes:
  success    — reached a "final" answer
  parse_fail — model output wasn't parseable JSON (fence / chatter / cut-off)
  max_steps  — never reached final within the step limit

Also records any tool errors seen along the way (e.g. model guessed a bad path),
so successful-but-bumpy runs are visible too. Raw evidence is saved to
experiment/exp5_results.md — paste the interesting bits into the devlog table.
"""

from datetime import datetime

import ollama

from agent import system_prompt, run_tool, try_parse

TASK = "Summarize devlog.md in 3 bullet points."
RUNS = 10
MAX_STEPS = 5
MODEL = "qwen3.5:9b"

results = []  # (run_no, outcome, evidence)

for run in range(1, RUNS + 1):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": TASK},
    ]
    outcome = "max_steps"
    evidence = ""

    for step in range(MAX_STEPS):
        resp = ollama.chat(model=MODEL, messages=messages, think=False)
        text = resp["message"]["content"]
        messages.append({"role": "assistant", "content": text})

        kind, content = try_parse(text)
        if kind == "tool":
            result = run_tool(content["tool"], content["args"])
            messages.append({"role": "user", "content": f"Tool result: {result}"})
            if result.startswith("Error:"):
                # run may still recover — log what path/tool the model tried
                evidence += f"[step {step + 1} tool error] model said: {text}\n"
        elif kind == "final":
            outcome = "success"
            break
        else:  # parse fail — keep the raw output, this is the valuable part
            outcome = "parse_fail"
            evidence += f"[step {step + 1} parse fail] raw output:\n{text}\n"
            break

    results.append((run, outcome, evidence))
    print(f"run {run:2d}: {outcome}" + ("  (see evidence)" if evidence else ""))

ok = sum(1 for _, o, _ in results if o == "success")
clean = sum(1 for _, o, e in results if o == "success" and not e)
print(f"\nSuccess rate: {ok}/{RUNS}  (clean, no tool errors on the way: {clean}/{RUNS})")

with open("experiment/exp5_results.md", "w", encoding="utf-8") as f:
    f.write(f"# exp5 stability tally — {datetime.now():%Y-%m-%d %H:%M}\n\n")
    f.write(f"Task: {TASK}\nModel: {MODEL}\n")
    f.write(f"Success: {ok}/{RUNS} (clean: {clean}/{RUNS})\n\n")
    for run_no, outcome, evidence in results:
        f.write(f"## run {run_no}: {outcome}\n\n")
        if evidence:
            f.write("```\n" + evidence + "```\n\n")

print("Raw evidence saved to experiment/exp5_results.md")
