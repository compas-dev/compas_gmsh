from __future__ import annotations

from typing import Optional

import sys
import gmsh

from compas.datastructures import Mesh

from compas_gmsh.options import MeshAlgorithm
from compas_gmsh.options import OptimizationAlgorithm


class Model:
    """Base model for mesh generation."""

    def __init__(self,
                 name: str,
                 verbose: bool = False,
                 algo: MeshAlgorithm = MeshAlgorithm.FrontalDelaunay) -> Model:
        gmsh.initialize(sys.argv)
        gmsh.option.setNumber("General.Terminal", int(verbose))
        gmsh.option.setNumber("Mesh.Algorithm", algo.value)
        gmsh.model.add(name)
        self.mesh = gmsh.model.mesh
        self.factory = gmsh.model.occ

    def __del__(self):
        gmsh.finalize()

    @property
    def length_min(self) -> float:
        """Minimum edge length for meshing."""
        gmsh.option.getNumber("Mesh.CharacteristicLengthMin")

    @length_min.setter
    def length_min(self, value: float):
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", value)

    @property
    def length_max(self) -> float:
        """Maximum edge length for meshing."""
        gmsh.option.getNumber("Mesh.CharacteristicLengthMax")

    @length_max.setter
    def length_max(self, value: float):
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", value)

    def info(self) -> None:
        """Print information about the current model."""
        types = self.mesh.getElementTypes()
        for number in types:
            props = self.mesh.getElementProperties(number)
            name = props[0]
            dim = props[1]
            order = props[2]
            number_of_nodes = props[3]
            local_node_coords = props[4]
            number_of_primary_nodes = props[5]
            print(name)
            print('--', number)
            print('--', dim)
            print('--', order)
            print('--', number_of_nodes)
            print('--', local_node_coords)
            print('--', number_of_primary_nodes)

    def generate_mesh(self,
                      dim: int = 2,
                      verbose: bool = False,
                      algo: MeshAlgorithm = MeshAlgorithm.FrontalDelaunay) -> None:
        """Generate a mesh of the current model."""
        gmsh.option.setNumber("General.Terminal", int(verbose))
        gmsh.option.setNumber("Mesh.Algorithm", algo.value)
        self.factory.synchronize()
        self.mesh.generate(dim)

    def refine_mesh(self) -> None:
        """Refine the model mesh by uniformly splitting the edges."""
        self.mesh.refine()

    def optimize_mesh(self,
                      algo: Optional[OptimizationAlgorithm] = None,
                      niter: int = 1) -> None:
        """Optimize the model mesh using the specified method."""
        if algo:
            algo = algo.value
        else:
            algo = ""
        self.mesh.optimize(algo, niter=niter)

    def recombine_mesh(self) -> None:
        """Recombine the mesh into quadrilateral faces."""
        self.mesh.recombine()

    def mesh_to_compas(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        nodes = self.mesh.getNodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order='C')
        xyz = {}
        for tag, coords in zip(node_tags, node_coords):
            xyz[int(tag)] = coords.tolist()
        elements = self.mesh.getElements()
        faces = []
        for etype, etags, ntags in zip(*elements):
            if etype == 2:
                # triangles
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    triangle = ntags[i * n: i * n + n]
                    faces.append(triangle.tolist())
            elif etype == 3:
                # quads
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    quad = ntags[i * n: i * n + n]
                    faces.append(quad.tolist())

        return Mesh.from_vertices_and_faces(xyz, faces)
