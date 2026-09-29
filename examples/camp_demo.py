"""Command-line reproduction of the Monta NPC camp demo.

Run:
    python -m examples.camp_demo
    python -m examples.camp_demo --events injury,block

Observe two agents (Aki, Ren) negotiate, gather, build, and recover from
injected disturbances. This is the same state machine as the Unity build,
just rendered to stdout.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Allow running directly from a checkout without installing.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from native_life.agent import BDIAgent, PlanBoard, all_done   # noqa: E402
from native_life.replanner import handle_event             # noqa: E402
from native_life.task_graph import build_camp_goal_graph   # noqa: E402
from native_life.world import ResourceNode, World          # noqa: E402


def banner(msg: str) -> None:
    print("\n" + "=" * 60)
    print(msg)
    print("=" * 60)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", default="",
                    help="comma-separated subset of: injury,block")
    ap.add_argument("--speed", type=float, default=0.0,
                    help="seconds to sleep between ticks (0 = as fast as possible)")
    args = ap.parse_args()

    w = World()
    w.add_agent("Aki")
    w.add_agent("Ren")
    w.add_resource(ResourceNode("forest", "wood", amount=5))
    w.add_resource(ResourceNode("quarry", "stone", amount=5))
    w.add_resource(ResourceNode("pet_den", "pet", amount=1))

    root = build_camp_goal_graph()
    board = PlanBoard()

    def log(msg: str) -> None:
        print(f"[t={w.tick:>4}] {msg}")

    aki = BDIAgent("Aki", w, root, board, peers=["Ren"], logger=log)
    ren = BDIAgent("Ren", w, root, board, peers=["Aki"], logger=log)

    # Inject scheduled events (mirrors the UI buttons in the Unity demo).
    wanted = set(args.events.split(",")) if args.events else set()
    if "injury" in wanted:
        w.push_event("INJURY", {"agent": "Ren"}, at_tick=60)
    if "block" in wanted:
        w.push_event("RESOURCE_BLOCKED", {"node": "forest"}, at_tick=45)

    banner("Monta camp (CLI reproduction) — Aki & Ren agree to build a camp")
    log("Opening negotiation...")

    safety = 5000  # tick cap
    while not all_done(root) and w.tick < safety:
        # 1. Apply world events.
        for ev in w.drain_events():
            log(f"!! event {ev.type} {ev.payload}")
            handle_event(ev, w)

        # 2. Coordinator re-negotiates on the shared board.
        old_plan = dict(board.assignment)
        aki.maybe_replan()
        if board.assignment != old_plan:
            for task, agent in board.assignment.items():
                log(f"  plan: {task} -> {agent}")

        # 3. Each agent executes.
        for agent in (aki, ren):
            agent.execute()

        # 4. Advance world.
        w.step()
        if args.speed:
            time.sleep(args.speed)

    banner("Result")
    print(f"  wood left   : {w.inventory['wood']}")
    print(f"  stone left  : {w.inventory['stone']}")
    print(f"  foundation  : {w.structures['foundation']}")
    print(f"  walls       : {w.structures['walls']}")
    print(f"  roof        : {w.structures['roof']}")
    print(f"  pet captured: {w.structures['pet']}")
    print(f"  ticks used  : {w.tick}")
    if all_done(root):
        print("  CAMP ESTABLISHED ✅")
        return 0
    print("  did not finish within tick budget ❌")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
