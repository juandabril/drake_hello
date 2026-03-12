from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np


@dataclass(frozen=True)
class ReXPlaygroundConfig:
    seed: int = 7
    time_step: float = 0.02
    max_time: float = 24.0
    contact_stiffness: float = 850.0
    target_unscrew_turns: float = 6.5
    nominal_required_torque: float = 1.8
    torque_limit: float = 3.2


@dataclass(frozen=True)
class ReXEpisodeMetrics:
    policy: str
    success: bool
    cycle_time_s: float
    corrective_actions: int
    contact_force_peak_n: float
    torque_peak_nm: float
    energy_proxy: float
    chosen_route: str
    health_index: float
    uncertainty_index: float


def run_rex_episode(config: ReXPlaygroundConfig, policy: Literal["adaptive", "baseline"] = "adaptive"):
    """Simulate one de/remanufacturing episode with a selected control policy."""
    rng = np.random.default_rng(config.seed)

    # Uncertainty sampled per product instance.
    geometry_offset = rng.normal(0.0, 0.008)  # m
    friction_scale = np.clip(rng.normal(1.0, 0.25), 0.5, 1.6)
    health_index = float(np.clip(rng.normal(0.58, 0.2), 0.0, 1.0))
    uncertainty_index = float(np.clip(abs(geometry_offset) * 80.0 + abs(friction_scale - 1.0), 0.0, 1.0))

    required_torque = config.nominal_required_torque * friction_scale * (1.25 - 0.55 * health_index)
    required_torque = float(np.clip(required_torque, 0.7, config.torque_limit + 0.7))
    chosen_route = "reuse" if health_index >= 0.55 else "recycle"

    time_trace = []
    x_trace = []
    z_trace = []
    part_x_trace = []
    part_z_trace = []
    force_trace = []
    torque_trace = []
    phase_trace = []

    phase = "inspect"
    t = 0.0
    corrective_actions = 0
    unscrew_turns = 0.0
    energy_proxy = 0.0
    part_attached = False
    torque_bias = 0.0

    # Cell coordinates.
    part_x = 0.0
    part_z = 0.04
    ee_x = -0.45
    ee_z = 0.25
    target_contact_x = geometry_offset

    while t <= config.max_time:
        measured_force = 0.0
        torque_cmd = 0.0

        if phase == "inspect":
            if t >= 0.9:
                phase = "approach"

        elif phase == "approach":
            # Contact-free motion toward expected screw axis.
            ee_x += 0.45 * config.time_step
            ee_z += -0.12 * config.time_step
            if ee_x >= target_contact_x - 0.01 and ee_z <= 0.065:
                phase = "probe"

        elif phase == "probe":
            # Contact-rich alignment with force-based correction.
            penetration = max(0.0, 0.06 - ee_z)
            measured_force = config.contact_stiffness * penetration + rng.normal(0.0, 0.8)
            lateral_error = target_contact_x - ee_x
            ee_x += np.clip(lateral_error, -0.004, 0.004)

            if measured_force > 18.0:
                ee_z += 0.0015
                corrective_actions += 1
            else:
                ee_z -= 0.001

            if abs(lateral_error) < 0.0018 and 7.0 <= measured_force <= 18.0:
                phase = "unscrew"

        elif phase == "unscrew":
            if policy == "adaptive":
                # Low-level adaptive behavior under uncertain friction/health.
                torque_cmd = np.clip(
                    1.0 + 1.15 * abs(target_contact_x - ee_x) + 0.45 * (1.0 - health_index) + torque_bias,
                    0.5,
                    config.torque_limit,
                )
                if torque_cmd + 0.18 < required_torque:
                    corrective_actions += 1
                    ee_z += 0.0008
                    torque_bias = min(1.6, torque_bias + 0.02)
                    torque_cmd = min(config.torque_limit, torque_cmd + 0.26)
                else:
                    torque_bias = max(0.0, torque_bias - 0.004)
            else:
                # Baseline behavior: fixed recipe, no online correction.
                torque_cmd = 1.45 + 0.25 * (1.0 - health_index)
                torque_cmd = float(np.clip(torque_cmd, 0.5, config.torque_limit))

            # Turning speed drops with torque deficit.
            turn_rate = max(0.0, 1.4 - max(0.0, required_torque - torque_cmd) * 1.6)
            unscrew_turns += turn_rate * config.time_step
            energy_proxy += torque_cmd * torque_cmd * config.time_step

            if unscrew_turns >= config.target_unscrew_turns:
                part_attached = True
                phase = "extract"

        elif phase == "extract":
            # Extract and route to reuse/recycle bin.
            ee_z += 0.09 * config.time_step
            route_x = 0.28 if chosen_route == "reuse" else -0.28
            ee_x += np.clip(route_x - ee_x, -0.014, 0.014)
            if part_attached:
                part_x = ee_x
                part_z = max(0.04, ee_z - 0.03)
            if abs(ee_x - route_x) < 0.015 and ee_z > 0.19:
                phase = "sort"
                part_attached = False

        elif phase == "sort":
            part_x = 0.30 if chosen_route == "reuse" else -0.30
            part_z = 0.06
            break

        time_trace.append(t)
        x_trace.append(ee_x)
        z_trace.append(ee_z)
        part_x_trace.append(part_x)
        part_z_trace.append(part_z)
        force_trace.append(measured_force)
        torque_trace.append(torque_cmd)
        phase_trace.append(phase)

        t += config.time_step

    success = phase == "sort"
    metrics = ReXEpisodeMetrics(
        policy=policy,
        success=success,
        cycle_time_s=t,
        corrective_actions=corrective_actions,
        contact_force_peak_n=float(np.max(force_trace) if force_trace else 0.0),
        torque_peak_nm=float(np.max(torque_trace) if torque_trace else 0.0),
        energy_proxy=float(energy_proxy),
        chosen_route=chosen_route,
        health_index=health_index,
        uncertainty_index=uncertainty_index,
    )
    traces = {
        "t": np.array(time_trace),
        "ee_x": np.array(x_trace),
        "ee_z": np.array(z_trace),
        "part_x": np.array(part_x_trace),
        "part_z": np.array(part_z_trace),
        "force_n": np.array(force_trace),
        "torque_nm": np.array(torque_trace),
        "phase": np.array(phase_trace, dtype=object),
    }
    return metrics, traces
