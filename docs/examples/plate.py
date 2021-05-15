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
# Set target sizes at load vertex and on boundaries and corners
# ==============================================================================

vertex_target = {poa: 0.02}
vertex_target.update({vertex: 0.2 for vertex in mesh.vertices_on_boundary()})
vertex_target.update({vertex: 0.02 for vertex in mesh.vertices_where({'vertex_degree': 2})})

for u in list(vertex_target):
    a = geometric_key_xy(mesh.vertex_coordinates(u))
    for v in plate.vertices():
        b = geometric_key_xy(plate.vertex_coordinates(v))
        if b == a:
            vertex_target[v] = vertex_target[u]

# ==============================================================================
# Make meshing model
# ==============================================================================

model = MeshModel.from_mesh(plate, 1.0, name="test", vertex_length=vertex_target)

model.generate_mesh(2)
model.optimize_mesh(niter=10)

# ==============================================================================
# Viz
# ==============================================================================

viewer = App()
viewer.add(model.mesh_to_compas())

viewer.add(
    Arrow(
        Point(* plate.vertex_coordinates(poa)) + Vector(0, 0, 1), Vector(0, 0, -1),
        body_width=0.03
    ),
    facecolor=(1, 0, 0)
)

viewer.run()
