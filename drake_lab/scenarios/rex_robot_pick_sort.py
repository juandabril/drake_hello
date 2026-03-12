from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RobotPickSortConfig:
    seed: int = 42
    time_step: float = 0.02
    max_time: float = 40.0
    pick_tolerance_m: float = 0.012
    place_tolerance_m: float = 0.015
    grasp_success_base: float = 0.86
    human_intrusion_rate: float = 0.012
    uncertainty_scale: float = 1.0
    adaptive: bool = True


@dataclass(frozen=True)
class RobotPickSortMetrics:
    success: bool
    cycle_time_s: float
    picked_count: int
    placed_reuse: int
    placed_recycle: int
    failed_grasps: int
    replans: int
    safety_stops: int
    path_length_m: float
    avg_grasp_confidence: float


def _route_from_health(health: float) -> str:
    return "reuse" if health >= 0.55 else "recycle"


def run_robot_pick_sort_episode(config: RobotPickSortConfig):
    """Simulate a robot pick-sort episode with uncertainty and human safety events."""
    rng = np.random.default_rng(config.seed)

    # Generate incoming components with health and pose uncertainty.
    n_parts = 8
    part_health = np.clip(rng.normal(0.57, 0.22, size=n_parts), 0.0, 1.0)
    part_uncert = np.clip(rng.normal(0.5, 0.25, size=n_parts) * config.uncertainty_scale, 0.0, 1.0)
    part_x_nom = np.linspace(-0.22, 0.22, n_parts)
    part_z_nom = np.full(n_parts, 0.055)
    part_x_real = part_x_nom + rng.normal(0.0, 0.02 * config.uncertainty_scale, size=n_parts)
    part_z_real = part_z_nom + rng.normal(0.0, 0.004 * config.uncertainty_scale, size=n_parts)
    part_active = np.ones(n_parts, dtype=bool)

    # Robot end-effector state.
    ee_x = -0.42
    ee_z = 0.24
    carrying = -1
    target_idx = 0

    # Metrics.
    t = 0.0
    path_length = 0.0
    picked_count = 0
    placed_reuse = 0
    placed_recycle = 0
    failed_grasps = 0
    replans = 0
    safety_stops = 0
    grasp_conf_values = []
    phase = "scan"

    # Traces.
    trace_t = []
    trace_ee_x = []
    trace_ee_z = []
    trace_obj_x = []
    trace_obj_z = []
    trace_phase = []
    trace_human_alert = []

    obj_x = 0.0
    obj_z = 0.055

    while t <= config.max_time:
        human_alert = rng.random() < config.human_intrusion_rate
        if human_alert:
            safety_stops += 1
            phase = "safety_pause"

        prev_x, prev_z = ee_x, ee_z

        active_indices = np.where(part_active)[0]
        if active_indices.size == 0 and carrying < 0:
            phase = "done"
            break

        if phase == "safety_pause":
            if rng.random() < 0.2:
                phase = "transport" if carrying >= 0 else "scan"

        elif phase == "scan":
            if carrying >= 0:
                phase = "transport"
            elif active_indices.size > 0:
                # Prioritize high health first (re-manufacturing value), then lower uncertainty.
                candidates = sorted(
                    active_indices.tolist(),
                    key=lambda i: (-part_health[i], part_uncert[i]),
                )
                target_idx = candidates[0]
                phase = "approach_pick"

        elif phase == "approach_pick":
            tx = part_x_nom[target_idx]
            tz = 0.08
            ee_x += np.clip(tx - ee_x, -0.010, 0.010)
            ee_z += np.clip(tz - ee_z, -0.010, 0.010)
            if abs(ee_x - tx) < 0.01 and abs(ee_z - tz) < 0.01:
                phase = "align_pick"

        elif phase == "align_pick":
            # Adaptive policy reduces alignment error based on online correction.
            desired_x = part_x_real[target_idx]
            desired_z = part_z_real[target_idx] + 0.01
            gain = 0.65 if config.adaptive else 0.35
            ee_x += gain * np.clip(desired_x - ee_x, -0.006, 0.006)
            ee_z += gain * np.clip(desired_z - ee_z, -0.004, 0.004)
            if abs(ee_x - desired_x) < config.pick_tolerance_m and abs(ee_z - desired_z) < 0.01:
                phase = "grasp"

        elif phase == "grasp":
            pose_err = np.hypot(ee_x - part_x_real[target_idx], ee_z - part_z_real[target_idx])
            confidence = float(np.clip(config.grasp_success_base - 2.5 * pose_err - 0.35 * part_uncert[target_idx], 0.05, 0.99))
            grasp_conf_values.append(confidence)
            if rng.random() < confidence:
                carrying = target_idx
                picked_count += 1
                phase = "transport"
            else:
                failed_grasps += 1
                replans += 1
                if config.adaptive:
                    # Improve estimate after failed grasp.
                    part_x_real[target_idx] += rng.normal(0.0, 0.003)
                    part_z_real[target_idx] += rng.normal(0.0, 0.002)
                phase = "approach_pick"

        elif phase == "transport":
            route = _route_from_health(part_health[carrying])
            tx = 0.30 if route == "reuse" else -0.30
            tz = 0.22
            ee_x += np.clip(tx - ee_x, -0.012, 0.012)
            ee_z += np.clip(tz - ee_z, -0.012, 0.012)
            if abs(ee_x - tx) < 0.015 and abs(ee_z - tz) < 0.015:
                phase = "place"

        elif phase == "place":
            route = _route_from_health(part_health[carrying])
            part_active[carrying] = False
            if route == "reuse":
                placed_reuse += 1
            else:
                placed_recycle += 1
            carrying = -1
            phase = "scan"

        if carrying >= 0:
            obj_x = ee_x
            obj_z = max(0.055, ee_z - 0.03)
        elif active_indices.size > 0:
            obj_x = part_x_real[active_indices[0]]
            obj_z = part_z_real[active_indices[0]]

        path_length += float(np.hypot(ee_x - prev_x, ee_z - prev_z))

        trace_t.append(t)
        trace_ee_x.append(ee_x)
        trace_ee_z.append(ee_z)
        trace_obj_x.append(obj_x)
        trace_obj_z.append(obj_z)
        trace_phase.append(phase)
        trace_human_alert.append(human_alert)

        t += config.time_step

    success = np.all(~part_active)
    metrics = RobotPickSortMetrics(
        success=bool(success),
        cycle_time_s=float(t),
        picked_count=int(picked_count),
        placed_reuse=int(placed_reuse),
        placed_recycle=int(placed_recycle),
        failed_grasps=int(failed_grasps),
        replans=int(replans),
        safety_stops=int(safety_stops),
        path_length_m=float(path_length),
        avg_grasp_confidence=float(np.mean(grasp_conf_values) if grasp_conf_values else 0.0),
    )
    traces = {
        "t": np.array(trace_t),
        "ee_x": np.array(trace_ee_x),
        "ee_z": np.array(trace_ee_z),
        "obj_x": np.array(trace_obj_x),
        "obj_z": np.array(trace_obj_z),
        "phase": np.array(trace_phase, dtype=object),
        "human_alert": np.array(trace_human_alert),
    }
    return metrics, traces
