from pydrake.all import ConstantVectorSource, DiagramBuilder


def build_minimal_diagram():
    """Build a valid non-empty diagram."""
    builder = DiagramBuilder()
    builder.AddSystem(ConstantVectorSource([1.0]))
    return builder.Build()

