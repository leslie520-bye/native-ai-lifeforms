# Contributing to Native AI Lifeforms

Thanks for your interest! This project is young and we welcome issues,
scenarios, bridges, and documentation.

## Development setup

```bash
git clone https://github.com/leslie520-bye/native-ai-lifeforms.git
cd native-ai-lifeforms
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate
pip install -e ".[dev]"
```

Run the demo:

```bash
python -m native_life
python -m examples.camp_demo --events injury,block
```

Run tests:

```bash
pytest
```

## What we especially want

1. **New scenarios.** The camp demo is a minimal proof of concept. If you
   swap the task graph for a hospital ward, a space station, or a market
   stall, open a PR — that's how we stress the architecture.
2. **Engine bridges.** The Python kernel talks to a `World` interface.
   A `UnityBridge` or `UnrealBridge` that mirrors game state into this
   world is the single highest-leverage contribution.
3. **Negotiation improvements.** The current protocol is a simple
   load-balancing greedy assignment. Real multi-agent negotiation
   (argumentation, auctions, coalition formation) is on the roadmap.
4. **LLM adapter implementations.** We ship a stub. A working
   `OpenAIAdapter`, `vLLMAdapter`, or local-LLM adapter with a safety
   filter is very welcome.

## Code style

- Pure Python standard library on the runtime path; `pytest` is dev-only.
- Keep modules small and importable without side effects.
- Every new capability should come with a test under `tests/`.

## Ethics line

This architecture produces life-like *behavior*. It is **not** conscious,
and we will not merge marketing, demos, or docs that suggest otherwise.
Keep that distinction explicit in any PR that touches user-facing text.
