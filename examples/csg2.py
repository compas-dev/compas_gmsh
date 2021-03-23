from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas.geometry import Box

from compas.datastructures import Mesh

from compas_view2.app import App
from compas_gmsh.models.model import Model

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
# Solid Model
# ==============================================================================

model = Model(name="csg2")
model.length_min = 0.2
model.length_max = 0.2

# this needs to become `model.add()`
# and delegated to the corresponding ModelObject
# through registration of Object - ModelObject pairs

BOX = model.add_box(box)
SPHERE = model.add_sphere(sphere)
CX = model.add_cylinder(cylinderx)
CY = model.add_cylinder(cylindery)
CZ = model.add_cylinder(cylinderz)

# ideally this is passed to the model
# as a CSG tree
# and executed in one go

I = model.boolean_intersection(BOX, SPHERE)
U = model.boolean_union(model.boolean_union(CX, CY), CZ)
D = model.boolean_difference(I, U)

model.generate_mesh()
model.refine_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App()

viewer.add(mesh)
viewer.run()
