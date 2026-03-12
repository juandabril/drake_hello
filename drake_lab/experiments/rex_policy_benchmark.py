from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

import matplotlib
import numpy as np

from drake_lab.scenarios.rex_disassembly_playground import ReXPlaygroundConfig, run_rex_episode

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _write_csv(rows: list[dict], output_path: Path):
    if not rows:
        return
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def _summary_by_policy(rows: list[dict]):
    policies = sorted({r["policy"] for r in rows})
    summary = {}
    for p in policies:
        p_rows = [r for r in rows if r["policy"] == p]
        success = np.array([1.0 if r["success"] else 0.0 for r in p_rows])
        cycle = np.array([r["cycle_time_s"] for r in p_rows], dtype=float)
        corr = np.array([r["corrective_actions"] for r in p_rows], dtype=float)
        energy = np.array([r["energy_proxy"] for r in p_rows], dtype=float)
        summary[p] = {
            "n": len(p_rows),
            "success_rate": float(success.mean()),
            "cycle_time_mean": float(cycle.mean()),
            "cycle_time_std": float(cycle.std()),
            "corrective_mean": float(corr.mean()),
            "energy_mean": float(energy.mean()),
        }
    return summary


def _write_summary(summary: dict, output_path: Path):
    lines = []
    lines.append("ReX Policy Benchmark Summary")
    lines.append("")
    for policy in sorted(summary.keys()):
        s = summary[policy]
        lines.append(f"policy: {policy}")
        lines.append(f"  samples: {s['n']}")
        lines.append(f"  success_rate: {100.0 * s['success_rate']:.1f}%")
        lines.append(f"  cycle_time_mean: {s['cycle_time_mean']:.2f}s (+/- {s['cycle_time_std']:.2f})")
        lines.append(f"  corrective_actions_mean: {s['corrective_mean']:.1f}")
        lines.append(f"  energy_proxy_mean: {s['energy_mean']:.2f}")
        lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _plot_comparison(rows: list[dict], output_path: Path):
    adaptive_cycle = np.array([r["cycle_time_s"] for r in rows if r["policy"] == "adaptive"])
    baseline_cycle = np.array([r["cycle_time_s"] for r in rows if r["policy"] == "baseline"])
    adaptive_corr = np.array([r["corrective_actions"] for r in rows if r["policy"] == "adaptive"])
    baseline_corr = np.array([r["corrective_actions"] for r in rows if r["policy"] == "baseline"])

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    axes[0].boxplot([baseline_cycle, adaptive_cycle], labels=["baseline", "adaptive"])
    axes[0].set_title("Cycle time distribution")
    axes[0].set_ylabel("time [s]")
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].boxplot([baseline_corr, adaptive_corr], labels=["baseline", "adaptive"])
    axes[1].set_title("Corrective actions distribution")
    axes[1].set_ylabel("count")
    axes[1].grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)


def run_rex_policy_benchmark(samples: int = 48, start_seed: int = 200):
    rows = []
    for i in range(samples):
        seed = start_seed + i
        for policy in ("baseline", "adaptive"):
            metrics, _ = run_rex_episode(ReXPlaygroundConfig(seed=seed), policy=policy)
            row = asdict(metrics)
            row["seed"] = seed
            rows.append(row)

    outputs = Path("outputs")
    outputs.mkdir(exist_ok=True)
    csv_path = outputs / "8.topic_rex_policy_benchmark.csv"
    summary_path = outputs / "8.topic_rex_policy_benchmark_summary.txt"
    plot_path = outputs / "8.topic_rex_policy_benchmark.png"

    _write_csv(rows, csv_path)
    summary = _summary_by_policy(rows)
    _write_summary(summary, summary_path)
    _plot_comparison(rows, plot_path)

    baseline = summary["baseline"]
    adaptive = summary["adaptive"]
    print("Step 8 - Policy benchmark complete.")
    print(f"CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    print(f"Plot: {plot_path}")
    print(
        "Headline | "
        f"success baseline={100.0 * baseline['success_rate']:.1f}% vs adaptive={100.0 * adaptive['success_rate']:.1f}% ; "
        f"cycle_time baseline={baseline['cycle_time_mean']:.2f}s vs adaptive={adaptive['cycle_time_mean']:.2f}s"
    )

