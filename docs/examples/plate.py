from random import choice
import compas
from compas.geometry import Point, Vector
from compas.datastructures import Mesh, mesh_thicken
from compas.utilities import geometric_key_xy
from compas_gmsh.models import MeshModel
from compas_view2.app import App
from compas_view2.shapes import Arrow

# ==============================================================================
# Make a plate mesh
# ==============================================================================

mesh = Mesh.from_obj(compas.get("faces.obj"))
plate = mesh_thicken(mesh, 0.3)

# ==============================================================================
# Select random internal vertex for load application
# ==============================================================================

poa = choice(list(set(mesh.vertices()) - set(mesh.vertices_on_boundary())))

# ==============================================================================
# GMSH model
# ==============================================================================

model = MeshModel.from_mesh(plate, name="test")

model.heal()

vertex_target = {poa: 0.02}
# vertex_target.update({vertex: 0.2 for vertex in mesh.vertices_on_boundary()})
# vertex_target.update({vertex: 0.02 for vertex in mesh.vertices_where({'vertex_degree': 2})})

# for u in list(vertex_target):
#     a = geometric_key_xy(mesh.vertex_coordinates(u))
#     for v in plate.vertices():
#         b = geometric_key_xy(plate.vertex_coordinates(v))
#         if b == a:
#             vertex_target[v] = vertex_target[u]

for vertex in vertex_target:
    model.vertex_target(vertex, vertex_target[vertex])

model.generate_mesh()
model.optimize_mesh(niter=10)

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()
print(mesh.is_valid())

# ==============================================================================
# Viz
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rz = 0
viewer.view.camera.rx = -55
viewer.view.camera.tx = -5
viewer.view.camera.ty = -2
viewer.view.camera.distance = 10

viewer.add(mesh)

point = Point(* plate.vertex_coordinates(poa)) + Vector(0, 0, 1)
vector = Vector(0, 0, -1)
load = Arrow(point, vector, body_width=0.03)

viewer.add(load, facecolor=(1, 0, 0))

viewer.run()
