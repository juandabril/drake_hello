# Drake Hello: ReX Robotics Playground (Streamlit + Meshcat)

## ES | Español
Proyecto para simulación robótica de **de- & remanufacturing (ReX)** con:

- **Streamlit** para dashboard interactivo y benchmarking.
- **Meshcat (Drake)** para visualización 3D en tiempo real.
- Escenarios con incertidumbre, seguridad humano-robot y políticas `adaptive` vs `baseline`.

Objetivo: repo listo para ejecutar localmente y desplegar en **Streamlit Community Cloud**.

## EN | English
This project is a robotics simulation playground for **de- & remanufacturing (ReX)** featuring:

- **Streamlit** for interactive dashboards and benchmarking.
- **Meshcat (Drake)** for real-time 3D visualization.
- Uncertainty-aware scenarios, human-robot safety events, and `adaptive` vs `baseline` policies.

Goal: a repository ready for local execution and **Streamlit Community Cloud** deployment.

---

## ES | ¿Qué es Drake?
**Drake** es una librería de simulación/control para robótica.  
Aquí se usa para diseñar y validar lógica de control antes de pasar a hardware real.

## EN | What is Drake?
**Drake** is a robotics simulation/control library.  
In this repo, it is used to design and validate control logic before hardware deployment.

---

## ES/EN | Repository Structure

```text
drake_hello/
  drake_lab/
    apps/         # UI and runners (Streamlit / Meshcat)
    scenarios/    # Simulation engines and control logic
    experiments/  # Benchmark pipelines
    core/         # Shared utilities
  legacy/         # Previous single-file versions (traceability)
  streamlit_app.py
  requirements.txt
  runtime.txt
  DEPLOY_CHECKLIST.md
```

`streamlit_app.py` is the recommended cloud entrypoint.

---

## ES | Instalación local (WSL/Linux)
## EN | Local setup (WSL/Linux)

```bash
cd "/mnt/c/Users/juand/GitHub Projects/drake_hello"
python3 -m venv .venv_wsl
source .venv_wsl/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ES | Ejecutar demos principales
## EN | Run main demos

### Streamlit lab
```bash
streamlit run streamlit_app.py
```

### Meshcat real-time pick-sort demo
```bash
python 9.topic_robot_pick_sort_meshcat.py --wait-for-enter
```

### Policy benchmark (CSV + summary + plot)
```bash
python 8.topic_rex_policy_benchmark.py --samples 48 --start-seed 200
```

---

## ES | Comandos de control rápidos
## EN | Quick control commands

Baseline policy:
```bash
python 9.topic_robot_pick_sort_meshcat.py --baseline --uncertainty-scale 1.4 --wait-for-enter
```

Adaptive policy under harder uncertainty:
```bash
python 9.topic_robot_pick_sort_meshcat.py --uncertainty-scale 1.8 --wait-for-enter
```

---

## ES | Deploy en Streamlit Community Cloud
## EN | Deploy on Streamlit Community Cloud

1. Push repo to GitHub (`main` branch).
2. In Streamlit Cloud, create a new app.
3. Select:
   - Repository: `juandabril/drake_hello`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. Deploy.

### Required files
- `requirements.txt`
- `runtime.txt` (`python-3.10.16` for Drake compatibility)

---

## ES | Troubleshooting
## EN | Troubleshooting

- `ModuleNotFoundError: drake_lab`  
  Run commands from repo root.

- Meshcat `localhost` not reachable  
  Keep script alive (`--wait-for-enter`) and use `http://127.0.0.1:7000`.

- Streamlit Cloud build issues  
  Check Python runtime, dependencies, and main file path.

---

## ES | Valor técnico para investigación/aplicación
## EN | Technical value for research/application

- System design for collaborative robotic cells.
- High-level sequencing + low-level adaptation.
- Uncertainty robustness and reproducible KPI reporting.
- Evidence-ready outputs (CSV, summaries, plots, demos).

