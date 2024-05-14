from compas.colors import Color
from compas.datastructures import Mesh
from compas.geometry import Sphere
from compas.geometry import Translation
from compas.geometry import centroid_points
from compas.tolerance import Tolerance
from compas_gmsh.models import ShapeModel
from compas_viewer import Viewer

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

tol = Tolerance()

centroid_face = {}
for face in shell.faces():
    centroid_face[tol.geometric_key(shell.face_centroid(face))] = face

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
    if any(tol.geometric_key(centroid_points([tet.vertices[index] for index in face])) in centroid_face for face in tet.faces):
        bottom_exterior.append(tet)
    else:
        bottom_interior.append(tet)

for tet in top:
    if any(tol.geometric_key(centroid_points([tet.vertices[index] for index in face])) in centroid_face for face in tet.faces):
        top_exterior.append(tet)
    else:
        top_interior.append(tet)

# ==============================================================================
# This is a temp hack
# ==============================================================================

bottom_ext = Mesh()
for tet in bottom_exterior:
    bottom_ext.join(Mesh.from_vertices_and_faces(tet.vertices, tet.faces), weld=False)

bottom_int = Mesh()
for tet in bottom_interior:
    bottom_int.join(Mesh.from_vertices_and_faces(tet.vertices, tet.faces), weld=False)

top_ext = Mesh()
for tet in top_exterior:
    top_ext.join(Mesh.from_vertices_and_faces(tet.vertices, tet.faces), weld=False)

top_int = Mesh()
for tet in top_interior:
    top_int.join(Mesh.from_vertices_and_faces(tet.vertices, tet.faces), weld=False)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = Viewer()

viewer.renderer.camera.target = [0, 0, 0]
viewer.renderer.camera.position = [0, -8, 0]

T = Translation.from_vector([0, 0, 0.5])
top_ext.transform(T)
top_int.transform(T)

T = Translation.from_vector([0, 0, -0.5])
bottom_ext.transform(T)
bottom_int.transform(T)

viewer.scene.add(bottom_ext, facecolor=Color.red(), show_points=False)
viewer.scene.add(bottom_int, show_points=False)
viewer.scene.add(top_ext, facecolor=Color.green(), show_points=False)
viewer.scene.add(top_int, show_points=False)

viewer.show()
