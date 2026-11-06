# pyright: strict

"""Strict typing consumer for the installed wheel."""

import numpy as np
import numpy.typing as npt

from compas.datastructures import Mesh
from compas_gmsh.models import Model


def consume(model: Model) -> None:
    """Consume representative public return types without source access."""
    points: list[int] = model.points
    vertices: dict[int, npt.NDArray[np.float64]] = model.mesh_node_xyz()
    mesh: Mesh = model.mesh_to_compas()
    model.generate_mesh(2)
    model.destroy()
    print(points, vertices, mesh)
