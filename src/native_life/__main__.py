"""Allow `python -m native_life` to run the camp demo."""
from .agent import PlanBoard, all_done
from .replanner import handle_event
from .task_graph import build_camp_goal_graph
from .world import ResourceNode, World
from .agent import BDIAgent


def main() -> int:
    w = World()
    w.add_agent("Aki")
    w.add_agent("Ren")
    w.add_resource(ResourceNode("forest", "wood", amount=5))
    w.add_resource(ResourceNode("quarry", "stone", amount=5))
    w.add_resource(ResourceNode("den", "pet", amount=1))
    root = build_camp_goal_graph()
    board = PlanBoard()
    aki = BDIAgent("Aki", w, root, board, logger=print)
    ren = BDIAgent("Ren", w, root, board, logger=print)
    # Default: inject both perturbations, mirroring the Unity demo.
    w.push_event("INJURY", {"agent": "Ren"}, at_tick=60)
    w.push_event("RESOURCE_BLOCKED", {"node": "forest"}, at_tick=45)

    while not all_done(root) and w.tick < 5000:
        for ev in w.drain_events():
            print(f"[event] {ev.type} {ev.payload}")
            handle_event(ev, w)
        aki.maybe_replan()
        for a in (aki, ren):
            a.execute()
        w.step()

    print("CAMP ESTABLISHED" if all_done(root) else "did not finish")
    return 0 if all_done(root) else 1


if __name__ == "__main__":
    raise SystemExit(main())
