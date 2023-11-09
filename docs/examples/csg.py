from compas.geometry import Frame
from compas.geometry import Sphere, Cylinder, Box
from compas.geometry import Translation

from compas_view2.app import App
from compas_gmsh.models import CSGModel

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

viewer.add(sphere.to_brep(), opacity=0.5, facecolor=(1, 0, 0))
viewer.add(box.to_brep(), opacity=0.5, facecolor=(0, 1, 0))
viewer.add(cylx.to_brep(), opacity=0.5, facecolor=(0, 0, 1))
viewer.add(cyly.to_brep(), opacity=0.5, facecolor=(0, 0, 1))
viewer.add(cylz.to_brep(), opacity=0.5, facecolor=(0, 0, 1))

viewer.add(mesh)
viewer.run()
