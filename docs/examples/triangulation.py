from compas.geometry import Sphere

from compas_view2.app import App
from compas_gmsh.models import ShapeModel


# ==============================================================================
# Geometry
# ==============================================================================

sphere = Sphere([0, 0, 0], 10)

# ==============================================================================
# Solid Model
# ==============================================================================

model = ShapeModel(name="triangulation")

model.add_sphere(sphere)

model.length_min = 2
model.length_max = 3

model.generate_mesh(3)

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App()

viewer.add(mesh)
viewer.run()
