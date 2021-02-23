import sys
import gmsh

from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas.geometry import Box
from compas.geometry import Torus
from compas.geometry import Capsule

from compas.datastructures import Mesh
from compas.utilities import rgb_to_hex

from compas_viewers.multimeshviewer import MultiMeshViewer
from compas_viewers.multimeshviewer import MeshObject


class Model(object):

    def __init__(self, name):
        self.name = name
        self.model = gmsh.model
        self.mesh = gmsh.model.mesh
        self.factory = gmsh.model.occ

    def info(self):
        types = self.model.mesh.getElementTypes()
        for number in types:
            props = self.model.mesh.getElementProperties(number)
            name = props[0]
            dim = props[1]
            order = props[2]
            number_of_nodes = props[3]
            local_node_coords = props[4]
            number_of_primary_nodes = props[5]
            print(name)
            print('--', number)
            print('--', dim)
            print('--', order)
            print('--', number_of_nodes)
            print('--', local_node_coords)
            print('--', number_of_primary_nodes)

    def synchronize(self):
        self.factory.synchronize()

    def generate_mesh(self, dim=2):
        self.synchronize()
        self.model.mesh.generate(dim)

    def refine_mesh(self):
        self.model.mesh.refine()

    def mesh_to_compas(self):
        nodes = self.mesh.getNodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order='C')
        node_paramcoords = nodes[2]
        xyz = {}
        for tag, coords  in zip(node_tags, node_coords):
            xyz[int(tag)] = coords.tolist()
        elements = self.mesh.getElements()
        triangles = []
        for etype, etags, ntags in zip(*elements):
            if etype == 2:
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    triangle = ntags[i * n: i * n + n]
                    triangles.append(triangle.tolist())
        return Mesh.from_vertices_and_faces(xyz, triangles)

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

    def boolean_fragment(self, A, B):
        pass


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

cylinderx = Cylinder((YZ, 0.7 * R), 4 * R)
cylindery = Cylinder((ZX, 0.7 * R), 4 * R)
cylinderz = Cylinder((XY, 0.7 * R), 4 * R)

# ==============================================================================
# Gmsh
# ==============================================================================

gmsh.initialize(sys.argv)
gmsh.option.setNumber("General.Terminal", 1)
gmsh.option.setNumber("Mesh.Algorithm", 6)
gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 0.2)
gmsh.option.setNumber("Mesh.CharacteristicLengthMax", 0.2)

# ==============================================================================
# Solid Model
# ==============================================================================

model = Model(name="boolean")

BOX = model.add_box(box)
SPHERE = model.add_sphere(sphere)
CX = model.add_cylinder(cylinderx)
CY = model.add_cylinder(cylindery)
CZ = model.add_cylinder(cylinderz)

I = model.boolean_intersection(BOX, SPHERE)
U = model.boolean_union(model.boolean_union(CX, CY), CZ)
D = model.boolean_difference(I, U)

model.generate_mesh(2)
model.refine_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

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
