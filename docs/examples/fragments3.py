from compas.geometry import Point, Vector, Frame
from compas.geometry import Box
from compas.geometry import Translation
from compas.datastructures import Mesh

from compas_view2.app import App
from compas_gmsh.models import ShapeModel

# ==============================================================================
# Geometry
# ==============================================================================

b1 = Box(Frame.worldXY(), 1, 1, 1)
b2 = Box(Frame(b1.vertices[6], Vector.Xaxis(), Vector.Yaxis()), 1, 1, 1)

# ==============================================================================
# CSG Model
# ==============================================================================

model = ShapeModel(name="booleans")

model.options.mesh.lmin = 0.2
model.options.mesh.lmax = 0.2

model.boolean_fragment(
    [model.add_box(b1)],
    [model.add_box(b2)]
)

model.generate_mesh(3)
model.optimize_mesh()

# ==============================================================================
# Fragments
# ==============================================================================

# this needs to be integrated in the lib
# PRs very welcome! :)

nodes = model.mesh.get_nodes()
node_tags = nodes[0]
node_coords = nodes[1].reshape((-1, 3), order='C')
vertices = {}
for tag, coords in zip(node_tags, node_coords):
    vertices[int(tag)] = coords

fragments = []

for dim, tag in model.model.get_entities(3):
    _, downward = model.model.get_adjacencies(dim, tag)
    faces = []
    for tag in downward:
        elements = model.mesh.get_elements(dim - 1, tag)
        for etype, etags, ntags in zip(*elements):
            for i, etag in enumerate(etags):
                n = model.mesh.get_element_properties(etype)[3]
                faces.append(ntags[i * n: i * n + n])
    mesh = Mesh.from_vertices_and_faces(vertices, faces)
    mesh.remove_unused_vertices()
    fragments.append(mesh)

# ==============================================================================
# Visualization with viewer
# ==============================================================================

viewer = App(width=1600, height=900)

viewer.view.camera.rz = 0
viewer.view.camera.rx = -75
viewer.view.camera.tx = 0
viewer.view.camera.ty = 0
viewer.view.camera.distance = 10

viewer.add(b1, opacity=0.7, facecolor=(1, 0, 0), linewidth=2)
viewer.add(b2, opacity=0.7, facecolor=(0, 1, 0), linewidth=2)

T2 = Translation.from_vector([3, 0, 0])

point = Point(0, 0, 0)
for mesh in fragments:
    centroid = Point(* mesh.centroid())
    vector = centroid - point
    T1 = Translation.from_vector(vector * 0.2)

    mesh.transform(T2 * T1)

    viewer.add(mesh, hide_coplanaredges=True)

viewer.run()
