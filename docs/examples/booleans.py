from compas.geometry import Point, Vector, Plane
from compas.geometry import Sphere, Cylinder, Box
from compas.geometry import Translation

from compas_view2.app import App
from compas_gmsh.models import ShapeModel

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

cylx = Cylinder((YZ, 0.7 * R), 3 * R)
cyly = Cylinder((ZX, 0.7 * R), 3 * R)
cylz = Cylinder((XY, 0.7 * R), 3 * R)

# ==============================================================================
# CSG Model
# ==============================================================================

model = ShapeModel(name="booleans")

model.mesh_lmin = 0.2
model.mesh_lmax = 0.2

model.boolean_difference(
    model.boolean_intersection(
        [model.add_sphere(sphere)],
        [model.add_box(box)]
    ),
    model.boolean_union(
        [model.add_cylinder(cylz)],
        [model.add_cylinder(cylx), model.add_cylinder(cyly)]
    )
)

model.options.mesh.meshsize_max = 0.1

model.generate_mesh()
model.optimize_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

mesh = model.mesh_to_compas()

mesh.transform(Translation.from_vector([4 * R, 0, 0]))

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rz = -35
viewer.view.camera.rx = -75
viewer.view.camera.tx = -2 * R
viewer.view.camera.ty = 1
viewer.view.camera.distance = 12

viewer.add(sphere, u=32, v=32, opacity=0.5, color=(1, 0, 0))
viewer.add(box, opacity=0.5, color=(0, 1, 0))
viewer.add(cylx, u=32, opacity=0.5, color=(0, 0, 1))
viewer.add(cyly, u=32, opacity=0.5, color=(0, 0, 1))
viewer.add(cylz, u=32, opacity=0.5, color=(0, 0, 1))

viewer.add(mesh)
viewer.run()
