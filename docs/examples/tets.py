from compas.geometry import Sphere, Translation, centroid_points
from compas.utilities import geometric_key
from compas_view2.app import App
from compas_view2.objects import Collection
from compas_gmsh.models import ShapeModel

# ==============================================================================
# Geometry
# ==============================================================================

sphere = Sphere(2)

# ==============================================================================
# Solid Model
# ==============================================================================

model = ShapeModel(name="tets")
model.options.mesh.lmax = 0.2

model.add_sphere(sphere)
model.generate_mesh(3)

# ==============================================================================
# COMPAS mesh
# ==============================================================================

tets = model.mesh_to_tets()
shell = model.mesh_to_compas()

# ==============================================================================
# Boundary lookup
# ==============================================================================

# replace by model method

centroid_face = {}
for face in shell.faces():
    centroid_face[geometric_key(shell.face_centroid(face))] = face

bottom_exterior = []
bottom_interior = []

top_exterior = []
top_interior = []

bottom, top = [], []
for tet in tets:
    centroid = centroid_points(tet.vertices)
    if centroid[2] < 0:
        bottom.append(tet)
    else:
        top.append(tet)

for tet in bottom:
    if any(
        geometric_key(centroid_points([tet.vertices[index] for index in face]))
        in centroid_face
        for face in tet.faces
    ):
        bottom_exterior.append(tet)
    else:
        bottom_interior.append(tet)

for tet in top:
    if any(
        geometric_key(centroid_points([tet.vertices[index] for index in face]))
        in centroid_face
        for face in tet.faces
    ):
        top_exterior.append(tet)
    else:
        top_interior.append(tet)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [0, -8, 0]
viewer.view.camera.look_at([0, 0, 0])

T = Translation.from_vector([0, 0, 0.5])
for tet in top:
    tet.transform(T)

T = Translation.from_vector([0, 0, -0.5])
for tet in bottom:
    tet.transform(T)

viewer.add(Collection(bottom_exterior), facecolor=(1, 0, 0))
viewer.add(Collection(bottom_interior))

viewer.add(Collection(top_exterior), facecolor=(0, 1, 0))
viewer.add(Collection(top_interior))

# viewer.add(shell)

viewer.run()
