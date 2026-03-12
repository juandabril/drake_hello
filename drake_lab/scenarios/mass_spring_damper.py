from __future__ import annotations

import numpy as np
from pydrake.all import ConstantVectorSource, DiagramBuilder, LinearSystem, LogVectorOutput

from drake_lab.core.simulation import SimulationConfig, run_to


def simulate_mass_spring_damper(duration: float = 5.0, constant_force: float = 1.0):
    """Run a mass-spring-damper model and return the final state."""
    # x = [position, velocity]
    # xdot = A x + B u
    a_matrix = np.array([[0.0, 1.0], [-4.0, -0.8]])  # k=4, b=0.8, m=1
    b_matrix = np.array([[0.0], [1.0]])  # External force input.
    c_matrix = np.eye(2)
    d_matrix = np.zeros((2, 1))

    builder = DiagramBuilder()
    plant = builder.AddSystem(LinearSystem(a_matrix, b_matrix, c_matrix, d_matrix))
    force = builder.AddSystem(ConstantVectorSource([constant_force]))
    builder.Connect(force.get_output_port(), plant.get_input_port())
    logger = LogVectorOutput(plant.get_output_port(), builder)

    diagram = builder.Build()
    context = diagram.CreateDefaultContext()
    plant_context = plant.GetMyMutableContextFromRoot(context)
    plant_context.SetContinuousState(np.array([0.0, 0.0]))

    simulator = run_to(diagram, context, SimulationConfig(duration=duration))
    log = logger.FindLog(simulator.get_context())
    final_position, final_velocity = log.data()[:, -1]
    return final_position, final_velocity

