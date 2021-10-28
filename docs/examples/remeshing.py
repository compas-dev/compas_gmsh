from math import radians
import compas
from compas.geometry import Point, Translation, Rotation, Scale
from compas.datastructures import Mesh
from compas_gmsh.models import MeshModel
from compas_view2.app import App

# ==============================================================================
# Input
# ==============================================================================

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))

centroid = Point(* mesh.centroid())
vector = Point(0, 0, 0) - centroid
vector.z = 0

T = Translation.from_vector(vector)
R = Rotation.from_axis_and_angle([0, 0, 1], radians(105))
S = Scale.from_factors([0.3, 0.3, 0.3])

mesh.transform(S * R * T)

# ==============================================================================
# GMSH model
# ==============================================================================

model = MeshModel.from_mesh(mesh, 1.0, name='tubemesh')

model.length_min = 0.1
model.length_max = 0.2

model.generate_mesh()
model.optimize_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rx = -75
viewer.view.camera.tx = -1
viewer.view.camera.ty = 0

viewer.add(mesh)

viewer.run()
