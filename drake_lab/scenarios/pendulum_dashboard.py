from __future__ import annotations

import numpy as np
from pydrake.all import Adder, ConstantVectorSource, DiagramBuilder, Gain, LogVectorOutput, MatrixGain
from pydrake.examples import PendulumPlant

from drake_lab.core.simulation import SimulationConfig, run_to


def simulate_pendulum_pd_with_logs(
    duration: float = 6.0,
    initial_state=(1.0, 0.0),
    kp: float = 8.0,
    kd: float = 2.0,
):
    """Return full time-series logs for a closed-loop pendulum with a PD controller."""
    builder = DiagramBuilder()

    plant = builder.AddSystem(PendulumPlant())
    reference = builder.AddSystem(ConstantVectorSource([0.0, 0.0]))

    error = builder.AddSystem(Adder(2, 2))
    builder.Connect(reference.get_output_port(), error.get_input_port(0))

    neg_state = builder.AddSystem(Gain(-1.0, 2))
    builder.Connect(plant.get_output_port(), neg_state.get_input_port())
    builder.Connect(neg_state.get_output_port(), error.get_input_port(1))

    controller = builder.AddSystem(MatrixGain(np.array([[kp, kd]])))
    builder.Connect(error.get_output_port(), controller.get_input_port())
    builder.Connect(controller.get_output_port(), plant.get_input_port())

    state_logger = LogVectorOutput(plant.get_output_port(), builder)
    torque_logger = LogVectorOutput(controller.get_output_port(), builder)

    diagram = builder.Build()
    context = diagram.CreateDefaultContext()
    plant_context = plant.GetMyMutableContextFromRoot(context)
    plant_context.SetContinuousState(np.array(initial_state))

    simulator = run_to(diagram, context, SimulationConfig(duration=duration))

    state_log = state_logger.FindLog(simulator.get_context())
    torque_log = torque_logger.FindLog(simulator.get_context())

    time = state_log.sample_times()
    state = state_log.data()  # [theta, theta_dot]
    torque = torque_log.data()[0, :]
    return time, state, torque

