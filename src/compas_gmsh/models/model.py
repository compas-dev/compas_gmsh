from __future__ import annotations

import sys
import gmsh

from compas.datastructures import Mesh


class Model:
    """Base model for mesh generation."""

    def __init__(self, name: str, verbose: bool = False, algo: int = 6) -> Model:
        gmsh.initialize(sys.argv)
        gmsh.option.setNumber("General.Terminal", int(verbose))
        gmsh.option.setNumber("Mesh.Algorithm", algo)
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

    def generate_mesh(self, dim: int = 2) -> None:
        """Generate a mesh of the current model."""
        self.factory.synchronize()
        self.mesh.generate(dim)

    def refine_mesh(self) -> None:
        """Refine the model mesh."""
        self.mesh.refine()

    def mesh_to_compas(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        nodes = self.mesh.getNodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order='C')
        # node_paramcoords = nodes[2]
        xyz = {}
        for tag, coords in zip(node_tags, node_coords):
            xyz[int(tag)] = coords.tolist()
        elements = self.mesh.getElements()
        triangles = []
        for etype, etags, ntags in zip(*elements):
            # if etype == 1:  # lines
            #     print(f'line: {len(etags)}')
            if etype == 2:  # triangles
                # print(f'triangle: {len(etags)}')
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    triangle = ntags[i * n: i * n + n]
                    triangles.append(triangle.tolist())
            # elif etype == 4:  # tets
            #     print(f'tetrahedron: {len(etags)}')
            # elif etype == 15:  # points
            #     print(f'point: {len(etags)}')

        return Mesh.from_vertices_and_faces(xyz, triangles)
