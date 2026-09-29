"""Bounded multi-agent negotiation protocol.

The real Unity prototype spends ~20 seconds *speaking* the negotiation.
Here we model the decision part: a turn-bounded proposal/counter-proposal
game that converges in a handful of iterations. The spoken lines are a
rendering concern, not a planning concern.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .task_graph import Task
from .world import World


@dataclass
class Proposal:
    agent: str
    assignment: Dict[str, str]   # task_name -> agent_name
    makespan: int


def negotiate(agents: List[str], ready_tasks: List[Task],
              w: World, in_flight: Optional[Dict[str, str]] = None,
              max_turns: int = 6) -> Dict[str, str]:
    """Converge on a task-to-agent assignment.

    ``in_flight`` maps tasks already being executed (task_name -> agent) so
    that re-negotiation does not double-book an agent who is mid-task.
    """
    if not ready_tasks:
        return {}

    in_flight = in_flight or {}
    ordered = sorted(ready_tasks, key=lambda t: -t.cost)
    # Tasks already in flight are locked to their current owner; only assign
    # ready tasks that nobody is working on yet.
    locked = {t: a for t, a in in_flight.items()
              if not _task_done(w, t)}
    free = [t for t in ordered if t.name not in locked]

    load: Dict[str, int] = {a: 0 for a in agents}
    assignment: Dict[str, str] = dict(locked)
    # Seed load from locked work so fresh tasks go to the less-loaded agent.
    for tname, agent in locked.items():
        for t in ordered:
            if t.name == tname:
                load[agent] += t.cost
                break

    for t in free:
        candidates = [a for a in agents
                      if not (w.agents[a].hp < 0.3 and t.name in
                              {"gather_stone", "build_walls"})]
        if not candidates:
            candidates = agents
        chosen = min(candidates, key=lambda a: load[a])
        assignment[t.name] = chosen
        load[chosen] += t.cost

    return assignment


def _task_done(w: World, task_name: str) -> bool:
    # Cheap mirror of task completion; agents pass completed tasks via the
    # task graph, but negotiation only sees World. We treat known-done
    # structures as proxies.
    proxies = {
        "build_foundation": w.structures["foundation"],
        "build_walls": w.structures["walls"],
        "build_roof": w.structures["roof"],
        "capture_pet": w.structures["pet"],
    }
    return proxies.get(task_name, False)
