from typing import Tuple, List, Dict, Optional

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
                 mesh_algorithm: MeshAlgorithm = MeshAlgorithm.Automatic) -> None:
        gmsh.initialize(sys.argv)
        gmsh.model.add(name or f'{self.__class__.__name__}')
        self._verbose = False
        self._mesh_algorithm = None
        self.verbose = verbose
        self.mesh_algorithm = mesh_algorithm
        self.model = gmsh.model
        self.mesh = gmsh.model.mesh
        self.occ = gmsh.model.occ

    def __del__(self):
        gmsh.finalize()

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._verbose = bool(value)
        gmsh.option.set_number("General.Terminal", int(value))

    # ==============================================================================
    # Model
    # ==============================================================================

    @property
    def points(self):
        return self.model.get_entities(0)

    @property
    def lines(self):
        return self.model.get_entities(1)

    @property
    def surfaces(self):
        return self.model.get_entities(2)

    @property
    def volumes(self):
        return self.model.get_entities(3)

    def synchronize(self):
        self.occ.synchronize()

    # ==============================================================================
    # Meshing
    # ==============================================================================

    @property
    def mesh_lmin(self) -> float:
        """Minimum edge length for meshing."""
        gmsh.option.get_number("Mesh.CharacteristicLengthMin")

    @mesh_lmin.setter
    def mesh_lmin(self, value: float):
        gmsh.option.set_number("Mesh.CharacteristicLengthMin", value)

    @property
    def mesh_lmax(self) -> float:
        """Maximum edge length for meshing."""
        gmsh.option.get_number("Mesh.CharacteristicLengthMax")

    @mesh_lmax.setter
    def mesh_lmax(self, value: float):
        gmsh.option.set_number("Mesh.CharacteristicLengthMax", value)

    @property
    def mesh_algorithm(self) -> MeshAlgorithm:
        return self._mesh_algorithm

    @mesh_algorithm.setter
    def mesh_algorithm(self, algo: MeshAlgorithm) -> None:
        self._mesh_algorithm = algo.value
        gmsh.option.set_number("Mesh.Algorithm", algo.value)

    def generate_mesh(self, dim: int = 2) -> None:
        """Generate a mesh of the current model."""
        self.occ.synchronize()
        self.mesh.generate(dim)

    def refine_mesh(self) -> None:
        """Refine the model mesh by uniformly splitting the edges."""
        self.mesh.refine()

    def optimize_mesh(self,
                      algo: OptimizationAlgorithm = OptimizationAlgorithm.Default,
                      niter: int = 1) -> None:
        """Optimize the model mesh using the specified method."""
        self.mesh.optimize(algo.value, niter=niter)

    def recombine_mesh(self) -> None:
        """Recombine the mesh into quadrilateral faces."""
        self.mesh.recombine()

    # ==============================================================================
    # Export
    # ==============================================================================

    def mesh_to_vertices_and_faces(self) -> Tuple[Dict[int, List[float]], List[List[int]]]:
        """Convert the model mesh to a COMPAS mesh data structure."""
        nodes = self.mesh.get_nodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order='C')
        vertices = {}
        for tag, coords in zip(node_tags, node_coords):
            vertices[int(tag)] = coords

        elements = self.mesh.get_elements()
        faces = []
        for etype, etags, ntags in zip(*elements):
            if etype == 2:
                # triangle
                for i, etag in enumerate(etags):
                    n = self.mesh.get_element_properties(etype)[3]
                    a, b, c = ntags[i * n: i * n + n]
                    faces.append([a, b, c])
            elif etype == 3:
                # quad
                for i, etag in enumerate(etags):
                    n = self.mesh.get_element_properties(etype)[3]
                    a, b, c, d = ntags[i * n: i * n + n]
                    faces.append([a, b, c, d])

        return vertices, faces

    def mesh_to_compas(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        vertices, faces = self.mesh_to_vertices_and_faces()
        return Mesh.from_vertices_and_faces(vertices, faces)

    def mesh_to_openmesh(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        try:
            import openmesh as om  # noqa: F401
        except ImportError:
            print('OpenMesh is not installed. Install using `pip install openmesh`.')
            raise
        vertices, faces = self.mesh_to_vertices_and_faces()
        if len(faces[0]) == 3:
            mesh = om.TriMesh()
        elif len(faces[0]) == 4:
            mesh = om.PolyMesh()
        vertex_index = {}
        for vertex in vertices:
            index = mesh.add_vertex(vertices[vertex])
            vertex_index[vertex] = index
        for face in faces:
            mesh.add_face(* [vertex_index[vertex] for vertex in face])
        return mesh

    def mesh_to_volmesh(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure."""
        pass

    def mesh_to_tets(self) -> List[Polyhedron]:
        """Convert the model mesh to a COMPAS mesh data structure."""
        nodes = self.mesh.get_nodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order='C')
        xyz = {}
        for tag, coords in zip(node_tags, node_coords):
            xyz[int(tag)] = coords
        elements = self.mesh.get_elements()
        tets = []
        for etype, etags, ntags in zip(*elements):
            if etype == 4:
                # tetrahedron
                for i, etag in enumerate(etags):
                    n = self.mesh.get_element_properties(etype)[3]
                    vertices = [xyz[index] for index in ntags[i * n: i * n + n]]
                    faces = [
                        [0, 1, 2],
                        [0, 2, 3],
                        [1, 3, 2],
                        [0, 3, 1]]
                    tets.append(Polyhedron(vertices, faces))
        return tets
