from compas.geometry import Sphere

from compas_view2.app import App
from compas_gmsh.models import ShapeModel


# ==============================================================================
# Geometry
# ==============================================================================

sphere = Sphere([0, 0, 0], 2)

# ==============================================================================
# Solid Model
# ==============================================================================

model = ShapeModel(name="quads")

model.add_sphere(sphere)

model.lmin = 0.05
model.lmax = 0.1

model.generate_mesh()
model.recombine_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rz = 0
viewer.view.camera.rx = -55
viewer.view.camera.tx = 0
viewer.view.camera.ty = 0
viewer.view.camera.distance = 7

viewer.add(mesh)

viewer.run()
