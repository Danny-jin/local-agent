# Devlog

_This document records the failures I encountered during implementation._

## 07/06/2026

**What I did today:** Installed Ollama and set up the model; it now runs on my GPU.

**Where I got stuck:**

1. `brew install ollama` only installs the Ollama app (the local inference server). The Python client library is a separate package — I also needed `pip install ollama` inside my venv before `import ollama` could work.
2. Got a KeyError printing `resp["messages"]["content"]`. Lesson: the _request_ takes `messages` (plural — the whole conversation history as a list), but the _response_ contains `message` (singular — the one new reply), and the text is in `resp["message"]["content"]`.
3. First run seemed to hang: the model defaults to thinking mode AND the 6.6GB model had to cold-load into GPU memory, so the (non-streaming) call stayed silent for over a minute. Setting `think=False` skips the thinking phase; once the model is warm in memory, responses come back in ~1-2s.
