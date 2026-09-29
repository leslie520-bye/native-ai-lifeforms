"""STRIPS/HTN-style task graph.

A top-level Desire (e.g. ESTABLISH_CAMP) is decomposed into a DAG of tasks.
Each task has preconditions over the world, effects it applies on completion,
and an estimated cost in ticks.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .world import World


@dataclass
class Task:
    name: str
    preconditions: Callable[[World], bool]
    effects: Callable[[World], None]
    cost: int = 10
    subtasks: List["Task"] = field(default_factory=list)
    completed: bool = False
    assigned_to: Optional[str] = None

    def is_ready(self, w: World) -> bool:
        if self.completed:
            return False
        if self.subtasks:
            return all(s.completed for s in self.subtasks)
        return self.preconditions(w)


def _enough_wood(w: World) -> bool: return w.has("wood", 5)
def _enough_stone(w: World) -> bool: return w.has("stone", 3)
def _foundation_built(w: World) -> bool: return w.structures["foundation"]
def _walls_built(w: World) -> bool: return w.structures["walls"]
def _roof_built(w: World) -> bool: return w.structures["roof"]
def _always(w: World) -> bool: return True


def build_camp_goal_graph() -> Task:
    """Construct the ESTABLISH_CAMP task graph used in the camp demo.

    Layout (simplified vs. the Unity prototype, but same spirit):

        ESTABLISH_CAMP
        ├── gather_wood (needs an unblocked wood node)
        ├── gather_stone (needs an unblocked stone node)
        ├── build_foundation (needs wood>=2, stone>=1)
        ├── build_walls (needs foundation, wood>=2, stone>=2)
        ├── build_roof (needs walls, wood>=1)
        └── capture_pet (independent, optional flavor)
    """
    root = Task(name="ESTABLISH_CAMP", preconditions=_always, effects=lambda w: None, cost=1)

    gather_wood = Task(
        name="gather_wood",
        preconditions=lambda w: any(
            r.kind == "wood" and not r.blocked and r.amount > 0
            for r in w.resources.values()
        ),
        effects=lambda w: (w.give("wood", 5),),
        cost=20,
    )
    gather_stone = Task(
        name="gather_stone",
        preconditions=lambda w: any(
            r.kind == "stone" and not r.blocked and r.amount > 0
            for r in w.resources.values()
        ),
        effects=lambda w: (w.give("stone", 3),),
        cost=20,
    )
    build_foundation = Task(
        name="build_foundation",
        preconditions=lambda w: w.has("wood", 2) and w.has("stone", 1),
        effects=lambda w: (w.take("wood", 2), w.take("stone", 1),
                           setattr(w.structures, "foundation", True)),
        cost=15,
    )
    build_walls = Task(
        name="build_walls",
        preconditions=lambda w: w.structures["foundation"] and w.has("wood", 2) and w.has("stone", 2),
        effects=lambda w: (w.take("wood", 2), w.take("stone", 2),
                           setattr(w.structures, "walls", True)),
        cost=25,
    )
    build_roof = Task(
        name="build_roof",
        preconditions=lambda w: w.structures["walls"] and w.has("wood", 1),
        effects=lambda w: (w.take("wood", 1),
                           setattr(w.structures, "roof", True)),
        cost=15,
    )
    capture_pet = Task(
        name="capture_pet",
        preconditions=lambda w: any(
            r.kind == "pet" and not r.blocked and r.amount > 0
            for r in w.resources.values()
        ),
        effects=lambda w: setattr(w.structures, "pet", True),
        cost=20,
    )

    for t in (gather_wood, gather_stone, build_foundation, build_walls, build_roof, capture_pet):
        root.subtasks.append(t)
    return root


def ready_tasks(root: Task, w: World) -> List[Task]:
    """Return incomplete, ready tasks in dependency order."""
    out: List[Task] = []
    for t in root.subtasks:
        if t.is_ready(w):
            out.append(t)
    return out
