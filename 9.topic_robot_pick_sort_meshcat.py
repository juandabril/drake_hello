import argparse

from drake_lab.apps.rex_robot_pick_sort_meshcat import run_robot_pick_sort_meshcat_demo


def parse_args():
    parser = argparse.ArgumentParser(description="Robot pick-sort Meshcat demo.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for scenario.")
    parser.add_argument("--uncertainty-scale", type=float, default=1.0, help="Uncertainty multiplier.")
    parser.add_argument("--baseline", action="store_true", help="Use baseline policy (no adaptive corrections).")
    parser.add_argument("--realtime-factor", type=float, default=1.0, help="Replay speed (1.0 = real-time).")
    parser.add_argument("--hold-seconds", type=float, default=20.0, help="Keep Meshcat alive after replay.")
    parser.add_argument("--wait-for-enter", action="store_true", help="Keep Meshcat alive until Enter is pressed.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_robot_pick_sort_meshcat_demo(
        seed=args.seed,
        adaptive=not args.baseline,
        uncertainty_scale=args.uncertainty_scale,
        realtime_factor=args.realtime_factor,
        hold_seconds=args.hold_seconds,
        wait_for_enter=args.wait_for_enter,
    )

