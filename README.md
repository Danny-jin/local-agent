# Local Agent

## Project Introduction

Make a small model (qwen3.5:9b) running on your Mac call tools reliably, and quantify exactly where it falls short.

## Failure Modes

Big models are trained for tool use, but a small model will hallucinate the name of a tool that doesn't exist, or loop forever without giving a final answer.

## Architecture

```
user task → [1] prompt builder → [2] local model (Ollama) → [3] output parser
                  ↑                                              │
                  │                                    ┌─────────┴─────────┐
                  │                                tool call          final answer
                  │                                    │                   │
                  └──── feed result back ── [4] tool executor          → user

[5] main loop: wires it all together + step limit
```

## Roadmap

- **W1:** minimal ReAct loop + one real tool (`read_file`), end to end
- **W2:** error handling / retries + a small eval set (tool-call success rate)
- **W3:** reliability improvements; compare homemade protocol vs Ollama's native tool API
