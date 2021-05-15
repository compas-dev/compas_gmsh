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


class OptimizationAlgorithm(Enum):
    Gmsh = "Gmsh"
    Netgen = "Netgen"
    HighOrder = "HighOrder"
    HighOrderElastic = "HighOrderElastic"
    HighOrderFastCurving = "HighOrderFastCurving"
    Laplace2D = "Laplace2D"
    Relocate2D = "Relocate2D"
    Relocate3D = "Relocate3D"
