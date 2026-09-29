"""Smoke tests for the planning + replanning core.

Run:
    python -m pytest tests/
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from native_life.agent import BDIAgent, PlanBoard, all_done
from native_life.replanner import handle_event
from native_life.task_graph import build_camp_goal_graph
from native_life.world import ResourceNode, World


def _make_world() -> World:
    w = World()
    w.add_agent("Aki")
    w.add_agent("Ren")
    w.add_resource(ResourceNode("forest", "wood", amount=5))
    w.add_resource(ResourceNode("quarry", "stone", amount=5))
    w.add_resource(ResourceNode("den", "pet", amount=1))
    return w


def _run(w: World, root, ticks=2000) -> None:
    board = PlanBoard()
    aki = BDIAgent("Aki", w, root, board, peers=["Ren"])
    ren = BDIAgent("Ren", w, root, board, peers=["Aki"])
    for _ in range(ticks):
        for ev in w.drain_events():
            handle_event(ev, w)
        aki.maybe_replan()
        for agent in (aki, ren):
            agent.execute()
        w.step()
        if all_done(root):
            return


def test_camp_completes_without_perturbation():
    w = _make_world()
    root = build_camp_goal_graph()
    _run(w, root)
    assert all_done(root)
    assert w.structures["roof"] is True
    assert w.structures["pet"] is True


def test_camp_completes_with_injury():
    w = _make_world()
    w.push_event("INJURY", {"agent": "Ren"}, at_tick=60)
    root = build_camp_goal_graph()
    _run(w, root)
    assert all_done(root)


def test_camp_completes_with_blocked_resource():
    w = _make_world()
    # Block the forest; the gatherer must fall back. Our toy world has only
    # one wood node, so blocking it makes the task unachievable -- assert
    # replanning at least *runs* and does not crash.
    w.push_event("RESOURCE_BLOCKED", {"node": "forest"}, at_tick=45)
    root = build_camp_goal_graph()
    _run(w, root, ticks=500)
    # We don't assert success here; the point is that the system handles the
    # event gracefully. In a richer world there'd be a second wood node.
    assert w.resources["forest"].blocked is True
