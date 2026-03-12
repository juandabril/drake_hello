from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
from pydrake.all import Adder, ConstantVectorSource, DiagramBuilder, Gain, LogVectorOutput, MatrixGain, Simulator
from pydrake.examples import PendulumPlant

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    # Monolithic version kept for historical comparison.
    builder = DiagramBuilder()
    plant = builder.AddSystem(PendulumPlant())
    reference = builder.AddSystem(ConstantVectorSource([0.0, 0.0]))

    error = builder.AddSystem(Adder(2, 2))
    builder.Connect(reference.get_output_port(), error.get_input_port(0))

    neg_state = builder.AddSystem(Gain(-1.0, 2))
    builder.Connect(plant.get_output_port(), neg_state.get_input_port())
    builder.Connect(neg_state.get_output_port(), error.get_input_port(1))

    controller = builder.AddSystem(MatrixGain(np.array([[8.0, 2.0]])))
    builder.Connect(error.get_output_port(), controller.get_input_port())
    builder.Connect(controller.get_output_port(), plant.get_input_port())

    state_logger = LogVectorOutput(plant.get_output_port(), builder)
    torque_logger = LogVectorOutput(controller.get_output_port(), builder)

    diagram = builder.Build()
    context = diagram.CreateDefaultContext()
    plant_context = plant.GetMyMutableContextFromRoot(context)
    plant_context.SetContinuousState(np.array([1.0, 0.0]))

    simulator = Simulator(diagram, context)
    simulator.AdvanceTo(6.0)

    state_log = state_logger.FindLog(simulator.get_context())
    torque_log = torque_logger.FindLog(simulator.get_context())

    time = state_log.sample_times()
    theta = state_log.data()[0, :]
    theta_dot = state_log.data()[1, :]
    torque = torque_log.data()[0, :]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Closed-Loop Pendulum Dashboard (Single-File Legacy)")

    axes[0].plot(time, theta, color="tab:blue")
    axes[0].set_ylabel("theta [rad]")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(time, theta_dot, color="tab:orange")
    axes[1].set_ylabel("theta_dot [rad/s]")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(time, torque, color="tab:green")
    axes[2].set_ylabel("tau [N m]")
    axes[2].set_xlabel("time [s]")
    axes[2].grid(True, alpha=0.3)

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "legacy_5.topic_pendulum_dashboard_single_file.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=140)

    print("Legacy single-file dashboard generated.")
    print(f"Image path: {output_path}")


if __name__ == "__main__":
    main()

