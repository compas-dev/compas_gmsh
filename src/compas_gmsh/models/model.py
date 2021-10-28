from typing import List, Optional

import sys
import gmsh

from compas.geometry import Polyhedron
from compas.datastructures import Mesh

from compas_gmsh.options import MeshAlgorithm
from compas_gmsh.options import OptimizationAlgorithm


class Model:
    """Base model for mesh generation."""

    def __init__(self,
                 name: Optional[str] = None,
                 verbose: bool = False,
                 mesh_algorithm: MeshAlgorithm = MeshAlgorithm.FrontalDelaunay) -> None:
        gmsh.initialize(sys.argv)
        gmsh.model.add(name or f'{self.__class__.__name__}')
        self._verbose = False
        self._mesh_algorithm = None
        self.verbose = verbose
        self.mesh_algorithm = mesh_algorithm
        self.mesh = gmsh.model.mesh
        self.factory = gmsh.model.occ

    def __del__(self):
        gmsh.finalize()

    @property
    def lmin(self) -> float:
        """Minimum edge length for meshing."""
        gmsh.option.getNumber("Mesh.CharacteristicLengthMin")

    @lmin.setter
    def lmin(self, value: float):
        gmsh.option.setNumber("Mesh.CharacteristicLengthMin", value)

    @property
    def lmax(self) -> float:
        """Maximum edge length for meshing."""
        gmsh.option.getNumber("Mesh.CharacteristicLengthMax")

    @lmax.setter
    def lmax(self, value: float):
        gmsh.option.setNumber("Mesh.CharacteristicLengthMax", value)

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._verbose = bool(value)
        gmsh.option.setNumber("General.Terminal", int(value))

    @property
    def mesh_algorithm(self) -> MeshAlgorithm:
        return self._mesh_algorithm

    @mesh_algorithm.setter
    def mesh_algorithm(self, algo: MeshAlgorithm) -> None:
        self._mesh_algorithm = algo.value
        gmsh.option.setNumber("Mesh.Algorithm", algo.value)

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
                      algorithm: MeshAlgorithm = MeshAlgorithm.FrontalDelaunay) -> None:
        """Generate a mesh of the current model."""
        self.verbose = verbose
        self.mesh_algorithm = algorithm
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
            xyz[int(tag)] = coords
        elements = self.mesh.getElements()
        faces = []
        for etype, etags, ntags in zip(*elements):
            if etype == 2:
                # triangle
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    a, b, c = ntags[i * n: i * n + n]
                    faces.append([a, b, c])
            elif etype == 3:
                # quad
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    a, b, c, d = ntags[i * n: i * n + n]
                    faces.append([a, b, c, d])

        return Mesh.from_vertices_and_faces(xyz, faces)

    def mesh_to_openmesh(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        try:
            import openmesh as om
        except ImportError:
            print('OpenMesh is not installed. Install using `pip install openmesh`.')
            raise
        om.TriMesh()

    def mesh_to_volmesh(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        pass

    def mesh_to_tets(self) -> List[Polyhedron]:
        """Convert the model mesh to a COMPAS mesh data structure."""
        nodes = self.mesh.getNodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order='C')
        xyz = {}
        for tag, coords in zip(node_tags, node_coords):
            xyz[int(tag)] = coords
        elements = self.mesh.getElements()
        tets = []
        for etype, etags, ntags in zip(*elements):
            if etype == 4:
                # tetrahedron
                for i, etag in enumerate(etags):
                    n = self.mesh.getElementProperties(etype)[3]
                    vertices = [xyz[index] for index in ntags[i * n: i * n + n]]
                    faces = [
                        [0, 1, 2],
                        [0, 2, 3],
                        [1, 3, 2],
                        [0, 3, 1]]
                    tets.append(Polyhedron(vertices, faces))
        return tets
