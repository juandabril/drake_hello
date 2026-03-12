from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from drake_lab.scenarios.pendulum_dashboard import simulate_pendulum_pd_with_logs


def main():
    st.set_page_config(page_title="Drake Pendulum Lab (Legacy)", layout="wide")
    st.title("Drake Pendulum Lab (Legacy Single-File)")
    st.caption("Single-file Streamlit app kept for architecture comparison.")

    with st.sidebar:
        st.header("Simulation Settings")
        duration = st.slider("Duration [s]", min_value=1.0, max_value=20.0, value=6.0, step=0.5)
        theta0 = st.slider("Initial theta [rad]", min_value=-3.14, max_value=3.14, value=1.0, step=0.01)
        theta_dot0 = st.slider("Initial theta_dot [rad/s]", min_value=-10.0, max_value=10.0, value=0.0, step=0.1)
        kp = st.slider("Kp", min_value=0.0, max_value=30.0, value=8.0, step=0.5)
        kd = st.slider("Kd", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
        run = st.button("Run Simulation", type="primary")

    if not run:
        st.info("Adjust parameters and click 'Run Simulation'.")
        return

    time, state, torque = simulate_pendulum_pd_with_logs(
        duration=duration,
        initial_state=(theta0, theta_dot0),
        kp=kp,
        kd=kd,
    )
    theta = state[0, :]
    theta_dot = state[1, :]

    col1, col2, col3 = st.columns(3)
    col1.metric("Final theta", f"{theta[-1]:.3f} rad")
    col2.metric("Final theta_dot", f"{theta_dot[-1]:.3f} rad/s")
    col3.metric("Peak |tau|", f"{abs(torque).max():.3f} N m")

    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Closed-Loop Pendulum Response")

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

    st.pyplot(fig, use_container_width=True)


if __name__ == "__main__":
    main()
