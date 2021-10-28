from compas.geometry import Sphere, Translation, centroid_points
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

model.lmin = 0.1
model.lmax = 0.2

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
viewer.view.camera.rx = -85
viewer.view.camera.tx = 0
viewer.view.camera.ty = 0
viewer.view.camera.distance = 7

bottom, top = [], []

for tet in tets:
    centroid = centroid_points(tet.vertices)
    if centroid[2] < 0:
        bottom.append(tet)
    else:
        top.append(tet)

T = Translation.from_vector([0, 0, 0.5])
for tet in top:
    tet.transform(T)

T = Translation.from_vector([0, 0, -0.5])
for tet in bottom:
    tet.transform(T)

viewer.add(Collection(bottom), facecolor=(1, 0, 0))
viewer.add(Collection(top), facecolor=(0, 1, 0))

viewer.run()
