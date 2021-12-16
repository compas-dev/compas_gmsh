from random import choice
from compas.geometry import Point, Vector
from compas.datastructures import Mesh, mesh_thicken
from compas.utilities import geometric_key_xy
from compas_gmsh.models import MeshModel
from compas_view2.app import App
from compas_view2.shapes import Arrow

# ==============================================================================
# Make a plate mesh
# ==============================================================================

mesh = Mesh.from_meshgrid(dx=10, nx=5)
plate = mesh_thicken(mesh, 0.3)

# ==============================================================================
# Select random internal vertex for load application
# ==============================================================================

poa = choice(list(set(mesh.vertices()) - set(mesh.vertices_on_boundary())))

# ==============================================================================
# GMSH model
# ==============================================================================

model = MeshModel.from_mesh(plate, targetlength=2.0)

model.mesh_targetlength_at_vertex(poa, 0.01)

for vertex in mesh.vertices_on_boundary():
    a = geometric_key_xy(mesh.vertex_coordinates(vertex))
    for vertex in plate.vertices():
        b = geometric_key_xy(plate.vertex_coordinates(vertex))
        if a == b:
            model.mesh_targetlength_at_vertex(vertex, 0.1)

for vertex in mesh.vertices_where({'vertex_degree': 2}):
    model.mesh_targetlength_at_vertex(vertex, 0.01)

# model.heal()
model.generate_mesh()
# model.optimize_mesh(niter=10)
# model.recombine_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

lengths = [mesh.edge_length(*edge) for edge in mesh.edges()]

print(mesh.is_valid())
print(min(lengths))
print(max(lengths))

omesh = model.mesh_to_openmesh()
print(omesh)

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

poa = Point(* plate.vertex_coordinates(poa))
start = poa + Vector(0, 0, 1)
vector = Vector(0, 0, -1)
load = Arrow(start, vector, body_width=0.03)

viewer.add(poa, size=20)
viewer.add(load, facecolor=(1, 0, 0))

viewer.run()
