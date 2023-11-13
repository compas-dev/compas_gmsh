from compas.geometry import Point, Vector
from compas.datastructures import Mesh, mesh_thicken
from compas_gmsh.models import MeshModel
from compas_view2.app import App
from compas_view2.shapes import Arrow

# ==============================================================================
# Make a plate mesh
# ==============================================================================

mesh = Mesh.from_meshgrid(dx=10, nx=5)
plate = mesh_thicken(mesh, 0.3)

# ==============================================================================
# GMSH model
# ==============================================================================

model = MeshModel.from_mesh(plate, targetlength=2.0)

# =============================================================================
# Target lengths
# =============================================================================

poa = list(mesh.vertices_where({"x": 4.0, "y": 4.0}))[0]
model.mesh_targetlength_at_vertex(poa, 0.01)

for vertex in mesh.vertices_on_boundary():
    for point in model.find_points_at_xy(mesh.vertex_coordinates(vertex)):
        model.mesh_targetlength_at_point(point, 0.1)

for vertex in mesh.vertices_where({"vertex_degree": 2}):
    tag = model.find_point_at_vertex(vertex)
    model.mesh_targetlength_at_point(tag, 0.1)

model.generate_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

# ==============================================================================
# Viz
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [5, -6, 7]
viewer.view.camera.look_at([5, 5, 0])

viewer.add(mesh)

poa = Point(*plate.vertex_coordinates(poa))
start = poa + Vector(0, 0, 1)
vector = Vector(0, 0, -1)
load = Arrow(start, vector, body_width=0.03)

viewer.add(poa, pointsize=20)
viewer.add(load, facecolor=(1, 0, 0))

viewer.run()
