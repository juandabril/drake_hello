from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from drake_lab.scenarios.basic_diagram import build_minimal_diagram


if __name__ == "__main__":
    diagram = build_minimal_diagram()
    print("Step 1 - Minimal Drake diagram created successfully.")
    print("Diagram name:", diagram.get_name() or "<unnamed>")
