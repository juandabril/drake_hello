import argparse

from drake_lab.apps.rex_meshcat_playground import run_rex_meshcat_playground


def parse_args():
    parser = argparse.ArgumentParser(description="ReX disassembly Meshcat playground.")
    parser.add_argument("--seed", type=int, default=7, help="Random seed for uncertainty sampling.")
    parser.add_argument("--realtime-factor", type=float, default=1.0, help="1.0 = real-time replay.")
    parser.add_argument("--hold-seconds", type=float, default=20.0, help="Keep Meshcat server alive after replay.")
    parser.add_argument("--wait-for-enter", action="store_true", help="Keep Meshcat alive until Enter is pressed.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_rex_meshcat_playground(
        realtime_factor=args.realtime_factor,
        seed=args.seed,
        hold_seconds=args.hold_seconds,
        wait_for_enter=args.wait_for_enter,
    )
