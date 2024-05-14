from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Line
from compas.geometry import Point
from compas.geometry import Vector
from compas_gmsh.models import MeshModel
from compas_viewer import Viewer

# ==============================================================================
# Make a plate mesh
# ==============================================================================

mesh = Mesh.from_meshgrid(dx=10, nx=5)
plate = mesh.thickened(0.3)

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

viewer = Viewer()

viewer.renderer.camera.target = [5, 5, 0]
viewer.renderer.camera.position = [5, -6, 7]

viewer.scene.add(mesh, show_points=False)

poa = Point(*plate.vertex_coordinates(poa))
start = poa + Vector(0, 0, 1)
vector = Vector(0, 0, -1)
load = Line.from_point_and_vector(start, vector)

viewer.scene.add(poa, pointsize=20)
viewer.scene.add(load, linecolor=Color.red(), lineswidth=5, show_points=False)

viewer.show()
