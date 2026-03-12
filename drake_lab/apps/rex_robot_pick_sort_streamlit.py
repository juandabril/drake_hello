from __future__ import annotations

from dataclasses import asdict

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from drake_lab.scenarios.rex_robot_pick_sort import RobotPickSortConfig, run_robot_pick_sort_episode


def _run_batch(samples: int, base_seed: int, uncertainty_scale: float, adaptive: bool, intrusion_rate: float):
    rows = []
    for i in range(samples):
        cfg = RobotPickSortConfig(
            seed=base_seed + i,
            uncertainty_scale=uncertainty_scale,
            adaptive=adaptive,
            human_intrusion_rate=intrusion_rate,
        )
        metrics, _ = run_robot_pick_sort_episode(cfg)
        row = asdict(metrics)
        row["seed"] = base_seed + i
        row["policy"] = "adaptive" if adaptive else "baseline"
        rows.append(row)
    return pd.DataFrame(rows)


def run_app():
    st.set_page_config(page_title="ReX Robot Pick-Sort Lab", layout="wide")
    st.title("ReX Robot Pick-Sort Digital Twin Lab")
    st.caption("Human-robot collaborative de/remanufacturing simulation with uncertainty, replanning, and KPI benchmarking.")

    with st.sidebar:
        st.header("Scenario")
        samples = st.slider("Episodes per policy", min_value=6, max_value=100, value=24, step=2)
        base_seed = st.number_input("Base seed", min_value=1, max_value=100000, value=500, step=1)
        uncertainty_scale = st.slider("Uncertainty scale", min_value=0.5, max_value=2.5, value=1.1, step=0.1)
        intrusion_rate = st.slider("Human intrusion probability / step", min_value=0.0, max_value=0.06, value=0.012, step=0.002)
        run_btn = st.button("Run Benchmark", type="primary")

    if not run_btn:
        st.info("Configure the scenario and click 'Run Benchmark'.")
        return

    with st.spinner("Running adaptive and baseline policies..."):
        df_ad = _run_batch(samples, int(base_seed), uncertainty_scale, adaptive=True, intrusion_rate=intrusion_rate)
        df_bl = _run_batch(samples, int(base_seed), uncertainty_scale, adaptive=False, intrusion_rate=intrusion_rate)
        df = pd.concat([df_bl, df_ad], ignore_index=True)

    grp = df.groupby("policy").agg(
        success_rate=("success", "mean"),
        cycle_time_s=("cycle_time_s", "mean"),
        failed_grasps=("failed_grasps", "mean"),
        replans=("replans", "mean"),
        safety_stops=("safety_stops", "mean"),
        path_length_m=("path_length_m", "mean"),
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Adaptive success rate", f"{100.0 * grp.loc['adaptive', 'success_rate']:.1f}%")
    c2.metric("Baseline success rate", f"{100.0 * grp.loc['baseline', 'success_rate']:.1f}%")
    c3.metric("Cycle time gain", f"{grp.loc['baseline', 'cycle_time_s'] - grp.loc['adaptive', 'cycle_time_s']:.2f} s")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    axes[0].boxplot(
        [
            df[df["policy"] == "baseline"]["cycle_time_s"],
            df[df["policy"] == "adaptive"]["cycle_time_s"],
        ],
        labels=["baseline", "adaptive"],
    )
    axes[0].set_title("Cycle time distribution")
    axes[0].set_ylabel("time [s]")
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].boxplot(
        [
            df[df["policy"] == "baseline"]["failed_grasps"],
            df[df["policy"] == "adaptive"]["failed_grasps"],
        ],
        labels=["baseline", "adaptive"],
    )
    axes[1].set_title("Failed grasps distribution")
    axes[1].set_ylabel("count")
    axes[1].grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)

    st.subheader("Policy Summary")
    summary = grp.copy()
    summary["success_rate"] = 100.0 * summary["success_rate"]
    summary = summary.rename(columns={"success_rate": "success_rate_%"})
    st.dataframe(summary, use_container_width=True)

    st.subheader("Episode-Level Metrics")
    st.dataframe(df, use_container_width=True)
