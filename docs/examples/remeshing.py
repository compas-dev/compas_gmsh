from random import choice

import compas
from compas.datastructures import Mesh
from compas.topology import astar_shortest_path
from compas_gmsh.models import MeshModel
from compas_gmsh.options import MeshAlgorithm
from compas_viewer import Viewer

# ==============================================================================
# Input
# ==============================================================================

mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

# =============================================================================
# Target lengths
# =============================================================================

targetlength = {vertex: 1.0 for vertex in mesh.vertices()}

corners = list(mesh.vertices_where(vertex_degree=2))

start = choice(list(set(mesh.vertices()) - set(mesh.vertices_on_boundary())))
end = choice(corners)

for vertex in astar_shortest_path(mesh, start, end):
    targetlength[vertex] = 0.05

# ==============================================================================
# GMSH model
# ==============================================================================

model = MeshModel.from_mesh(mesh, name="tubemesh", targetlength=targetlength)
model.options.mesh.algorithm = MeshAlgorithm.FrontalDelaunay

model.generate_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

# ==============================================================================
# Visualize
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [1, 5, 0]
viewer.renderer.camera.position = [1, -5, 1]

viewer.scene.add(mesh, show_points=False)
viewer.show()
