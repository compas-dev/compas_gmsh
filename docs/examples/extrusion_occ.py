# type: ignore

from compas.brep import Brep
from compas.geometry import Circle
from compas.geometry import Frame
from compas.geometry import Plane
from compas_gmsh.models import Model
from compas_occ.brep import OCCBrepEdge
from compas_occ.brep import OCCBrepFace
from compas_occ.brep import OCCBrepLoop
from compas_view2.app import App

circle1 = Circle(1.0, frame=Frame([2, 2, 0]))
circle2 = Circle(2.0, frame=Frame([-2, -2, 0]))
circle3 = Circle(0.5, frame=Frame([2, -2, 0]))

loop1 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle1)])
loop2 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle2)])
loop3 = OCCBrepLoop.from_edges([OCCBrepEdge.from_circle(circle3)])

face = OCCBrepFace.from_plane(Plane.worldXY(), domain_u=(-5, 5), domain_v=(-5, 5))
face.add_loops([loop1, loop2, loop3], reverse=True)

brep = Brep.from_extrusion(face, [0, 0, 0.3])
brep.heal()
brep.make_solid()
brep.to_step("brep_with_holes.step")

model = Model.from_step("brep_with_holes.step")
model.options.mesh.lmin = 0.001
model.options.mesh.lmax = 0.3

for point in model.find_points_at_xyz([-5, -5, 0.3]):
    model.mesh_targetlength_at_point(point, 0.01)

# for point in model.find_points_at_xyz([+5, -5, 0.3]):
#     model.mesh_targetlength_at_point(point, 0.01)

p1 = model.occ.add_point(-3, +3, 0.3, 0.1)
p2 = model.occ.add_point(+1, -1, 0.3, 0.1)
e1 = model.occ.add_line(p1, p2)

model.synchronize()

model.mesh.embed(1, [e1], 2, 9)

model.generate_mesh(3)
mesh = model.mesh_to_compas()

# =============================================================================
# Visualization
# =============================================================================

viewer = App(width=1600, height=900)
viewer.view.camera.position = [0, -12, 10]
viewer.view.camera.look_at([0, 2, 0])

# viewer.add(brep, linewidth=2, opacity=0.5)

# for surface in model.surfaces:
#     viewer.add(model.surface_mesh(surface))

for curve in model.curves:
    viewer.add(model.curve_to_polyline(curve), linewidth=2)

for point in model.points:
    viewer.add(model.point_to_point(point), pointsize=10)

viewer.add(mesh, opacity=0.7)
viewer.show()
