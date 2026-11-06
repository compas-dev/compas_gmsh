from compas_gmsh.models import Model
from compas_gmsh.options import MeshAlgorithm
from compas_gmsh.options import MeshSizeExtendFromBoundary


def test_public_mesh_options_round_trip() -> None:
    model = Model(name="options")
    try:
        options = model.options.mesh

        options.algorithm = MeshAlgorithm.Delaunay
        options.lmin = 0.1
        options.lmax = 1.5
        assert options.lmin == 0.1
        assert options.lmax == 1.5

        options.mesh_only_empty = True
        options.meshsize_extend_from_boundary = MeshSizeExtendFromBoundary.OnlySurfaces
        options.meshsize_min = 0.2
        options.meshsize_max = 2.5
        options.meshsize_from_curvature = True
        options.meshsize_from_points = False
        options.min_nodes_circle = 11
        options.min_nodes_curve = 5

        assert options.algorithm is MeshAlgorithm.Delaunay
        assert options.mesh_only_empty is True
        assert options.meshsize_extend_from_boundary is MeshSizeExtendFromBoundary.OnlySurfaces
        assert options.meshsize_min == 0.2
        assert options.meshsize_max == 2.5
        assert options.meshsize_from_curvature is True
        assert options.meshsize_from_points is False
        assert options.min_nodes_circle == 11
        assert options.min_nodes_curve == 5
    finally:
        model.destroy()
