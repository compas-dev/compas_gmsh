from compas.geometry import Box
from compas.geometry import Frame

from compas.datastructures import Mesh

from compas_view2.app import App
from compas_gmsh.model import Model


# ==============================================================================
# Geometry
# ==============================================================================

b1 = Box(Frame([+4, +4, 0], [1, 0, 0], [0, 1, 0]), 10, 10, 10)
b2 = Box(Frame([-4, -4, 0], [1, 0, 0], [0, 1, 0]), 10, 10, 10)

# ==============================================================================
# Solid Model
# ==============================================================================

model = Model(name="csg1")

B1 = model.add_box(b1)
B2 = model.add_box(b2)

model.boolean_union(B1, B2)

model.length_min = 0.2
model.length_max = 0.5

model.generate_mesh()
model.refine_mesh()

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
