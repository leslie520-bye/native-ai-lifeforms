"""BDI agent loop.

Each agent is an independent loop, but they share a *plan board* (a
blackboard) on which a single coordinator writes the task assignment each
tick. This avoids the two agents independently negotiating and double-booking
the same task.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from . import negotiation as neg
from .skills import Skill
from .task_graph import Task, ready_tasks
from .world import World


class PlanBoard:
    """Shared blackboard: task_name -> agent_name."""

    def __init__(self) -> None:
        self.assignment: Dict[str, str] = {}


class BDIAgent:
    def __init__(self, name: str, world: World, root: Task,
                 board: PlanBoard,
                 peers: Optional[List[str]] = None,
                 logger=None) -> None:
        self.name = name
        self.w = world
        self.root = root
        self.board = board
        self.peers = peers or []
        self.log = logger or (lambda msg: None)
        self.current_skill: Optional[Skill] = None

    # -- BDI cycle ------------------------------------------------------
    def sense(self) -> None:
        pass

    def maybe_replan(self) -> None:
        """Called once per tick by the coordinator (not per-agent).

        Recomputes the shared assignment. Cheap: < 5 ms.
        """
        ready = ready_tasks(self.root, self.w)
        if not ready:
            return
        # in-flight = tasks currently being executed by anyone.
        in_flight: Dict[str, str] = {}
        for a in self.w.agents.values():
            if a.current_task:
                in_flight[a.current_task] = a.name
        all_agents = list(self.w.agents.keys())
        self.board.assignment = neg.negotiate(
            all_agents, ready, self.w, in_flight=in_flight,
        )

    def execute(self) -> None:
        # If the world says we're not on a task but we still hold a skill,
        # it was aborted by an event (injury, blocked resource) -- drop it.
        if self.current_skill is not None and self.w.agents[self.name].current_task is None:
            self.log(f"  [{self.name}] interrupted {self.current_skill.task_name}")
            self.current_skill = None

        # If already running a skill, step it.
        if self.current_skill is not None:
            done = self.current_skill.step()
            if done:
                self._complete_current()
            return

        # Pick up the task assigned to us on the shared board.
        my_task = next((t for t, a in self.board.assignment.items()
                         if a == self.name and not self._is_done(t)), None)
        if my_task is None:
            if self.w.agents[self.name].hp < 0.5:
                self.log(f"  [{self.name}] hurt -> resting")
                self.w.agents[self.name].current_task = "recover"
                self.current_skill = Skill("recover", self.name, self.w)
            return

        self.w.agents[self.name].current_task = my_task
        self.log(f"  [{self.name}] start {my_task}")
        self.current_skill = Skill(my_task, self.name, self.w)

    # -- helpers --------------------------------------------------------
    def _is_done(self, task_name: str) -> bool:
        for t in self.root.subtasks:
            if t.name == task_name:
                return t.completed
        return True

    def _complete_current(self) -> None:
        task_name = self.current_skill.task_name
        for t in self.root.subtasks:
            if t.name == task_name and not t.completed:
                t.completed = True
                t.assigned_to = self.name
                self.log(f"  [{self.name}] done  {task_name}")
        self.w.agents[self.name].current_task = None
        self.current_skill = None
        self.board.assignment.pop(task_name, None)


def all_done(root: Task) -> bool:
    return all(t.completed for t in root.subtasks)
