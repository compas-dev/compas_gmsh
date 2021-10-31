from math import radians
import compas
from compas.geometry import Point, Line, Translation, Rotation, Scale
from compas.datastructures import Mesh
from compas_gmsh.models import MeshModel
from compas_view2.app import App

# ==============================================================================
# Input
# ==============================================================================

mesh = Mesh.from_json(compas.get('tubemesh.json'))

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

model = MeshModel.from_mesh(mesh, name='tubemesh')

for vertex in list(mesh.vertices())[:10]:
    model.vertex_target(vertex, 0.05)

for vertex in list(mesh.vertices())[10:]:
    model.vertex_target(vertex, 0.5)

model.generate_mesh()
model.optimize_mesh(niter=10)

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

for u, v in mesh.edges():
    a = mesh.vertex_coordinates(u)
    b = mesh.vertex_coordinates(v)

    if mesh.halfedge[u][v] is None:
        viewer.add(Line(a, b), linewidth=10, color=(1, 0, 0))
    elif mesh.halfedge[v][u] is None:
        viewer.add(Line(a, b), linewidth=10, color=(1, 0, 0))

viewer.run()
