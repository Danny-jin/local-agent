# Devlog

_This document records the failures I encountered during implementation._

## 07/06/2026

**What I did today:** Installed Ollama and set up the model; it now runs on my GPU.

**Where I got stuck:**

1. `brew install ollama` only installs the Ollama app (the local inference server). The Python client library is a separate package — I also needed `pip install ollama` inside my venv before `import ollama` could work.
2. Got a KeyError printing `resp["messages"]["content"]`. Lesson: the _request_ takes `messages` (plural — the whole conversation history as a list), but the _response_ contains `message` (singular — the one new reply), and the text is in `resp["message"]["content"]`.
3. First run seemed to hang: the model defaults to thinking mode AND the 6.6GB model had to cold-load into GPU memory, so the (non-streaming) call stayed silent for over a minute. Setting `think=False` skips the thinking phase; once the model is warm in memory, responses come back in ~1-2s.

## 07/13/2026

**What I did today:** Set up the basic agent loop with tool use (fake tool): custom JSON protocol → parse → execute → feed result back, end to end.

**Where I got stuck:**

1. The model's output is always just a string. Even though I asked it to output JSON format, I still need `json.loads(output)` to convert that string into a real dict before I can read keys from it (`loads` for strings; `load` is for file objects).
2. If I call `ollama.chat` each time without updating the `messages` list, the model won't remember the previous conversation — the "memory" only exists because I append every turn to `messages` and re-send the whole history.
3. There are three roles in `messages`: `system` for the system prompt, `user` for the human's input, `assistant` for the model's own previous output.
4. After every tool call, the tool result must be appended back into `messages`, so in the next round the model knows it already received the result.
5. Appended the **parsed dict** to `messages` instead of the model's raw text — crashed on round 2 because a message's `content` must be a string. Lesson: the history stores what the model literally said, not my interpretation of it.
6. `try_parse` had no fallback return, so valid JSON without a "tool"/"final" key returned `None` → `TypeError` when unpacking. Lesson: every branch of a parser needs an explicit return.

**First step tomorrow:** Poke the loop on purpose (tasks that need no tool / hallucinated tool names / same task ×3 to check format stability), then swap the fake tool for the real `read_file`.

## 07/20/2026 (W1-c: real read_file, end to end)

**What I did today:** Swapped the fake `read_file` for the real one — the model can now read local files and answer based on their actual content, end to end. The tool never raises: every failure comes back as an `Error: ...` string appended to messages, so the model can see it and react (this is what lets the loop survive a nonexistent path instead of dying in a traceback). Guards implemented: path allowlist (`resolve()` before `is_relative_to()`, so `../` tricks can't escape the repo), file-not-found / is-a-directory / not-UTF-8 handling, and truncation at 3000 chars.

**Failure classification table** (raw material for W1-d — fix the most common category first):

| # | Task | Symptom (raw output snippet) | Category |
|---|------|------------------------------|----------|
| 1 | Summarize devlog.md ×10 (exp5 stability run) | **6/10 succeeded** (clean 6/10 — no tool errors in any run). 4 fails, all step-1/2 parse fails: run 3 = perfect JSON wrapped in ```json fence · run 5 = fence + extra closing brace `}}}` · run 4 = final answer with the closing `}` missing (cut-off generation) · run 10 = valid JSON but wrong schema `{"error": ...}` — invented its own key AND claimed the file missing without ever calling the tool. Full evidence: `experiment/exp5_results.md` | Broken format: fence ×3, cut-off ×1, malformed ×1, schema violation ×1 |
| 2 | Task says just `devlog.md` (relative) | Earlier ad-hoc runs: ~50% → `Error: file not found`. **Not** a tool bug — repo-relative join means the literal string `devlog.md` always resolves; the failing runs were the *model* emitting a different path string (temperature). Note: in the controlled exp5 ×10, path guessing never appeared (all 6 successes clean) — the earlier 50% likely came from different task phrasing; keep watching. | Bad path (model-side path guessing) |
| 3 | Read README.md → one sentence | Correct, clean run | — |
| 4 | Read notes/plan.md (nonexistent) | Model saw `Error: file not found` and answered honestly that the file doesn't exist; loop survived (error-as-string design validated) | Bad path — handled |
| 5 | "What is recursion? Explain in one sentence" (no tool needed) | Answered directly, no unnecessary tool call | — (no odd behavior) |
| 6 | `Use the web_search tool ...` (hallucinated name) | Model obeyed the user's fake tool instead of refusing per the system prompt's tool list (rambled about the signature, invented a DuckDuckGo URL), then half-recovered in a final admitting it couldn't. Output was a 4-in-1 format specimen: leaked `</think>` tag (despite think=False) + chatter + TWO JSON candidates in one reply (fenced tool call, then a final) + double-encoded JSON inside the final. Parse failed at step 1, so the run_tool fallback branch (`Error: tool does not exist`) was never actually reached — still untested; rerun until a clean `{"tool": "web_search"...}` parses to watch the model react to the Error. | Hallucinated tool name (induced) + Broken format |

**Where I got stuck:**

1. `ModuleNotFoundError` running `python experiment/exp4_readfile.py`: Python's module search path starts from the *script's own directory*, not the terminal's cwd, so `agent.py` at repo root wasn't findable. Fix: run `python -m experiment.exp4_readfile` from the repo root — `-m` puts the current directory on the search path.
2. The agent loop lived at module top level, so `from agent import read_file` executed the whole loop before exp4 could run. Wrapped the loop in `if __name__ == "__main__":` — now importing only brings in the functions; the loop runs only when the file is executed directly. Lesson: import runs all top-level code.
3. Suspected an odd/even alternating parse failure — disproved it with a repeated-run tally: no strict alternation, just default temperature (~0.8) sampling making the output format vary run to run. Same root cause as the path-guessing in table row 2. Lesson: distinguish systematic bugs from stochastic behavior by running the experiment, not by pattern-matching 3 data points. (`options={"temperature": 0, "seed": 42}` pins outputs for controlled tests; keeping defaults for normal runs — format instability IS the project.)

**First step tomorrow (W1-d):** Fix the two model-side instabilities the table exposed: ① strip markdown fences / chatter before `json.loads` + one retry on parse failure (Broken format); ② add one system-prompt line — paths are relative to the repo root, use file names exactly as given (Bad path, model side); ③ per-round request/response logging to a file, so failure evidence stops depending on scrollback.
