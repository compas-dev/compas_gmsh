from compas.colors import Color
from compas.geometry import Box
from compas.geometry import Frame
from compas.geometry import Translation
from compas.geometry import Vector
from compas_gmsh.models import ShapeModel
from compas_view2.app import App

# ==============================================================================
# Geometry
# ==============================================================================

b1 = Box(1)
b2 = Box(1, frame=Frame(b1.vertices[6]))

# ==============================================================================
# CSG Model
# ==============================================================================

model = ShapeModel(name="booleans")

model.options.mesh.lmin = 0.05
model.options.mesh.lmax = 0.05

model.boolean_fragment([model.add_box(b1)], [model.add_box(b2)])
model.generate_mesh(3)
model.optimize_mesh()

# ==============================================================================
# Fragments
# ==============================================================================

fragments = []

for volume in model.volumes:
    mesh = model.volume_mesh(volume)
    fragments.append(mesh)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [2.5, -4, 1]
viewer.view.camera.look_at([2, 0, 0])

T1 = Translation.from_vector([3, 0, 0])

viewer.add(b1, opacity=0.7, facecolor=(1, 0, 0), show_lines=False)
viewer.add(b2, opacity=0.7, facecolor=(0, 1, 0), show_lines=False)

for tag in model.points:
    viewer.add(model.point_to_point(tag))

for tag in model.curves:
    viewer.add(model.curve_to_polyline(tag), linewidth=3)

colors = [Color.red(), Color.grey(), Color.green()]
for i, mesh in enumerate(fragments):
    T2 = Translation.from_vector(Vector(*mesh.centroid()) * 0.5)
    mesh.transform(T1 * T2)
    viewer.add(mesh, facecolor=colors[i])

viewer.run()
