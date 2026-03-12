import argparse

from drake_lab.experiments.rex_policy_benchmark import run_rex_policy_benchmark


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark baseline vs adaptive ReX policies.")
    parser.add_argument("--samples", type=int, default=48, help="Number of seeds (episodes per policy).")
    parser.add_argument("--start-seed", type=int, default=200, help="Start seed for reproducibility.")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_rex_policy_benchmark(samples=args.samples, start_seed=args.start_seed)

