# This reimplements gmsh/demos/boolean/boolean.geo in Python.

import sys
import gmsh

from compas.utilities import rgb_to_hex
from compas.datastructures import Mesh
from compas_viewers.multimeshviewer import MultiMeshViewer
from compas_viewers.multimeshviewer import MeshObject

# ==============================================================================
# Gmsh
# ==============================================================================

gmsh.initialize(sys.argv)

gmsh.option.setNumber("General.Terminal", 1)

gmsh.model.add("boolean")

# from http://en.wikipedia.org/wiki/Constructive_solid_geometry

gmsh.option.setNumber("Mesh.Algorithm", 6)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.4)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.4)

R = 1.4
Rs = R * .7
Rt = R * 1.25

gmsh.model.occ.addBox(-R, -R, -R, 2 * R, 2 * R, 2 * R, 1)
gmsh.model.occ.addSphere(0, 0, 0, Rt, 2)
gmsh.model.occ.intersect([(3, 1)], [(3, 2)], 3)
gmsh.model.occ.addCylinder(-2 * R, 0, 0, 4 * R, 0, 0, Rs, 4)
gmsh.model.occ.addCylinder(0, -2 * R, 0, 0, 4 * R, 0, Rs, 5)
gmsh.model.occ.addCylinder(0, 0, -2 * R, 0, 0, 4 * R, Rs, 6)
gmsh.model.occ.fuse([(3, 4), (3, 5)], [(3, 6)], 7)
gmsh.model.occ.cut([(3, 3)], [(3, 7)], 8)

gmsh.model.occ.synchronize()

gmsh.model.mesh.generate(3)
#gmsh.model.mesh.refine()
#gmsh.model.mesh.setOrder(2)
#gmsh.model.mesh.partition(4)

# gmsh.write("boolean.msh")

# ==============================================================================
# Mesh nodes
# ==============================================================================

nodes = gmsh.model.mesh.getNodes()
node_tags = nodes[0]
node_coords = nodes[1].reshape((-1, 3), order='C')
node_paramcoords = nodes[2]

xyz = {}
for tag, coords  in zip(node_tags, node_coords):
    xyz[int(tag)] = coords.tolist()

# ==============================================================================
# Mesh elements
# ==============================================================================

elements = gmsh.model.mesh.getElements()

lines = []
triangles = []
points = []

for etype, etags, ntags in zip(*elements):
    if etype == 1:
        # lines
        pass
    elif etype == 2:
        # triangles
        for i, etag in enumerate(etags):
            n = gmsh.model.mesh.getElementProperties(etype)[3]
            triangle = ntags[i * n: i * n + n]
            triangles.append(triangle.tolist())

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = Mesh.from_vertices_and_faces(xyz, triangles)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

meshes = []
meshes.append(MeshObject(mesh, color=rgb_to_hex((210, 210, 210))))

viewer = MultiMeshViewer()
viewer.meshes = meshes

viewer.show()

# ==============================================================================
# Shutdown
# ==============================================================================

gmsh.finalize()
