"""Event-driven replanning.

When an event invalidates a committed intention, we abort the current skill,
mark the affected task dirty, and let the next BDI tick re-negotiate.
"""
from __future__ import annotations

from typing import Optional, Tuple

from .world import Event, World


def handle_event(event: Event, w: World) -> Optional[Tuple[str, str]]:
    """Apply an event to the world. Return (agent_to_interrupt, new_task_name)
    if an agent's current intention should be aborted, else None.
    """
    if event.type == "INJURY":
        victim = event.payload["agent"]
        w.agents[victim].hp = 0.2
        # The victim drops whatever it was doing; peers keep working.
        # The victim will self-route to "recover" on the next tick because
        # execute() starts a recover skill when hp < 0.5 and idle.
        w.agents[victim].current_task = None
        return (victim, "recover")

    if event.type == "RESOURCE_BLOCKED":
        node = event.payload["node"]
        if node in w.resources:
            w.resources[node].blocked = True
        # Abort any agent currently gathering from a now-blocked node.
        for a in w.agents.values():
            if a.current_task in {"gather_wood", "gather_stone"}:
                a.current_task = None
                return (a.name, a.current_task or "replan")
        return None

    if event.type == "RESOURCE_UNBLOCKED":
        node = event.payload["node"]
        if node in w.resources:
            w.resources[node].blocked = False

    return None
