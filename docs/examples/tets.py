from compas.geometry import Sphere, centroid_points
from compas_view2.app import App
from compas_view2.objects import Collection
from compas_gmsh.models import ShapeModel

# ==============================================================================
# Geometry
# ==============================================================================

sphere = Sphere([0, 0, 0], 2)

# ==============================================================================
# Solid Model
# ==============================================================================

model = ShapeModel(name="tets")

model.add_sphere(sphere)

model.length_min = 0.1
model.length_max = 0.2

model.generate_mesh(3)

# ==============================================================================
# COMPAS mesh
# ==============================================================================

tets = model.mesh_to_tets()

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rz = 0
viewer.view.camera.rx = -55
viewer.view.camera.tx = 0
viewer.view.camera.ty = 0
viewer.view.camera.distance = 7

below = []
for tet in tets:
    centroid = centroid_points(tet.vertices)
    if centroid[2] < 0:
        below.append(tet)

viewer.add(Collection(below))

viewer.run()
