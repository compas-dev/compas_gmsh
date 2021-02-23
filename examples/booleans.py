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

from compas_view2.app import App


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
        return 3, tag

    def add_sphere(self, sphere):
        x, y, z = sphere.point
        R = sphere.radius
        tag = self.factory.addSphere(x, y, z, R)
        return 3, tag

    def add_box(self, box):
        x0, y0, z0 = box.frame.point
        x = x0 - 0.5 * box.xsize
        y = y0 - 0.5 * box.ysize
        z = z0 - 0.5 * box.zsize
        tag = self.factory.addBox(x, y, z, box.xsize, box.ysize, box.zsize)
        return 3, tag

    def boolean_intersection(self, A, B):
        # the dim is necessary because tags are only unique per dimension
        result = self.factory.intersect([A], [B])
        objects = result[0]
        return objects[0]  # return the dim and the tag

    def boolean_union(self, A, B):
        result = self.factory.fuse([A], [B])
        objects = result[0]
        return objects[0]

    def boolean_difference(self, A, B):
        result = self.factory.cut([A], [B])
        objects = result[0]
        return objects[0]


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

# types = gmsh.model.mesh.getElementTypes()
# for number in types:
#     props = gmsh.model.mesh.getElementProperties(number)
#     name = props[0]
#     dim = props[1]
#     order = props[2]
#     number_of_nodes = props[3]
#     local_node_coords = props[4]
#     number_of_primary_nodes = props[5]
#     print(name)
#     print('--', number)
#     print('--', dim)
#     print('--', order)
#     print('--', number_of_nodes)
#     print('--', local_node_coords)
#     print('--', number_of_primary_nodes)

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
tetrahedrons = []
points = []

for etype, etags, ntags in zip(*elements):
    if not etype:
        continue
    if etype == 1:
        # lines
        pass
    elif etype == 2:
        # triangles
        for i, etag in enumerate(etags):
            n = gmsh.model.mesh.getElementProperties(etype)[3]
            triangle = ntags[i * n: i * n + n]
            triangles.append(triangle.tolist())
    elif etype == 3:
        # tetrahedrons
        pass
    elif etype == 15:
        # points
        pass

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = Mesh.from_vertices_and_faces(xyz, triangles)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App()

viewer.add(mesh)
viewer.run()

# ==============================================================================
# Shutdown
# ==============================================================================

gmsh.finalize()
