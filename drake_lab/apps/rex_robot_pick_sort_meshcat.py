from __future__ import annotations

import time
from pathlib import Path

import matplotlib
from pydrake.geometry import Box, Meshcat, Rgba, Sphere, StartMeshcat
from pydrake.math import RigidTransform

from drake_lab.scenarios.rex_robot_pick_sort import RobotPickSortConfig, run_robot_pick_sort_episode

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _build_scene(meshcat: Meshcat):
    meshcat.Delete()
    meshcat.SetObject("/cell/table", Box(1.1, 0.65, 0.04), Rgba(0.33, 0.33, 0.37, 1.0))
    meshcat.SetTransform("/cell/table", RigidTransform([0.0, 0.0, 0.0]))

    meshcat.SetObject("/cell/reuse_bin", Box(0.18, 0.18, 0.14), Rgba(0.08, 0.55, 0.16, 0.9))
    meshcat.SetTransform("/cell/reuse_bin", RigidTransform([0.32, 0.0, 0.085]))

    meshcat.SetObject("/cell/recycle_bin", Box(0.18, 0.18, 0.14), Rgba(0.58, 0.14, 0.14, 0.9))
    meshcat.SetTransform("/cell/recycle_bin", RigidTransform([-0.32, 0.0, 0.085]))

    meshcat.SetObject("/cell/human_zone", Box(0.24, 0.24, 0.01), Rgba(0.72, 0.10, 0.88, 0.28))
    meshcat.SetTransform("/cell/human_zone", RigidTransform([0.0, -0.23, 0.03]))

    meshcat.SetObject("/cell/robot_ee", Sphere(0.025), Rgba(0.96, 0.78, 0.09, 1.0))
    meshcat.SetTransform("/cell/robot_ee", RigidTransform([-0.42, 0.0, 0.24]))

    meshcat.SetObject("/cell/object", Box(0.05, 0.04, 0.03), Rgba(0.15, 0.35, 0.85, 0.95))
    meshcat.SetTransform("/cell/object", RigidTransform([0.0, 0.0, 0.055]))


def _animate(meshcat: Meshcat, traces, realtime_factor: float):
    if traces["t"].size < 2:
        return
    for i in range(traces["t"].size):
        meshcat.SetTransform("/cell/robot_ee", RigidTransform([float(traces["ee_x"][i]), 0.0, float(traces["ee_z"][i])]))
        meshcat.SetTransform("/cell/object", RigidTransform([float(traces["obj_x"][i]), 0.0, float(traces["obj_z"][i])]))

        if bool(traces["human_alert"][i]):
            meshcat.SetProperty("/cell/human_zone", "color", [0.95, 0.12, 0.12, 0.45])
        else:
            meshcat.SetProperty("/cell/human_zone", "color", [0.72, 0.10, 0.88, 0.28])

        if i == 0:
            continue
        dt = float(traces["t"][i] - traces["t"][i - 1]) / max(realtime_factor, 1e-6)
        time.sleep(max(0.0, dt))


def _save_episode_plot(traces, output_path: Path):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.5), sharex=True)
    fig.suptitle("Robot Pick-Sort Episode")

    axes[0].plot(traces["t"], traces["ee_x"], label="ee_x")
    axes[0].plot(traces["t"], traces["ee_z"], label="ee_z")
    axes[0].set_ylabel("EE pose [m]")
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc="upper right")

    axes[1].plot(traces["t"], traces["obj_x"], label="obj_x", color="tab:green")
    axes[1].plot(traces["t"], traces["obj_z"], label="obj_z", color="tab:orange")
    axes[1].set_ylabel("Object pose [m]")
    axes[1].set_xlabel("time [s]")
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc="upper right")

    fig.tight_layout()
    fig.savefig(output_path, dpi=140)


def run_robot_pick_sort_meshcat_demo(
    seed: int = 42,
    adaptive: bool = True,
    uncertainty_scale: float = 1.0,
    realtime_factor: float = 1.0,
    hold_seconds: float = 20.0,
    wait_for_enter: bool = False,
):
    config = RobotPickSortConfig(seed=seed, adaptive=adaptive, uncertainty_scale=uncertainty_scale)
    metrics, traces = run_robot_pick_sort_episode(config)

    meshcat = StartMeshcat()
    _build_scene(meshcat)
    _animate(meshcat, traces, realtime_factor)

    outputs = Path("outputs")
    outputs.mkdir(exist_ok=True)
    fig_path = outputs / "9.topic_robot_pick_sort_episode.png"
    _save_episode_plot(traces, fig_path)

    print("Step 9 - Robot pick-sort Meshcat demo complete.")
    print(f"Meshcat URL: {meshcat.web_url()}")
    print(f"Episode figure: {fig_path}")
    print(
        "KPIs | "
        f"success={metrics.success}, cycle_time={metrics.cycle_time_s:.2f}s, "
        f"picked={metrics.picked_count}, reuse={metrics.placed_reuse}, recycle={metrics.placed_recycle}, "
        f"failed_grasps={metrics.failed_grasps}, replans={metrics.replans}, safety_stops={metrics.safety_stops}, "
        f"path={metrics.path_length_m:.2f}m, avg_grasp_conf={metrics.avg_grasp_confidence:.2f}"
    )

    if wait_for_enter:
        input("Meshcat is running. Press Enter to close...")
    elif hold_seconds > 0:
        print(f"Keeping Meshcat alive for {hold_seconds:.1f}s...")
        time.sleep(hold_seconds)

