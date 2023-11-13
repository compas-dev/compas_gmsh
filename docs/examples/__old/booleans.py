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

model.options.mesh.lmax = 0.05

model.boolean_difference(
    model.boolean_intersection([model.add_sphere(sphere)], [model.add_box(box)]),
    model.boolean_union(
        [model.add_cylinder(cylz)], [model.add_cylinder(cylx), model.add_cylinder(cyly)]
    ),
)

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
viewer.view.camera.position = [10, -7, 3]
viewer.view.camera.look_at([4, 0, 0])

viewer.add(sphere.to_brep(), opacity=0.5, facecolor=(1, 0, 0), linewidth=2)
viewer.add(box.to_brep(), opacity=0.5, facecolor=(0, 1, 0), linewidth=2)
viewer.add(cylx.to_brep(), opacity=0.5, facecolor=(0, 0, 1), linewidth=2)
viewer.add(cyly.to_brep(), opacity=0.5, facecolor=(0, 0, 1), linewidth=2)
viewer.add(cylz.to_brep(), opacity=0.5, facecolor=(0, 0, 1), linewidth=2)

viewer.add(mesh)
viewer.run()
