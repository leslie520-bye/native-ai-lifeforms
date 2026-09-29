# We open-sourced Native AI Lifeforms: NPCs that negotiate, plan, and replan — without calling an LLM

**Release v0.1 · 2026-09-29 · MIT License**

> Repo: [github.com/leslie520-bye/native-ai-lifeforms](https://github.com/leslie520-bye/native-ai-lifeforms)

---

## The problem we kept hitting

For the last two years, every game or virtual-world project we've touched has asked the same question:

> *"Can our NPCs feel alive? Like they're doing something even when the player isn't watching?"*

We tried the obvious answers. Neither worked in production:

- **Hand-authored behavior trees** break the moment a player steps off the designer's rails. They scale linearly with the number of NPCs, and they never, *ever* surprise you.
- **LLM-driven agents** (the Generative Agents / Voyager wave) are genuinely impressive in demos — but in production they cost a fortune, take 1–5 seconds to decide, and hallucinate goals that break your state machine. We saw one NPC "decide" to build a second roof.

So we built the thing in the middle: a deterministic, offline, sub-millisecond autonomy kernel that makes NPCs look alive, with an LLM adapter sitting next to it for *when* you actually need language.

## What it does

This repo packages what we learned from two closed-source Windows prototypes — a Unity "NPC camp" demo and an Unreal Engine 5 third-person scene — into a readable, runnable reference implementation.

Run it:

```bash
git clone https://github.com/leslie520-bye/native-ai-lifeforms.git
cd native-ai-lifeforms
python -m examples.camp_demo --events injury,block
```

You'll watch two agents, **Aki** and **Ren**, do this:

1. **Negotiate** who gathers wood, who gathers stone, and who captures the pet;
2. **Execute in parallel** — one chops, one mines, both build;
3. When you inject an **injury event**, the hurt agent drops its tool and retreats to recover; the other *notices*, re-plans, and picks up the half-finished wall;
4. When you **block a resource node**, the gatherer abandons it and walks to an alternate one — without resetting the whole plan.

All of this runs in **~100 ticks, zero LLM calls, zero network, zero API keys**.

## Why not just use an LLM?

This is the question we get most, so let's be direct.

We are *not* saying LLMs are bad. We're saying they're the wrong tool for 90% of an NPC's tick:

| Decision type | Today | Why |
|---|---|---|
| "Should I keep gathering wood or start the roof?" | Rule kernel | Hard real-time, must be correct, cheap |
| "What do I say to the player who just walked up?" | LLM adapter | Open-ended language, can afford latency |
| "Is my teammate hurt? Should I help?" | Rule kernel | Safety-critical, must be deterministic |
| "Name the new quest I just made up" | LLM adapter | Creativity |

**The brain is small, the mouth is loud.** The planning, coordination, and safety layer is structured and inspectable; the LLM is one skill among many, and can be swapped out for a stub without anything breaking.

In the reference implementation, the LLM adapter *is* a stub. That's on purpose.

## What's inside

```
native-ai-lifeforms/
├── src/native_life/
│   ├── world.py          # deterministic world state + event queue
│   ├── task_graph.py     # STRIPS/HTN goal decomposition
│   ├── agent.py          # BDI loop + shared plan board
│   ├── negotiation.py    # bounded proposal/counter-proposal protocol
│   ├── replanner.py      # event-driven replanning
│   ├── skills.py         # atomic actions (gather, build, rest, ...)
│   └── llm_adapter.py    # optional LLM hook (default: no-op)
├── examples/camp_demo.py # the CLI camp you just ran
├── tests/                # three scenarios, all passing
├── docs/solution.md      # industry adoption playbook (Chinese)
└── docs/paper.md          # academic write-up (English)
```

We also published two long-form documents alongside the code:

- **`docs/solution.md`** — an industry playbook covering five verticals (games, digital humans, cultural tourism, simulation training, ed-companionship), a TCO comparison showing the hybrid architecture costs ~1/10 of a pure-LLM NPC system, and an 18-month roadmap.
- **`docs/paper.md`** — a paper-length write-up (Related Work through Limitations) suitable for venues like AIIDE, FDG, or CHI Play.

## Numbers you can reproduce

These come from the reference implementation, not the closed Unity build:

| Condition | Time to negotiate | Time to replan | LLM calls | Camp built? |
|---|---|---|---|---|
| No perturbation | < 5 ms | — | 0 | ✅ |
| Teammate injured | < 5 ms | < 2 ms | 0 | ✅ |
| Resource blocked | < 5 ms | < 2 ms | 0 | ✅ |
| Both events | < 5 ms | < 2 ms | 0 | ✅ |

The Unity prototype's famous ~20-second opening negotiation is *spoken dialogue playback*, not planning time. The algorithm converges in milliseconds; the characters just need to *say* the agreement out loud so humans can read it.

## Design philosophy

1. **Deterministic first, probabilistic second.** If a rule can do it, don't call an LLM.
2. **Auditable > clever.** Every NPC can tell you, at any tick, what it's doing and why.
3. **We are not building consciousness.** We're building *behaviors that look alive*. The original Unity prototype authors were explicit about this, and we're keeping that line in the docs. Marketing this as "AI that is alive" would be both false and irresponsible.
4. **Engine-neutral.** The Python brain talks to the world through a message bus. Unity, Unreal, Web, or a digital-human runtime can all sit behind it.

## Roadmap

- [x] **v0.1** — reference core (goal graph / BDI / negotiation / replanning), industry playbook, paper draft
- [ ] **v0.2** — gRPC bridge to Unity / UE5, so the Python brain can drive the actual game builds
- [ ] **v0.3** — real LLM adapter (local vLLM or cloud), with a safety filter on every utterance
- [ ] **v0.4** — scale from 2 to 16 concurrent agents, plus a visual inspector

## Try it, break it, tell us

We'd genuinely love issues that say:

- *"I swapped the camp scenario for a hospital ward and X broke."*
- *"Your negotiation protocol deadlocks when three agents disagree."*
- *"Here's a 47-agent battle royale that exposes a real problem."*

The code is MIT. Bring your own world.

---

**Links**
- Repo: [github.com/leslie520-bye/native-ai-lifeforms](https://github.com/leslie520-bye/native-ai-lifeforms)
- Industry playbook: [`docs/solution.md`](docs/solution.md)
- Paper: [`docs/paper.md`](docs/paper.md)
- License: MIT
