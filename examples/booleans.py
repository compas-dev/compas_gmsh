# This reimplements gmsh/demos/boolean/boolean.geo in Python.

import sys
import gmsh

from compas.utilities import rgb_to_hex
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas.geometry import Box
from compas.datastructures import Mesh
from compas_viewers.multimeshviewer import MultiMeshViewer
from compas_viewers.multimeshviewer import MeshObject


class Factory(object):

    def __init__(self, factory):
        self.factory = factory

    def add_cylinder(self, cylinder):
        H = cylinder.height
        R = cylinder.radius
        base = cylinder.plane.point
        normal = cylinder.plane.normal
        start = base + normal.scaled(-0.5 * H)
        vector = normal.scaled(H)
        x0, y0, z0 = start
        dx, dy, dz = vector
        tag = self.factory.addCylinder(x0, y0, z0, dx, dy, dz, R)
        return tag

    def add_sphere(self, sphere):
        x, y, z = sphere.point
        R = sphere.radius
        tag = self.factory.addSphere(x, y, z, R)
        return tag

    def add_box(self, box):
        x0, y0, z0 = box.frame.point
        x = x0 - 0.5 * box.xsize
        y = y0 - 0.5 * box.ysize
        z = z0 - 0.5 * box.zsize
        tag = self.factory.addBox(x, y, z, box.xsize, box.ysize, box.zsize)
        return tag

    def boolean_intersection(self, A, B, dim=3):
        objects_in = [(dim, A)]
        tools_in = [(dim, B)]
        res = self.factory.intersect(objects_in, tools_in)
        objects_out = res[0]
        obj = objects_out[0]
        obj_dim, obj_tag = obj
        return obj_tag

    def boolean_union(self, A, B, dim=3):
        objects_in = [(dim, A)]
        tools_in = [(dim, B)]
        res = self.factory.fuse(objects_in, tools_in)
        objects_out = res[0]
        obj = objects_out[0]
        obj_dim, obj_tag = obj
        return obj_tag

    def boolean_difference(self, A, B, dim=3):
        objects_in = [(dim, A)]
        tools_in = [(dim, B)]
        res = self.factory.cut(objects_in, tools_in)
        objects_out = res[0]
        obj = objects_out[0]
        obj_dim, obj_tag = obj
        return obj_tag


# ==============================================================================
# Geometry
# ==============================================================================

R = 1.4

O = Point(0, 0, 0)
X = Vector(1, 0, 0)
Y = Vector(0, 1, 0)
Z = Vector(0, 0, 1)
YZ = Plane(O, X)
ZX = Plane(O, Y)
XY = Plane(O, Z)

box = Box.from_width_height_depth(2 * R, 2 * R, 2 * R)
sphere = Sphere(O, 1.25 * R)

cylinderX = Cylinder((YZ, 0.7 * R), 4 * R)
cylinderY = Cylinder((ZX, 0.7 * R), 4 * R)
cylinderZ = Cylinder((XY, 0.7 * R), 4 * R)

# ==============================================================================
# Gmsh
# ==============================================================================

gmsh.initialize(sys.argv)

gmsh.option.setNumber("General.Terminal", 0)
gmsh.option.setNumber("Mesh.Algorithm", 6)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.2)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.2)

gmsh.model.add("boolean")

factory = Factory(gmsh.model.occ)

b = factory.add_box(box)
s = factory.add_sphere(sphere)
cx = factory.add_cylinder(cylinderX)
cy = factory.add_cylinder(cylinderY)
cz = factory.add_cylinder(cylinderZ)

intersection = factory.boolean_intersection(b, s)
union = factory.boolean_union(factory.boolean_union(cx, cy), cz)
cut = factory.boolean_difference(intersection, union)

gmsh.model.occ.synchronize()
gmsh.model.mesh.generate(2)
gmsh.model.mesh.refine()
#gmsh.model.mesh.setOrder(2)
#gmsh.model.mesh.partition(4)

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
tetrahedrons = []

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
