from compas.geometry import Point, Vector, Plane
from compas.geometry import Sphere, Cylinder, Box
from compas.geometry import Translation

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

cylx = Cylinder((YZ, 0.7 * R), 3 * R)
cyly = Cylinder((ZX, 0.7 * R), 3 * R)
cylz = Cylinder((XY, 0.7 * R), 3 * R)

# ==============================================================================
# CSG Model
# ==============================================================================

tree = {
    'difference': [
        {'intersection': [sphere, box]},
        {'union': [cylx, cyly, cylz]}
    ]
}

model = CSGModel(tree, name="csg")

model.options.mesh.lmax = 0.1

model.compute_tree()

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

viewer.add(sphere, u=32, v=32, opacity=0.5, facecolor=(1, 0, 0))
viewer.add(box, opacity=0.5, facecolor=(0, 1, 0))
viewer.add(cylx, u=32, opacity=0.5, facecolor=(0, 0, 1))
viewer.add(cyly, u=32, opacity=0.5, facecolor=(0, 0, 1))
viewer.add(cylz, u=32, opacity=0.5, facecolor=(0, 0, 1))

viewer.add(mesh)
viewer.run()
