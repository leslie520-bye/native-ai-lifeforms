"""Atomic skills bound to task names.

A skill is a coroutine-like step function: each tick it does a small amount
of work, and returns True when the task is complete. Skills are where the
"embodiment" hooks live (in a real engine, they'd drive animation/navigation).
"""
from __future__ import annotations

from dataclasses import dataclass

from .world import World


@dataclass
class SkillProgress:
    task_name: str
    agent: str
    ticks_left: int


SKILL_DURATIONS = {
    "gather_wood": 20,
    "gather_stone": 20,
    "build_foundation": 15,
    "build_walls": 25,
    "build_roof": 15,
    "capture_pet": 20,
    "recover": 30,
}


class Skill:
    """A step-once-per-tick executor for one task, by one agent."""

    def __init__(self, task_name: str, agent: str, world: World) -> None:
        self.task_name = task_name
        self.agent = agent
        self.world = world
        self.ticks_left = SKILL_DURATIONS[task_name]

    def step(self) -> bool:
        """Advance one tick. Return True when the skill has finished."""
        self.ticks_left -= 1
        if self.ticks_left <= 0:
            self._finish()
            return True
        return False

    # internal ----------------------------------------------------------
    def _finish(self) -> None:
        w = self.world
        if self.task_name == "gather_wood":
            w.give("wood", 5)
            for node in w.resources.values():
                if node.kind == "wood" and not node.blocked and node.amount > 0:
                    node.amount -= 1
                    break
        elif self.task_name == "gather_stone":
            w.give("stone", 3)
            for node in w.resources.values():
                if node.kind == "stone" and not node.blocked and node.amount > 0:
                    node.amount -= 1
                    break
        elif self.task_name == "gather_wood":
            w.give("wood", 5)
        elif self.task_name == "build_foundation":
            w.take("wood", 2); w.take("stone", 1)
            w.structures["foundation"] = True
        elif self.task_name == "build_walls":
            w.take("wood", 2); w.take("stone", 2)
            w.structures["walls"] = True
        elif self.task_name == "build_roof":
            w.take("wood", 1)
            w.structures["roof"] = True
        elif self.task_name == "capture_pet":
            w.structures["pet"] = True
        elif self.task_name == "recover":
            w.agents[self.agent].hp = 1.0
