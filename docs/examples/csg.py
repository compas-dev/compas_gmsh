from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Plane
from compas.geometry import Sphere
from compas.geometry import Cylinder
from compas.geometry import Box

from compas_view2.app import App
from compas_gmsh.models import CSGModel

# ==============================================================================
# Geometry
# ==============================================================================

R = 1.4

P = Point(0, 0, 0)
X = Vector(1, 0, 0)
Y = Vector(0, 1, 0)
Z = Vector(0, 0, 1)
YZ = Plane(P, X)
ZX = Plane(P, Y)
XY = Plane(P, Z)

box = Box.from_width_height_depth(2 * R, 2 * R, 2 * R)
sphere = Sphere(P, 1.25 * R)

cylx = Cylinder((YZ, 0.7 * R), 4 * R)
cyly = Cylinder((ZX, 0.7 * R), 4 * R)
cylz = Cylinder((XY, 0.7 * R), 4 * R)

# ==============================================================================
# CSG Model
# ==============================================================================

tree = {'difference': [{'intersection': [sphere, box]}, {'union': [cylx, cyly, cylz]}]}

model = CSGModel(tree, name="csg")
model.length_min = 0.2
model.length_max = 0.2

model.compute_tree()
model.generate_mesh()
model.refine_mesh()
model.optimize_mesh()

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
