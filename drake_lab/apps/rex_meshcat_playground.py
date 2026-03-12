from __future__ import annotations

import time
from pathlib import Path

import matplotlib
import numpy as np
from pydrake.geometry import Box, Meshcat, Rgba, Sphere, StartMeshcat
from pydrake.math import RigidTransform

from drake_lab.scenarios.rex_disassembly_playground import ReXPlaygroundConfig, run_rex_episode

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _build_meshcat_scene(meshcat: Meshcat):
    """Create a simple ReX cell scene in Meshcat."""
    meshcat.Delete()

    meshcat.SetObject("/cell/table", Box(1.0, 0.6, 0.04), Rgba(0.35, 0.35, 0.38, 1.0))
    meshcat.SetTransform("/cell/table", RigidTransform([0.0, 0.0, 0.0]))

    meshcat.SetObject("/cell/reuse_bin", Box(0.16, 0.16, 0.12), Rgba(0.10, 0.55, 0.15, 0.85))
    meshcat.SetTransform("/cell/reuse_bin", RigidTransform([0.30, 0.0, 0.08]))

    meshcat.SetObject("/cell/recycle_bin", Box(0.16, 0.16, 0.12), Rgba(0.55, 0.15, 0.15, 0.85))
    meshcat.SetTransform("/cell/recycle_bin", RigidTransform([-0.30, 0.0, 0.08]))

    meshcat.SetObject("/cell/e_waste_module", Box(0.14, 0.10, 0.05), Rgba(0.20, 0.30, 0.82, 0.95))
    meshcat.SetTransform("/cell/e_waste_module", RigidTransform([0.0, 0.0, 0.06]))

    meshcat.SetObject("/cell/robot_ee", Sphere(0.025), Rgba(0.95, 0.78, 0.10, 1.0))
    meshcat.SetTransform("/cell/robot_ee", RigidTransform([-0.45, 0.0, 0.25]))

    meshcat.SetObject("/cell/human_zone", Box(0.20, 0.20, 0.01), Rgba(0.62, 0.12, 0.78, 0.30))
    meshcat.SetTransform("/cell/human_zone", RigidTransform([0.0, -0.22, 0.03]))


def _animate_episode(meshcat: Meshcat, traces, realtime_factor: float):
    """Replay one episode in Meshcat."""
    if traces["t"].size < 2:
        return
    for i in range(traces["t"].size):
        ee_x = float(traces["ee_x"][i])
        ee_z = float(traces["ee_z"][i])
        part_x = float(traces["part_x"][i])
        part_z = float(traces["part_z"][i])

        meshcat.SetTransform("/cell/robot_ee", RigidTransform([ee_x, 0.0, ee_z]))
        meshcat.SetTransform("/cell/e_waste_module", RigidTransform([part_x, 0.0, part_z]))

        if i == 0:
            continue
        dt = float(traces["t"][i] - traces["t"][i - 1]) / max(realtime_factor, 1e-6)
        time.sleep(max(0.0, dt))


def _plot_dashboard(traces, output_path: Path):
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    fig.suptitle("ReX Contact-Adaptive Disassembly Episode")

    axes[0].plot(traces["t"], traces["ee_x"], label="ee_x")
    axes[0].plot(traces["t"], traces["ee_z"], label="ee_z")
    axes[0].set_ylabel("EE position [m]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="upper right")

    axes[1].plot(traces["t"], traces["force_n"], color="tab:orange")
    axes[1].set_ylabel("Contact force [N]")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(traces["t"], traces["torque_nm"], color="tab:green")
    axes[2].set_ylabel("Unscrew torque [N m]")
    axes[2].set_xlabel("time [s]")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)


def _plot_monte_carlo(output_path: Path, samples: int = 24):
    cycle = []
    corrections = []
    uncertainty = []
    success = []
    for i in range(samples):
        m, _ = run_rex_episode(ReXPlaygroundConfig(seed=100 + i))
        cycle.append(m.cycle_time_s)
        corrections.append(m.corrective_actions)
        uncertainty.append(m.uncertainty_index)
        success.append(1.0 if m.success else 0.0)

    cycle = np.array(cycle)
    corrections = np.array(corrections)
    uncertainty = np.array(uncertainty)
    success = np.array(success)

    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(corrections, cycle, c=uncertainty, cmap="viridis", s=70, alpha=0.9)
    ax.set_title("Monte Carlo Robustness Map (ReX cell)")
    ax.set_xlabel("Corrective actions [count]")
    ax.set_ylabel("Cycle time [s]")
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label("Uncertainty index")
    ax.grid(True, alpha=0.3)

    success_rate = float(success.mean() * 100.0)
    ax.text(
        0.02,
        0.98,
        f"success rate: {success_rate:.1f}%",
        transform=ax.transAxes,
        va="top",
        ha="left",
        bbox={"facecolor": "white", "alpha": 0.7, "edgecolor": "none"},
    )

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)


def run_rex_meshcat_playground(
    realtime_factor: float = 1.0,
    seed: int = 7,
    hold_seconds: float = 20.0,
    wait_for_enter: bool = False,
):
    """Run one advanced ReX episode, replay it in Meshcat, and save KPI dashboards."""
    config = ReXPlaygroundConfig(seed=seed)
    metrics, traces = run_rex_episode(config)

    meshcat = StartMeshcat()
    _build_meshcat_scene(meshcat)
    _animate_episode(meshcat, traces, realtime_factor=realtime_factor)

    outputs = Path("outputs")
    outputs.mkdir(exist_ok=True)
    episode_plot_path = outputs / "7.topic_rex_episode_dashboard.png"
    monte_carlo_path = outputs / "7.topic_rex_monte_carlo.png"
    _plot_dashboard(traces, episode_plot_path)
    _plot_monte_carlo(monte_carlo_path)

    print("Step 7 - ReX Meshcat real-time playground complete.")
    print(f"Meshcat URL: {meshcat.web_url()}")
    print(f"Episode dashboard: {episode_plot_path}")
    print(f"Monte Carlo robustness map: {monte_carlo_path}")
    print(
        "KPIs | "
        f"success={metrics.success}, cycle_time={metrics.cycle_time_s:.2f}s, "
        f"corrective_actions={metrics.corrective_actions}, "
        f"force_peak={metrics.contact_force_peak_n:.2f}N, torque_peak={metrics.torque_peak_nm:.2f}Nm, "
        f"route={metrics.chosen_route}, health_index={metrics.health_index:.2f}, "
        f"uncertainty_index={metrics.uncertainty_index:.2f}"
    )

    if wait_for_enter:
        input("Meshcat is running. Press Enter to close...")
    elif hold_seconds > 0:
        print(f"Keeping Meshcat alive for {hold_seconds:.1f}s...")
        time.sleep(hold_seconds)
