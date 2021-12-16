"""
********************************************************************************
compas_gmsh.interop
********************************************************************************

.. currentmodule:: compas_gmsh.interop


Enumerations
============

.. autosummary::
    :toctree: generated/
    :nosignatures:

    MeshAlgorithm
    OptimizationAlgorithm

"""
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
    Default = ""
    Gmsh = "Gmsh"
    Netgen = "Netgen"
    HighOrder = "HighOrder"
    HighOrderElastic = "HighOrderElastic"
    HighOrderFastCurving = "HighOrderFastCurving"
    Laplace2D = "Laplace2D"
    Relocate2D = "Relocate2D"
    Relocate3D = "Relocate3D"


class RecombinationAlgorithm(Enum):
    Simple = 0
    Blossom = 1
    SimpleFullQuad = 2
    BlossomFullQuad = 3
