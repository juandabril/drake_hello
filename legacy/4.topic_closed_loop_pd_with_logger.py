from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from drake_lab.scenarios.closed_loop_pendulum_pd import simulate_closed_loop_pendulum_pd


if __name__ == "__main__":
    theta, theta_dot, torque_peak = simulate_closed_loop_pendulum_pd()
    print("Step 4 - Closed-loop pendulum with PD controller and logging complete (4s).")
    print(f"Final state: theta={theta:.3f}, theta_dot={theta_dot:.3f}")
    print(f"Peak absolute torque: {torque_peak:.3f}")
