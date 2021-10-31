from compas.geometry import Sphere, Translation
from compas_view2.app import App
from compas_gmsh.models import ShapeModel

# ==============================================================================
# Geometry
# ==============================================================================

sphere = Sphere([0, 0, 0], 2)

# ==============================================================================
# Solid Model
# ==============================================================================

model = ShapeModel(name="trimesh")

model.add_sphere(sphere)

model.mesh_lmin = 0.1
model.mesh_lmax = 0.2

model.generate_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

model.refine_mesh()

trimesh = model.mesh_to_compas()

model.recombine_mesh()

quadmesh = model.mesh_to_compas()

quadmesh.transform(Translation.from_vector([5, 0, 0]))

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rz = 0
viewer.view.camera.rx = -55
viewer.view.camera.tx = -2.5
viewer.view.camera.ty = 0
viewer.view.camera.distance = 7

viewer.add(trimesh)
viewer.add(quadmesh)

viewer.run()
