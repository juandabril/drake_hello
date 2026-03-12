from __future__ import annotations

from dataclasses import dataclass

from pydrake.all import Simulator


@dataclass(frozen=True)
class SimulationConfig:
    duration: float


def run_to(diagram, context, config: SimulationConfig) -> Simulator:
    """Run a Drake diagram until the configured final time."""
    simulator = Simulator(diagram, context)
    simulator.AdvanceTo(config.duration)
    return simulator

