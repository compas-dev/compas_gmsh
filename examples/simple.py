import gmsh
import sys
import numpy

from compas.datastructures import Mesh
from compas_plotters import MeshPlotter

gmsh.initialize(sys.argv)
gmsh.model.add("square")

a = gmsh.model.geo.addPoint(0, 0, 0, 0.1)
b = gmsh.model.geo.addPoint(1, 0, 0, 0.1)
c = gmsh.model.geo.addPoint(1, 1, 0, 0.1)
d = gmsh.model.geo.addPoint(0, 1, 0, 0.1)
ab = gmsh.model.geo.addLine(a, b)
bc = gmsh.model.geo.addLine(b, c)
cd = gmsh.model.geo.addLine(c, d)
da = gmsh.model.geo.addLine(d, a)
loop = gmsh.model.geo.addCurveLoop([ab, bc, cd, da])
surf = gmsh.model.geo.addPlaneSurface([loop])

gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)

# types = gmsh.model.mesh.getElementTypes()
# for t in types:
#     props = gmsh.model.mesh.getElementProperties(t)
#     name = props[0]
#     dim = props[1]
#     order = props[2]
#     number_of_nodes = props[3]
#     local_node_coords = props[4]
#     number_of_primary_nodes = props[5]
#     print(name)
#     print('--', t)
#     print('--', dim)
#     print('--', order)
#     print('--', number_of_nodes)
#     print('--', local_node_coords)
#     print('--', number_of_primary_nodes)

nodes = gmsh.model.mesh.getNodes()
node_tags = nodes[0]
node_coords = nodes[1].reshape((-1, 3), order='C')
node_paramcoords = nodes[2]

xyz = {}
for tag, coords  in zip(node_tags, node_coords):
    xyz[int(tag)] = coords.tolist()

elements = gmsh.model.mesh.getElements()
elem_types = elements[0]
elem_tags = elements[1]
node_tags = elements[2]

# lines = []
# etype = elem_types[0]  # 1
# for i, etag in enumerate(elem_tags[0]):
#     n = gmsh.model.mesh.getElementProperties(etype)[3]
#     ntags = node_tags[0][i * n: i * n + n]
#     lines.append(ntags.tolist())

triangles = []
etype = elem_types[1]  # 2
for i, etag in enumerate(elem_tags[1]):
    n = gmsh.model.mesh.getElementProperties(etype)[3]
    ntags = node_tags[1][i * n: i * n + n]
    triangles.append(ntags.tolist())

# points = []
# etype = elem_types[2]  # 15
# for i, etag in enumerate(elem_tags[2]):
#     n = gmsh.model.mesh.getElementProperties(etype)[3]
#     ntags = node_tags[2][i * n: i * n + n]
#     if n == 1:
#         points.append(ntags.tolist()[0])

# ==============================================================================
# Make a COMPAS mesh
# ==============================================================================

mesh = Mesh.from_vertices_and_faces(xyz, triangles)

# ==============================================================================
# Visualize using the mesh plotter
# ==============================================================================

plotter = MeshPlotter(mesh, figsize=(8, 5))
plotter.draw_vertices(radius=0.005)
plotter.draw_faces()
plotter.show()

# ==============================================================================
# Shutdown
# ==============================================================================

gmsh.finalize()
