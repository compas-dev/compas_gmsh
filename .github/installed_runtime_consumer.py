"""Headless smoke test for the exact installed wheel."""

from compas_gmsh.models import Model

model = Model(name="installed-wheel")
try:
    points = [
        model.occ.add_point(0.0, 0.0, 0.0),
        model.occ.add_point(1.0, 0.0, 0.0),
        model.occ.add_point(1.0, 1.0, 0.0),
        model.occ.add_point(0.0, 1.0, 0.0),
    ]
    curves = [model.occ.add_line(points[index], points[(index + 1) % 4]) for index in range(4)]
    loop = model.occ.add_curve_loop(curves)
    model.occ.add_plane_surface([loop])
    model.generate_mesh(2)
    mesh = model.mesh_to_compas()
    assert mesh.number_of_vertices() > 0
    assert mesh.number_of_faces() > 0
finally:
    model.destroy()
