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

# ==============================================================================
# CSG Model
# ==============================================================================

model = ShapeModel(name="booleans")

model.lmin = 0.2
model.lmax = 0.2

model.boolean_fragment(
    [model.add_sphere(sphere)],
    [model.add_box(box)]
)

model.generate_mesh()
model.refine_mesh()
model.optimize_mesh()

# ==============================================================================
# COMPAS mesh
# ==============================================================================

# mesh = model.mesh_to_compas()

print(model.model.getEntities())

# mesh.transform(Translation.from_vector([4 * R, 0, 0]))

# # ==============================================================================
# # Visualization with viewer
# # ==============================================================================

# viewer = App(width=1600, height=900)

# viewer.view.camera.rz = 0
# viewer.view.camera.rx = -75
# viewer.view.camera.tx = -2 * R
# viewer.view.camera.ty = 0
# viewer.view.camera.distance = 10

# viewer.add(sphere, u=32, v=32, opacity=0.5, color=(1, 0, 0))
# viewer.add(box, opacity=0.5, color=(0, 1, 0))

# viewer.add(mesh, opacity=0.5)
# viewer.run()
