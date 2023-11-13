from compas.geometry import Vector, Frame
from compas.geometry import Box
from compas.geometry import Translation

from compas_view2.app import App
from compas_gmsh.models import ShapeModel

# ==============================================================================
# Geometry
# ==============================================================================

b1 = Box(1)
b2 = Box(1, frame=Frame(b1.vertices[6]))

# ==============================================================================
# CSG Model
# ==============================================================================

model = ShapeModel(name="booleans")

model.boolean_fragment([model.add_box(b1)], [model.add_box(b2)])
model.generate_mesh(2)

# ==============================================================================
# Fragments
# ==============================================================================

fragments = []

for surface in model.surfaces:
    mesh = model.surface_mesh(surface)
    fragments.append(mesh)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [1.5, -5, 3]
viewer.view.camera.look_at([1.5, 0, 0])

viewer.add(b1, opacity=0.7, facecolor=(1, 0, 0), linewidth=2)
viewer.add(b2, opacity=0.7, facecolor=(0, 1, 0), linewidth=2)

T2 = Translation.from_vector([3, 0, 0])

for mesh in fragments:
    T1 = Translation.from_vector(Vector(*mesh.centroid()) * 0.2)

    mesh.transform(T2 * T1)
    viewer.add(mesh)

viewer.run()
