"""Deterministic world state and event bus.

The world is the single source of truth. Agents read from it; the only way
the environment (player, level designer, physics) changes it asynchronously
is by pushing entries onto ``event_queue``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(order=True)
class Event:
    """A timestamped world event. ``order=True`` lets us sort by tick."""
    tick: int
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceNode:
    name: str
    kind: str           # "wood" | "stone" | "pet"
    amount: int
    blocked: bool = False


@dataclass
class AgentState:
    name: str
    hp: float = 1.0
    position: str = "camp"
    inventory: Dict[str, int] = field(default_factory=dict)
    current_task: Optional[str] = None


class World:
    """A minimal, serializable world snapshot."""

    def __init__(self) -> None:
        self.tick: int = 0
        self.agents: Dict[str, AgentState] = {}
        self.resources: Dict[str, ResourceNode] = {}
        self.structures: Dict[str, bool] = {
            "foundation": False,
            "walls": False,
            "roof": False,
            "pet": False,
        }
        self.inventory: Dict[str, int] = {"wood": 0, "stone": 0}
        self.event_queue: List[Event] = []

    # -- agent / resource plumbing ---------------------------------------
    def add_agent(self, name: str) -> None:
        self.agents[name] = AgentState(name=name)

    def add_resource(self, node: ResourceNode) -> None:
        self.resources[node.name] = node

    # -- event bus ------------------------------------------------------
    def push_event(self, type_: str, payload: Optional[Dict[str, Any]] = None,
                   at_tick: Optional[int] = None) -> None:
        self.event_queue.append(Event(
            tick=self.tick if at_tick is None else at_tick,
            type=type_,
            payload=payload or {},
        ))

    def drain_events(self) -> List[Event]:
        self.event_queue.sort(key=lambda e: e.tick)
        ready = [e for e in self.event_queue if e.tick <= self.tick]
        self.event_queue = [e for e in self.event_queue if e.tick > self.tick]
        return ready

    # -- tick -----------------------------------------------------------
    def step(self) -> None:
        self.tick += 1

    # -- helpers used by skills ----------------------------------------
    def has(self, item: str, n: int) -> bool:
        return self.inventory.get(item, 0) >= n

    def take(self, item: str, n: int) -> None:
        if self.inventory.get(item, 0) < n:
            raise ValueError(f"not enough {item}")
        self.inventory[item] -= n

    def give(self, item: str, n: int) -> None:
        self.inventory[item] = self.inventory.get(item, 0) + n
