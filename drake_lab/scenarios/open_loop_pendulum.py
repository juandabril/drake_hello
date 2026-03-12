from __future__ import annotations

import numpy as np
from pydrake.all import ConstantVectorSource, DiagramBuilder, LogVectorOutput
from pydrake.examples import PendulumPlant

from drake_lab.core.simulation import SimulationConfig, run_to


def simulate_open_loop_pendulum(
    duration: float = 3.0, initial_state=(0.5, 0.0), constant_torque: float = 0.0
):
    """Run an open-loop pendulum and return the final state."""
    builder = DiagramBuilder()
    plant = builder.AddSystem(PendulumPlant())
    torque = builder.AddSystem(ConstantVectorSource([constant_torque]))
    builder.Connect(torque.get_output_port(), plant.get_input_port())
    logger = LogVectorOutput(plant.get_output_port(), builder)

    diagram = builder.Build()
    context = diagram.CreateDefaultContext()
    plant_context = plant.GetMyMutableContextFromRoot(context)
    # State format: [theta, theta_dot].
    plant_context.SetContinuousState(np.array(initial_state))

    simulator = run_to(diagram, context, SimulationConfig(duration=duration))
    log = logger.FindLog(simulator.get_context())
    final_theta, final_theta_dot = log.data()[:, -1]
    return final_theta, final_theta_dot

