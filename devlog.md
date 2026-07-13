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
