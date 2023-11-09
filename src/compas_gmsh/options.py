import gmsh
from enum import Enum


class MeshAlgorithm(Enum):
    MeshAdapt = 1
    Automatic = 2
    InitialMeshOnly = 3
    Delaunay = 5
    FrontalDelaunay = 6
    BAMG = 7
    FrontalDelaunayQuads = 8
    PackingParallelograms = 9

    @classmethod
    def __missing__(cls, value):
        return cls.MeshAdapt


class OptimizationAlgorithm(Enum):
    Default = ""
    Gmsh = "Gmsh"
    Netgen = "Netgen"
    HighOrder = "HighOrder"
    HighOrderElastic = "HighOrderElastic"
    HighOrderFastCurving = "HighOrderFastCurving"
    Laplace2D = "Laplace2D"
    Relocate2D = "Relocate2D"
    Relocate3D = "Relocate3D"

    @classmethod
    def __missing__(cls, value):
        return cls.Default


class RecombinationAlgorithm(Enum):
    Simple = 0
    Blossom = 1
    SimpleFullQuad = 2
    BlossomFullQuad = 3

    @classmethod
    def __missing__(cls, value):
        return cls.Blossom


class MeshSizeExtendFromBoundary(Enum):
    Never = 0
    SurfacesAndVolumes = 1
    SurfacesAndVolumesUseSmallestSurfaceElementEdgeLength = 2
    OnlySurfaces = -2
    OnlyVolumes = -3

    @classmethod
    def __missing__(cls, value):
        return cls.SurfacesAndVolumes


class MeshOptions:
    """Options for mesh generation in Gmsh.

    Attributes
    ----------
    algorithm : MeshAlgorithm
        The meshing algorithm to use.
    lmin : float
        The minimum characteristic edge length for meshing.
        Note that the actual minimum edge length may deviate from this value.
        The deviation is captured in an efficiency index, which tends to be around 0.8.
        Use :attr:`MeshAlgortihmFrontalDelaunay` for best results.
    lmax : float
        The maximum characteristic edge length for meshing.
        Note that the actual maximum edge length may deviate from this value.
        The deviation is captured in an efficiency index, which tends to be around 0.8.
        Use :attr:`MeshAlgortihmFrontalDelaunay` for best results.
    mesh_only_empty : bool
        Mesh only parts without existing mesh.
        Default is False.
    meshsize_extend_from_boundary : MeshSizeExtendFromBoundary
        Compute mesh size from the boundary inwards.
    meshsize_min : float
        Minimum size of mesh elements.
        Default is 0.
    meshsize_max : float
        Maximum size of mesh elements.
        Default is 1e+22.
    meshsize_from_curvature : bool
        Define mesh size based on curvature.
        Default is False.
    meshsize_from_points : bool
        Define mesh size based values assigned to points.
        Default is True.
    min_nodes_circle : float
        Minimum number of nodes for discretising a circle.
        Default is 7.
    min_nodes_curve : float
        Minimum number of nodes for discretising a curve.
        Default is 3.

    Notes
    -----
    There are three ways to specify the size of the mesh elements for a given geometry:

    1. First, if Mesh.CharacteristicLengthFromPoints is set (it is by default),
       you can simply specify desired mesh element sizes at the geometrical points of the model (with the Point command: see Points).
       The size of the mesh elements will then be computed by linearly interpolating these values on the initial mesh (see Mesh: finite element mesh generation).
       This might sometimes lead to over-refinement in some areas, so that you may have to add “dummy” geometrical entities in the model in order to get the desired element sizes.
       This method works with all the algorithms implemented in the mesh module.
       The final element sizes are of course constrained by the structured algorithms for which the element sizes are explicitly specified
       (e.g., transfinite and extruded grids: see Structured grids).
    2. Second, if Mesh.CharacteristicLengthFromCurvature is set (it is not by default), the mesh will be adapted with respect to the curvature of the geometrical entities.
    3. Finally, you can specify general mesh size "fields".

    Fields are supported by all the algorithms except those based on Netgen.
    The list of available fields with their options is given below.
    The three aforementioned methods can be used simultaneously, in which case the smallest element size is selected at any given point.
    All element sizes are further constrained by the Mesh.CharacteristicLengthMin, Mesh.CharacteristicLengthMax and Mesh.CharacteristicLengthFactor.

    """

    @property
    def algorithm(self) -> MeshAlgorithm:
        return MeshAlgorithm(gmsh.option.get_number("Mesh.Algorithm"))

    @algorithm.setter
    def algorithm(self, algo: MeshAlgorithm) -> None:
        gmsh.option.set_number("Mesh.Algorithm", algo.value)

    @property
    def lmin(self) -> float:
        gmsh.option.get_number("Mesh.CharacteristicLengthMin")

    @lmin.setter
    def lmin(self, value: float):
        gmsh.option.set_number("Mesh.CharacteristicLengthMin", value)

    @property
    def lmax(self) -> float:
        gmsh.option.get_number("Mesh.CharacteristicLengthMax")

    @lmax.setter
    def lmax(self, value: float):
        gmsh.option.set_number("Mesh.CharacteristicLengthMax", value)

    @property
    def mesh_only_empty(self) -> bool:
        return bool(gmsh.option.get_number("Mesh.MeshOnlyEmpty"))

    @mesh_only_empty.setter
    def mesh_only_empty(self, value: bool):
        gmsh.option.set_number("Mesh.MeshOnlyEmpty", int(value))

    @property
    def meshsize_extend_from_boundary(self) -> MeshSizeExtendFromBoundary:
        return MeshSizeExtendFromBoundary(
            gmsh.option.get_number("Mesh.MeshSizeExtendFromBoundary")
        )

    @meshsize_extend_from_boundary.setter
    def meshsize_extend_from_boundary(self, value: MeshSizeExtendFromBoundary):
        gmsh.option.set_number("Mesh.MeshSizeExtendFromBoundary", value.value)

    @property
    def meshsize_min(self) -> float:
        return gmsh.option.get_number("Mesh.MeshSizeMin")

    @meshsize_min.setter
    def meshsize_min(self, value: float):
        gmsh.option.set_number("Mesh.MeshSizeMin", value)

    @property
    def meshsize_max(self) -> float:
        return gmsh.option.get_number("Mesh.MeshSizeMax")

    @meshsize_max.setter
    def meshsize_max(self, value: float):
        gmsh.option.set_number("Mesh.MeshSizeMax", value)

    @property
    def meshsize_from_curvature(self) -> bool:
        return bool(gmsh.option.get_number("Mesh.MeshSizeFromCurvature"))

    @meshsize_from_curvature.setter
    def meshsize_from_curvature(self, value: bool):
        gmsh.option.set_number("Mesh.MeshSizeFromCurvature", int(value))

    @property
    def meshsize_from_points(self) -> bool:
        return bool(gmsh.option.get_number("Mesh.MeshSizeFromPoints"))

    @meshsize_from_points.setter
    def meshsize_from_points(self, value: bool):
        gmsh.option.set_number("Mesh.MeshSizeFromPoints", int(value))

    @property
    def min_nodes_circle(self) -> float:
        return int(gmsh.option.get_number("Mesh.MinimumCircleNodes"))

    @min_nodes_circle.setter
    def min_nodes_circle(self, value: float):
        gmsh.option.set_number("Mesh.MinimumCircleNodes", value)

    @property
    def min_nodes_curve(self) -> float:
        return int(gmsh.option.get_number("Mesh.MinimumCurveNodes"))

    @min_nodes_curve.setter
    def min_nodes_curve(self, value: float):
        gmsh.option.set_number("Mesh.MinimumCurveNodes", value)
