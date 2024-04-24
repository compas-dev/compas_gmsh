from random import choice

import compas
from compas.datastructures import Mesh
from compas.topology import astar_shortest_path
from compas_gmsh.models import MeshModel
from compas_gmsh.options import MeshAlgorithm
from compas_view2.app import App

# ==============================================================================
# Input
# ==============================================================================

mesh = Mesh.from_obj(compas.get("tubemesh.obj"))

# =============================================================================
# Target lengths
# =============================================================================

targetlength = {vertex: 1.0 for vertex in mesh.vertices()}

corners = list(mesh.vertices_where({"vertex_degree": 2}))

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

viewer = App(width=1600, height=900)
viewer.view.camera.position = [1, -5, 1]
viewer.view.camera.look_at([1, 5, 0])

viewer.add(mesh)
viewer.run()
