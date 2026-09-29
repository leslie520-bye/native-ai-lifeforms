"""native_life: a lightweight autonomous NPC (Native AI Lifeform) reference implementation.

Modules:
    world       -- deterministic world state and event queue
    task_graph  -- STRIPS/HTN-style goal graph
    skills      -- atomic skills (gather, build, rest, ...)
    agent       -- BDI agent loop
    negotiation -- bounded proposal/counter-proposal protocol
    replanner   -- event-driven replanning
    llm_adapter -- optional LLM hook (default: no-op stub)
"""

__version__ = "0.1.0"
