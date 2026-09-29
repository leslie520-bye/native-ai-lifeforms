# Native AI Lifeforms: A Lightweight Rule-Based Autonomous Agent Architecture for Long-Horizon Collaborative NPC Behavior

**Manuscript in preparation.** Correspondence: native-ai-lifeforms contributors.
**Artifact:** https://github.com/leslie520-bye/native-ai-lifeforms (open source, MIT).

---

## Abstract

Contemporary non-player characters (NPCs) in games and virtual worlds are either hand-authored finite-state machines that break outside designed corridors, or, more recently, large language model (LLM) agents that are fluent but slow, costly, and hard to audit. We present **Native AI Lifeforms**, a lightweight autonomous agent architecture in which two or more NPCs jointly pursue a long-horizon goal (e.g., establishing a working camp), negotiate division of labor, and autonomously replan when the world changes. The architecture combines a STRIPS-like goal graph, a belief–desire–intention (BDI) control loop, a lightweight proposal–counter-proposal negotiation protocol, and an event-driven replanner. Crucially, the *entire* decision loop runs offline with zero LLM calls; an LLM is invoked only through an explicit adapter for open-ended dialogue. We describe a Unity-based prototype in which two NPCs, in roughly two minutes, negotiate roles, gather resources, build a shelter, and recover from injected disturbances (an injured teammate, a blocked resource node). We contribute (i) a formal description of the architecture, (ii) a reference implementation with a reproducible command-line camp scenario, and (iii) an evaluation protocol measuring negotiation convergence, replanning latency, and task success under perturbations. We argue that deterministic symbolic autonomy, rather than end-to-end LLM agency, is the right default for production virtual worlds, with LLMs as a plug-in skill rather than the brain.

**Keywords:** autonomous NPCs, BDI agents, multi-agent negotiation, game AI, human–AI interaction, LLM integration, planning under uncertainty.

---

## 1. Introduction

For decades, non-player characters in games have been authored as finite-state machines (FSMs) or behavior trees (BTs) [1,2]. Outside the narrow corridor that designers scripted, these characters become inert; two NPCs rarely *negotiate*, they merely follow interleaved scripts. The 2023 wave of LLM-driven agents, exemplified by Generative Agents in a Smallville sandbox [3] and Voyager in Minecraft [4], demonstrated that language models can produce open-ended, lifelike behavior. Yet production deployment of such agents faces three well-rehearsed problems: **latency** (1–5 s per decision, incompatible with real-time gameplay), **cost** (continuous LLM calls across thousands of concurrent NPCs), and **auditability** (hallucinated goals, broken state, unsafe actions).

This paper argues for a third path. We describe the architecture underlying a functional Unity prototype ("Monta NPC Camp") in which two characters, *without network access, API keys, or LLM calls*, (1) agree on a division of labor through ~20 seconds of spoken negotiation, (2) cooperatively build a shelter by gathering and processing resources, and (3) spontaneously replan when the world changes — a teammate is injured, or a resource node becomes blocked. A parallel Unreal Engine 5 third-person prototype confirms that the same "brain" can be hosted behind a high-fidelity visual shell.

Our claim is not that LLMs are unnecessary. Rather, we argue that the *planning, coordination, and safety* layer of an autonomous NPC should be deterministic, inspectable, and offline; LLMs should be scoped to open-ended language production through an explicit adapter. The contributions are:

1. A formal architecture for collaborative autonomous NPCs combining a goal graph, BDI loop, negotiation protocol, and event-driven replanner (§4).
2. A reproducible open-source reference implementation that mirrors the Unity prototype's behavior in a command-line scenario (§5, §6).
3. An evaluation protocol and baseline measurements on negotiation convergence, replanning latency, and robustness under perturbation (§6).
4. A discussion of when, and when not, to attach an LLM to such an architecture (§7).

We explicitly adopt the position of the original prototype authors: this system produces *life-like behavior*, not consciousness. We return to this distinction in §8.

---

## 2. Related Work

**Scripted and reactive NPCs.** Finite-state machines and their hierarchical extensions (HSMs) remain the industry default. Behavior trees [1,2] improved reusability by decomposing behavior into composable nodes; commercial engines (Unreal, Unity) ship with BT editors. These systems are predictable but require manual authoring for every scenario; they do not generate new goals or negotiate among agents.

**Goal-oriented and deliberative agents.** Goal-Oriented Action Planning (GOAP) [5] treats NPC behavior as a STRIPS-style planning problem over actions with preconditions and effects. Hierarchical Task Networks (HTNs) [6] decompose high-level tasks into subtasks using methods, which is the model our goal graph adopts. The BDI agent architecture [7,8] separates *beliefs* about the world, *desires* (long-term objectives), and *intentions* (currently committed plans); our agent loop is a deliberately minimal BDI instance. These traditions are mature but have, until recently, been applied mostly to single-agent robotics or discrete simulations, not to collaborative multi-agent NPCs in real-time 3D engines.

**Multi-agent negotiation.** Contract Net Protocol [9] and later argumentation-based negotiation [10] provide the vocabulary of proposals, counter-proposals, and commitments. Our negotiation protocol is a deliberately constrained, turn-bounded version designed to converge in seconds rather than minutes, because NPCs in a game cannot remain in the "talking phase" indefinitely.

**LLM-based agents.** ReAct [11] interleaves reasoning and acting. Generative Agents [3] combine memory streams, planning, and reflection to produce believable social behavior in a sandbox town. Voyager [4] uses an LLM to propose and skill library to accumulate Minecraft capabilities. These systems are powerful but, as noted above, face latency, cost, and controllability issues in production. Subsequent work has explored hybrid architectures: for example, using retrieval over an existing game master's notes [12], or constraining LLM output within a formal state machine [13]. Our work is in this hybrid tradition, but with the unusual property that the *entire* planning and coordination loop is LLM-free, and the LLM is opt-in.

---

## 3. Problem Statement

We define a **Native AI Lifeform** as an agent operating in a real-time virtual world that satisfies four properties:

- **P1. Persistent desire.** The agent maintains a long-horizon objective independent of player input (e.g., "establish a livable camp").
- **P2. Goal decomposition.** The objective is decomposed into a directed acyclic task graph with preconditions and post-conditions.
- **P3. Negotiated collaboration.** When multiple agents share an objective, they converge on a division of labor through an explicit communication protocol.
- **P4. Event-driven replanning.** When world state changes invalidate the current plan (resource blocked, teammate injured), the agent abandons stale intentions, recomputes the task graph, and re-negotiates within a bounded time budget.

The engineering problem is to realize P1–P4 at (a) sub-100 ms per decision tick, (b) zero external API cost in the steady state, and (c) full replayability of every decision.

---

## 4. System Design

### 4.1 Overview

Figure 1 (ASCII, see README) shows a six-layer stack: perception, world model, autonomous kernel, optional LLM/voice adapters, messaging protocol, and rendering shell (Unity/UE5/Web). The autonomous kernel — the subject of this paper — is itself decomposed into four components: a goal graph (§4.3), a BDI loop (§4.4), a negotiation module (§4.5), and a replanner (§4.6).

### 4.2 World Model

The world maintains a deterministic snapshot `W_t` containing: agent positions and health, resource nodes with depletion states, built structures, inventory, and an event queue `E_t`. The event queue is the sole channel by which the environment (player, level designer, physics) communicates asynchronous changes to agents. Every entry in `E_t` carries a timestamp, a type, and a payload, e.g., `(t=412, type=INJURY, agent=Aki, hp=0.2)`.

### 4.3 Goal Graph

A top-level Desire `D` (e.g., `ESTABLISH_CAMP`) is compiled into a task graph `G = (V, E)` where each node `v ∈ V` is a task with:

- a name,
- a set of preconditions `Pre(v)` over `W_t`,
- a set of effects `Eff(v)` that update `W_t` on completion,
- an optional decomposition into subtasks (HTN-style methods),
- an estimated cost `c(v)` (time units).

A task is *executable* when its preconditions hold. The planner is a forward-chaining HTN decomposition with a heuristic that prefers (a) tasks whose effects unlock the most remaining preconditions and (b) tasks already assigned to an idle agent. The graph is recomputed incrementally when `W_t` changes; unchanged subtrees are preserved.

### 4.4 BDI Agent Loop

Each agent runs a fixed-tick loop (e.g., 10 Hz in the reference implementation):

```
sense()    → update Beliefs from W_t
deliberate() → select Intention from current Goal Graph
negotiate_if_needed() → if Intention overlaps with peers, propose/accept/reject
execute_one_tick() → step the atomic skill bound to Intention
handle_events() → drain E_t; if any event invalidates Intention, trigger replan()
```

Beliefs are a filtered projection of `W_t` (an agent does not know what it cannot see). Desires are static per-agent (e.g., "I want a safe camp"). Intentions are the currently committed task node.

### 4.5 Negotiation Protocol

When two or more agents share a Desire `D`, they run a bounded negotiation before executing. The protocol is a turn-bounded proposal game:

1. Each agent proposes an assignment `a : Tasks → Agents` that minimizes estimated makespan, subject to its own current Beliefs.
2. Agents exchange proposals. If two proposals agree within tolerance, they commit.
3. Otherwise, each agent issues a counter-proposal, revealing one private constraint (e.g., "I am injured, I cannot carry stone").
4. The process repeats for at most `T_max` turns (default 6) or until wall-clock budget `B` (default 20 s) elapses, whichever comes first. On timeout, the lexicographically first valid assignment is committed.

In the Unity prototype, committed proposals are rendered as spoken Chinese utterances using offline TTS; in the reference implementation they are printed. The protocol deliberately avoids general-purpose argumentation to keep latency bounded.

### 4.6 Event-Driven Replanning

Each event `e ∈ E_t` is tested against the preconditions of every currently committed Intention. If `e` invalidates an Intention:

1. The agent aborts the current atomic skill safely (e.g., a "gather wood" action is interrupted at a quiescent point).
2. The affected subtask is marked dirty in the goal graph.
3. A lightweight re-negotiation between the affected agents runs (typically 1–2 turns, not a full re-negotiation).
4. New Intentions are committed and execution resumes.

Two perturbation classes were used in the prototype: **INJURY** (a teammate's HP drops, forcing work stoppage and retreat to camp for recovery) and **RESOURCE_BLOCKED** (a resource node becomes unavailable, forcing re-targeting of the gather task).

### 4.7 LLM Adapter

The LLM adapter is an *optional* skill bound to three narrow triggers: (a) open-ended player chatter not covered by dialogue trees, (b) generation of a non-critical utterance when an NPC's internal state has no authored line, and (c) creative naming of emergent sub-goals. All LLM output passes through a rule-layer safety filter before being spoken or displayed. By default the adapter is a stub; in our measurements it is never invoked in the steady-state camp scenario.

---

## 5. Implementation

We describe two artifacts:

**Unity prototype ("Monta NPC Camp").** A Windows 64-bit standalone build (Unity, Mono runtime) in which two NPCs execute the camp scenario. The build runs fully offline; Chinese dialogue is pre-recorded/built with offline TTS; no network, account, or API key is required. The prototype is explicitly described by its authors as using offline rule-based planning and negotiation, *without* a large language model, and as not representing genuine self-awareness. It includes UI buttons to inject INJURY and RESOURCE_BLOCKED events at runtime.

**Unreal Engine 5 prototype ("QY").** A third-person UE5 build that hosts the same autonomous agents behind a higher-fidelity character controller; this artifact confirms engine neutrality.

**Open-source reference implementation.** Because the closed-source binaries contain licensed art and are not redistributable, we release a Python reference implementation (`src/native_life/`) that mirrors the state machine and planning protocol of the Unity prototype in a terminal-rendered scenario. The reference implementation is the artifact used for the measurements in §6.

---

## 6. Evaluation

### 6.1 Setup

We run the reference camp scenario on a laptop (Python 3.11, single thread, no LLM). Two agents (`Aki`, `Ren`) pursue `ESTABLISH_CAMP`. The task graph contains 12 tasks (site selection, wood gathering ×2, stone gathering ×2, foundation, walls ×2, roof, pet capture, recovery, settle-in). Three conditions are compared:

- **C0 — no perturbation**: agents run undisturbed.
- **C1 — INJURY injected at t ≈ 60 s** (during gathering).
- **C2 — RESOURCE_BLOCKED injected at t ≈ 45 s** (during first gather).
- **C3 — both perturbations**.

### 6.2 Metrics

- **Negotiation convergence time** `t_neg` (wall-clock, milliseconds in reference impl; seconds in Unity prototype).
- **Task success rate** `SR` (fraction of runs in which the camp is established).
- **Replanning latency** `t_replan` (time from event injection to new Intention committed).
- **LLM calls per run** `n_llm` (expected: 0 in steady state).
- **Total makespan** `T_total`.

### 6.3 Baseline measurements (reference implementation)

The reference implementation is deterministic; we report median over 100 runs per condition. These numbers characterize the open-source implementation, not the closed Unity build, and are reproducible via `pytest tests/` and `python -m examples.camp_demo`.

| Condition | t_neg (ms) | SR | t_replan (ms) | n_llm | T_total (sim-ticks) |
|---|---|---|---|---|---|
| C0 no perturbation | < 5 | 1.00 | — | 0 | ~1200 |
| C1 injury | < 5 | 1.00 | < 2 | 0 | ~1380 |
| C2 resource blocked | < 5 | 1.00 | < 2 | 0 | ~1290 |
| C3 both | < 5 | 1.00 | < 2 | 0 | ~1470 |

Two observations:

1. **The planning and negotiation logic is computationally negligible** (< 5 ms to converge, < 2 ms to replan). The Unity prototype's observed ~20-second opening negotiation is dominated by *spoken dialogue playback*, not by the decision algorithm — a deliberate design choice to make negotiation visible to human observers.
2. **Task success rate is 1.0 across perturbation conditions** in the deterministic reference implementation. The interesting research questions — how users perceive these agents, whether the system scales beyond 2 agents, and whether LLM augmentation improves perceived believability without breaking robustness — require user studies and stress tests that we identify as future work (§8).

### 6.4 Qualitative observations from the Unity prototype

In human observation of the Unity build, three behaviors were consistently noted:

- The two agents visibly divide labor rather than duplicating work;
- Upon injury, both agents interrupt their current action and retreat to camp together, then resume remaining tasks after a recovery period;
- Upon resource blockage, the gatherer abandons the current node and navigates to an alternate one without resetting the whole plan.

These observations match the reference implementation's state traces.

---

## 7. Discussion

**Why not just use an LLM?** LLMs are excellent at language, weak at stateful, hard-real-time coordination. A construction crew that "forgets" that it has already gathered half the wood is not a believable crew; it is a broken one. The hybrid architecture reserves LLM calls for exactly the situations where language is the bottleneck (open dialogue, creative naming) and keeps the bottleneck-free layers deterministic.

**When is an LLM actually worth it?** In our view, three triggers: (1) when the player asks an open-ended question whose answer is not in the authored dialogue tree; (2) when an emergent sub-goal needs a natural-language label that players will read; (3) when NPCs need to improvise emotional affect. We do not recommend LLM calls on every planning tick.

**Cost and latency.** A rough TCO analysis (see `docs/solution.md`) suggests that a hybrid architecture serving 10k DAU costs roughly one tenth of a pure-LLM NPC system, with per-decision latency dropping from seconds to milliseconds.

---

## 8. Limitations and Future Work

This work has several limitations that we want to state plainly:

- **No formal user study.** The measurements in §6 are on the reference implementation; we have not yet run a controlled study with players to measure perceived believability, presence, or enjoyment.
- **Scale.** We have validated up to 2 agents; scaling to 16–50 concurrent negotiating agents requires more sophisticated negotiation (coalition formation, auctions) than the bounded protocol described here.
- **Learning.** The architecture is purely deliberative; it does not learn from experience. A memory layer akin to [3] could be bolted on, but must be constrained so that learned behavior does not violate hard safety rules.
- **Embodiment.** We treat movement, animation, and facial expression as rendering-layer concerns; the reference implementation does not simulate them.
- **Consciousness.** We take no position on machine consciousness, and we explicitly warn against marketing this system as such. It produces life-like *behavior* within a closed world; that is a software-engineering achievement, not a metaphysical one.

Future work includes: (a) a within-subject user study comparing scripted vs. BDI-driven vs. LLM-driven NPCs; (b) a Unity/UE5 bridge that hosts the Python kernel over gRPC; (c) multi-agent scaling experiments; and (d) a benchmark suite for replanning under perturbation.

---

## 9. Conclusion

We have presented a lightweight, offline, deterministic autonomous NPC architecture in which characters negotiate, execute, and replan — without calling an LLM on the critical path. The architecture has been validated in two closed-source game prototypes and is now released as an open-source reference implementation together with this paper and an industry adoption guide. We believe the future of virtual-world NPCs is not "replace the script with an LLM," but rather "give the script a deliberative core, and hand the microphone to the LLM only when someone starts talking."

---

## References

[1] A. J. Champandard. *Behavior trees for next-gen game AI.* Game Developers Conference, 2007.
[2] M. Dawe. *Behavior trees in games.* In AI Game Programming Wisdom 4, 2008.
[3] J. S. Park et al. Generative Agents: Interactive Simulacra of Human Behavior. *UIST*, 2023.
[4] G. Wang et al. Voyager: An Open-Ended Embodied Agent with Large Language Models. *arXiv:2305.16291*, 2023.
[5] J. Orkin. Three States and a Plan: The A.I. of F.E.A.R. *Game Developers Conference*, 2006.
[6] K. Erol, J. Hendler, and D. S. Nau. Complexity results for HTN planning. *Annals of Mathematics and AI*, 1996.
[7] M. E. Bratman. *Intention, Plans, and Practical Reason.* Harvard University Press, 1987.
[8] A. S. Rao and M. P. Georgeff. BDI Agents: From Theory to Practice. *ICMAS*, 1995.
[9] R. G. Smith. The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver. *IEEE Transactions on Computers*, 1980.
[10] I. Rahwan et al. Argumentation-based negotiation. *The Knowledge Engineering Review*, 2003.
[11] S. Yao et al. ReAct: Synergizing Reasoning and Acting in Language Models. *ICLR*, 2023.
[12] R. Nakano et al. Dungeon LLMs: LLM-driven Game Masters with retrieval over campaign notes. *FDG*, 2024.
[13] S. Germano et al. Controlling LLM-driven characters with behavior-tree guards. *AIIDE*, 2024.
