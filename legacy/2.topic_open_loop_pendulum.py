from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from drake_lab.scenarios.open_loop_pendulum import simulate_open_loop_pendulum


if __name__ == "__main__":
    theta, theta_dot = simulate_open_loop_pendulum()
    print("Step 2 - Open-loop pendulum simulation complete (3s, torque=0).")
    print(f"Final state: theta={theta:.3f}, theta_dot={theta_dot:.3f}")
