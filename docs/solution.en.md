# Native AI Lifeforms: Industry Adoption Playbook (EN Summary)

**v0.1 · 2026-09**
Full Chinese version: [`solution.md`](solution.md) · Paper: [`paper.md`](paper.md)

---

## TL;DR

We show that NPCs in virtual worlds can be made to look *alive* — pursuing their own goals, negotiating with each other, and replanning when things go wrong — **without calling an LLM on the critical path**, fully offline, at millisecond latency, at roughly **one-tenth the running cost of a pure-LLM NPC system**.

LLMs are kept as a plug-in adapter for open-ended dialogue. The planning, coordination, and safety layer is deterministic, inspectable, and auditable.

## The gap today

| NPC type | How it's driven | Where it breaks |
|---|---|---|
| Scripted / behavior tree | Hand-authored | Outside the designed corridor |
| LLM agent | LLM on every tick | Latency, cost, hallucinated goals, unsafe actions |
| **Native AI Lifeform (this)** | Symbolic deliberative core + LLM adapter | Deterministic, offline, cheap |

## Architecture (six layers)

```
L6 Render:       Unity / Unreal / Web / digital human
L5 Protocol:     gRPC / WebSocket, JSON, event bus
L4 Adapters:     LLM (open dialogue) · TTS (voice) · safety filter
L3 Autonomous:  BDI · goal graph (HTN) · negotiation · replanning   ← zero LLM
L2 World model:  state snapshot · inventory · teammates · events
L1 Perception:   engine callbacks · sensors · player · environment
```

Three rules:
1. **L3 never calls an LLM.** It works offline, during network outages, and at scale.
2. **L4 is pluggable.** LLM output must pass a rule-layer safety filter before reaching the player.
3. **Everything is serializable.** What an NPC is doing and why is replayable.

## Five verticals

### 1. Games (open-world / MMO / single-player)
- Give town NPCs persistent desires (open shop, patrol, find a thief); they keep acting when the player looks away.
- Party members negotiate loot and tactics, cover when a teammate falls.
- Dynamic world events trigger genuine behavior change, not cut-scenes.
- LLM only for free-form chat; combat, pathing, quest gating stay on rules.
- **Cost reference:** a 20-NPC mid-size town is ~2 person-months of integration; LLM chat adds < ¥0.05 DAU-day.

### 2. Digital humans / live commerce / customer service
- Rules own the *flow*: product order, dwell time, upsell timing, compliance filters.
- LLM owns the *improv*: answering a barrage of live comments.
- Event replanning maps to incidents: out-of-stock → switch to a substitute; hostile chat → fall back to compliant scripted lines.

### 3. Cultural tourism / theme parks / museums
- A virtual guide has its own schedule: welcomes at the gate in the morning, "rests" at the tea house at noon, leads school groups in the afternoon, says goodbye at closing.
- On-device deployment: weak hotel Wi-Fi, no API keys.
- IoT hooks: closing bell → the guide actually says "time to go home" instead of looping a welcome.

### 4. Simulation training (emergency, medical, military, customer-service sandboxes)
- Every "trainee counterpart" is a lifeform with its own physiology, emotion, and goals (survive, ask for help, refuse to cooperate).
- Instructors inject events (fire spreads, someone collapses, comms down); lifeforms genuinely change behavior rather than following a script.
- Full logs auto-generate a training-after-action report.
- LLM only for in-character *lines*; the emotions and decisions stay on rules.

### 5. Ed-companionship (children, elderly)
- The companion has its own day: hungry in the morning, needs help on a task in the afternoon, "sleeps" at night.
- It does not lecture; it runs into its own problems ("I want to cross the river but can't swim") and invites the child to collaborate.
- **Hard safety:** rule-layer whitelist on every LLM utterance; no voice upload to the cloud.

## Cost comparison (10k DAU, monthly, RMB)

| Approach | Rules dev | LLM spend | Infra | Total / month |
|---|---|---|---|---|
| Pure script | low | 0 | low | ~20k |
| Pure LLM agent | 0 | 300k–800k | high | **350k–850k** |
| **Hybrid (this)** | mid (2–3 person-months) | 20k–60k | mid | **40k–90k** |

Hybrid: **~1/10 the pure-LLM running cost**, per-decision latency from seconds to <50 ms.

## 18-month roadmap

| Phase | Months | Deliverable |
|---|---|---|
| P0 Validation | M1–M2 | Replicate the Monta camp loop in your vertical, offline demo |
| P1 Productize | M3–M5 | SDK + Unity/Unreal plugins + 10 sample NPCs |
| P2 LLM hybrid | M6–M9 | Real LLM adapter, safety filters, cost dashboard |
| P3 Scale | M10–M14 | 50+ concurrent NPCs, visual behavior editor |
| P4 Cross-industry | M15–M18 | Reuse into a second/third vertical |

## Risks & ethics

| Risk | Mitigation |
|---|---|
| Marketing as "conscious AI" | Keep the prototype authors' disclaimer: life-like *behavior*, not consciousness. |
| LLM hallucination in safety-critical settings | Rule-layer gate before TTS/on-screen; medical/legal/child-facing paths disable open generation. |
| Unpredictable behavior | Hard per-NPC constraints (can't hurt the player, can't leave bounds); replanning passes a whitelist. |
| Cost blow-up | LLM calls rate-limited by NPC × duration × whitelisted topics; budget exhaustion auto-degrades to rules-only. |

## Starting now

1. Run `python -m examples.camp_demo`.
2. Pick one NPC in your product and ask:
   - What is its desire *today*?
   - If the world changes, how should it re-plan?
   - Which step actually needs an LLM?
3. Start from L3 (the rules core). Plug in the LLM at P2.
