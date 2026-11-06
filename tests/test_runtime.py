from pathlib import Path

import gmsh
import numpy as np
from compas.geometry import Box
from compas.geometry import Frame
from compas_gmsh.models import Model
from compas_gmsh.models import ShapeModel


FIXTURES = Path(__file__).parent / "fixtures"


def add_unit_square(model: Model) -> None:
    """Add a unit square surface to a model."""
    points = [
        model.occ.add_point(0.0, 0.0, 0.0),
        model.occ.add_point(1.0, 0.0, 0.0),
        model.occ.add_point(1.0, 1.0, 0.0),
        model.occ.add_point(0.0, 1.0, 0.0),
    ]
    curves = [model.occ.add_line(points[index], points[(index + 1) % 4]) for index in range(4)]
    loop = model.occ.add_curve_loop(curves)
    model.occ.add_plane_surface([loop])


def test_model_initializes_and_finalizes_repeatedly() -> None:
    for index in range(3):
        model = Model(name=f"lifecycle-{index}")
        assert gmsh.is_initialized()
        assert gmsh.model.get_current() == f"lifecycle-{index}"
        model.destroy()
        model.destroy()
        assert not gmsh.is_initialized()


def test_planar_mesh_converts_to_compas_mesh() -> None:
    model = Model(name="planar")
    try:
        add_unit_square(model)
        model.generate_mesh(2)
        mesh = model.mesh_to_compas()

        assert mesh.number_of_vertices() > 0
        assert mesh.number_of_faces() > 0
        vertices, faces = mesh.to_vertices_and_faces()
        assert all(0 <= index < len(vertices) for face in faces for index in face)
    finally:
        model.destroy()


def test_occ_solid_generates_tetrahedra() -> None:
    model = Model(name="solid")
    try:
        model.occ.add_box(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
        model.generate_mesh(3)
        tetrahedra = model.mesh_to_tets()

        assert tetrahedra
        assert all(len(tetrahedron.vertices) == 4 for tetrahedron in tetrahedra)
    finally:
        model.destroy()


def test_boolean_operation_returns_volume_entities() -> None:
    model = ShapeModel(name="boolean")
    try:
        first = model.add_box(Box(1.0))
        second = model.add_box(Box(1.0, frame=Frame([0.5, 0.0, 0.0])))

        result = model.boolean_intersection([first], [second])
        model.synchronize()

        assert result
        assert all(dimension == 3 for dimension, _ in result)
        assert model.volumes
    finally:
        model.destroy()


def test_from_step_opens_committed_read_only_fixture() -> None:
    fixture = FIXTURES / "line.step"
    before = fixture.read_bytes()

    model = Model.from_step(fixture)
    try:
        assert model.curves
    finally:
        model.destroy()

    assert fixture.read_bytes() == before


def test_mesh_arrays_have_consistent_shapes() -> None:
    model = Model(name="arrays")
    try:
        add_unit_square(model)
        model.generate_mesh(2)
        vertices, faces = model.mesh_to_vertices_and_faces()

        assert vertices
        assert faces
        assert all(np.asarray(point).shape == (3,) for point in vertices.values())
        assert all(np.asarray(face).ndim == 1 for face in faces)
    finally:
        model.destroy()


def test_point_lookup_accepts_numpy_coordinates() -> None:
    model = Model(name="numpy-point")
    try:
        point = model.occ.add_point(1.0, 2.0, 3.0)
        model.synchronize()

        assert model.find_points_at_xyz(np.array([1.0, 2.0, 3.0])) == [point]
        assert model.find_points_at_xy(np.array([1.0, 2.0, 99.0])) == [point]
    finally:
        model.destroy()
