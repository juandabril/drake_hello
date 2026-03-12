# Drake Hello: Robotics ReX Playground (Streamlit + Meshcat)

Proyecto orientado a **simulación robótica para de- & remanufacturing (ReX)** con:

- **Streamlit** para dashboards interactivos y benchmarking.
- **Meshcat (Drake)** para animación 3D en tiempo real.
- **Escenarios con incertidumbre, seguridad humano-robot, y control adaptive vs baseline**.

El objetivo es tener un repo listo para:

1. correr localmente en WSL/Linux, y  
2. desplegar gratis en **Streamlit Community Cloud** con link público (`*.streamlit.app`).

---

## ¿Qué es Drake y por qué usarlo aquí?

**Drake** es una librería de simulación y control para robótica.

En este repo se usa para:

- estructurar lógica de control por capas,
- simular interacción en celda colaborativa,
- visualizar y validar decisiones antes de pasar a hardware,
- producir KPIs reproducibles para investigación/aplicación industrial.

En resumen: permite pasar de una demo visual a una narrativa técnica sólida (robustez, mantenibilidad, reproducibilidad).

---

## Estructura del repo

```text
drake_hello/
  drake_lab/
    apps/         # Frontends (Streamlit / Meshcat runners)
    scenarios/    # Motor de simulación y lógica de control
    experiments/  # Benchmarks y comparación de políticas
    core/         # Utilidades base
  legacy/         # Versiones previas/single-file para trazabilidad
  streamlit_app.py
  requirements.txt
  runtime.txt
```

- `streamlit_app.py` es el **entrypoint recomendado para cloud**.
- `legacy/` conserva evolución histórica del proyecto.

---

## Instalación local (WSL/Linux)

```bash
cd "/mnt/c/Users/juand/GitHub Projects/drake_hello"
python3 -m venv .venv_wsl
source .venv_wsl/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Ejecutar demos principales

### 1) Dashboard interactivo (Streamlit)

```bash
streamlit run streamlit_app.py
```

### 2) Playground 3D en Meshcat (pick-sort colaborativo)

```bash
python 9.topic_robot_pick_sort_meshcat.py --wait-for-enter
```

### 3) Benchmark adaptive vs baseline (CSV + summary + plot)

```bash
python 8.topic_rex_policy_benchmark.py --samples 48 --start-seed 200
```

---

## Comando de control rápido (ejemplo útil)

Ejecutar política baseline para comparar contra adaptive:

```bash
python 9.topic_robot_pick_sort_meshcat.py --baseline --uncertainty-scale 1.4 --wait-for-enter
```

Ejecutar política adaptive en condiciones difíciles:

```bash
python 9.topic_robot_pick_sort_meshcat.py --uncertainty-scale 1.8 --wait-for-enter
```

Esto te da una comparación directa de comportamiento y KPIs bajo incertidumbre.

---

## Deploy a Streamlit Community Cloud (gratis)

1. Sube este repo a GitHub (rama `main`).
2. En Streamlit Community Cloud: **New app**.
3. Selecciona:
   - Repository: tu repo
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. Deploy.

### Archivos clave para que funcione en cloud

- `requirements.txt`: dependencias Python.
- `runtime.txt`: fija versión compatible (`python-3.10.16`) para `drake`.

---

## Troubleshooting

### `ModuleNotFoundError: drake_lab`

- Ejecuta desde la raíz del repo, no desde subcarpetas sueltas.

### Meshcat no abre en `localhost`

- Mantén el script corriendo (`--wait-for-enter`).
- Prueba `http://127.0.0.1:7000`.

### Error de deploy en Streamlit Cloud

- Verifica que el repo esté publicado en GitHub.
- Verifica `Main file path = streamlit_app.py`.
- Revisa logs de build por versión de Python/dependencias.

---

## Objetivo técnico del proyecto

Este repo está diseñado para mostrar capacidad en:

- system design para celdas robóticas colaborativas,
- task sequencing + adaptación online,
- robustez bajo incertidumbre,
- trazabilidad de resultados (CSV, summary, plots),
- comunicación técnica clara (demo + evidencia cuantitativa).

