from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from drake_lab.scenarios.pendulum_dashboard import simulate_pendulum_pd_with_logs


def main():
    time, state, torque = simulate_pendulum_pd_with_logs(duration=6.0, initial_state=(1.0, 0.0), kp=8.0, kd=2.0)
    theta = state[0, :]
    theta_dot = state[1, :]

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Closed-Loop Pendulum Dashboard (PD Control)")

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
    output_path = output_dir / "5.topic_pendulum_dashboard.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=140)

    print("Step 5 - Dashboard generated successfully.")
    print(f"Image path: {output_path}")
    print(f"Final state: theta={theta[-1]:.3f}, theta_dot={theta_dot[-1]:.3f}, |tau|max={abs(torque).max():.3f}")


if __name__ == "__main__":
    main()

