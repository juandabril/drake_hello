from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from drake_lab.scenarios.mass_spring_damper import simulate_mass_spring_damper


if __name__ == "__main__":
    position, velocity = simulate_mass_spring_damper()
    print("Step 3 - Mass-spring-damper simulation complete (5s, force=1).")
    print(f"Final state: position={position:.3f}, velocity={velocity:.3f}")
