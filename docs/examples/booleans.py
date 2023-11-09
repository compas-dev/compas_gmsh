from compas.geometry import Frame
from compas.geometry import Sphere, Cylinder, Box
from compas.geometry import Translation

from compas_view2.app import App
from compas_gmsh.models import ShapeModel

# ==============================================================================
# Geometry
# ==============================================================================

R = 1.4

box = Box(2 * R)
sphere = Sphere(radius=1.25 * R)

cylx = Cylinder(radius=0.7 * R, height=3 * R, frame=Frame.worldYZ())
cyly = Cylinder(radius=0.7 * R, height=3 * R, frame=Frame.worldZX())
cylz = Cylinder(radius=0.7 * R, height=3 * R, frame=Frame.worldXY())

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

viewer.add(sphere, u=32, v=32, opacity=0.5, facecolor=(1, 0, 0))
viewer.add(box, opacity=0.5, facecolor=(0, 1, 0))
viewer.add(cylx, u=32, opacity=0.5, facecolor=(0, 0, 1))
viewer.add(cyly, u=32, opacity=0.5, facecolor=(0, 0, 1))
viewer.add(cylz, u=32, opacity=0.5, facecolor=(0, 0, 1))

viewer.add(mesh)
viewer.run()
