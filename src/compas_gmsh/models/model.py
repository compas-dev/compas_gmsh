from typing import Tuple
from typing import List
from typing import Dict
from typing import Optional

import sys
import gmsh

from compas.geometry import Polyhedron
from compas.datastructures import Mesh

from compas_gmsh.options import MeshAlgorithm
from compas_gmsh.options import OptimizationAlgorithm

# from compas_gmsh.options import RecombinationAlgorithm


class Model:
    """
    Base model for mesh generation.

    Parameters
    ----------
    name : str, optional
        The name of the model.
    verbose, bool, optional
        Flag indicating if output should be printed to the terminal.

    """

    # gmsh.option.set_number('Mesh.MeshSizeFromCurvatureIsotropic', 0)
    # gmsh.option.set_number('Mesh.OptimizeNetgen', 0)
    # gmsh.option.set_number('Mesh.QuadsRemeshingBoldness', 0.66)
    # gmsh.option.set_number('Mesh.RecombineOptimizeTopology', 5)
    # gmsh.option.set_number('Mesh.RefineSteps', 10)
    # gmsh.option.set_number('Mesh.Smoothing', 1)
    # gmsh.option.set_number('Mesh.SmoothNormals', 0)
    # gmsh.option.set_number('Mesh.SmoothRatio', 1.8)
    # gmsh.option.set_number('Mesh.SubdivisionAlgorithm', 0)
    # gmsh.option.set_number('Mesh.ToleranceEdgeLength', 0)
    # gmsh.option.set_number('Mesh.ToleranceInitialDelaunay', 1e-12)

    class options:
        class MeshOptions:
            @property
            def algorithm(self) -> MeshAlgorithm:
                return gmsh.option.get_number("Mesh.Algorithm")

            @algorithm.setter
            def algorithm(self, algo: MeshAlgorithm) -> None:
                gmsh.option.set_number("Mesh.Algorithm", algo.value)

            @property
            def lmin(self) -> float:
                """Minimum characteristic edge length for meshing."""
                gmsh.option.get_number("Mesh.CharacteristicLengthMin")

            @lmin.setter
            def lmin(self, value: float):
                gmsh.option.set_number("Mesh.CharacteristicLengthMin", value)

            @property
            def lmax(self) -> float:
                """Maximum characteristic edge length for meshing."""
                gmsh.option.get_number("Mesh.CharacteristicLengthMax")

            @lmax.setter
            def lmax(self, value: float):
                gmsh.option.set_number("Mesh.CharacteristicLengthMax", value)

            @property
            def mesh_only_empty(self) -> bool:
                """Mesh only parts without existing mesh."""
                return bool(gmsh.option.get_number("Mesh.MeshOnlyEmpty"))

            @mesh_only_empty.setter
            def mesh_only_empty(self, value: bool):
                gmsh.option.set_number("Mesh.MeshOnlyEmpty", int(value))

            @property
            def meshsize_extend_from_boundary(self) -> bool:
                """Compute mesh size from the boundary inwards."""
                return bool(gmsh.option.get_number("Mesh.MeshSizeExtendFromBoundary"))

            @meshsize_extend_from_boundary.setter
            def meshsize_extend_from_boundary(self, value: bool):
                gmsh.option.set_number("Mesh.MeshSizeExtendFromBoundary", int(value))

            @property
            def meshsize_min(self) -> float:
                """Minimum size of mesh elements."""
                return gmsh.option.get_number("Mesh.MeshSizeMin")

            @meshsize_min.setter
            def meshsize_min(self, value: float):
                gmsh.option.set_number("Mesh.MeshSizeMin", value)

            @property
            def meshsize_max(self) -> float:
                """Maximum size of mesh elements."""
                return gmsh.option.get_number("Mesh.MeshSizeMax")

            @meshsize_max.setter
            def meshsize_max(self, value: float):
                gmsh.option.set_number("Mesh.MeshSizeMax", value)

            # combine in to MeshSizeMethod?

            @property
            def meshsize_from_curvature(self) -> bool:
                """Define mesh size based on curvature."""
                return bool(gmsh.option.get_number("Mesh.MeshSizeFromCurvature"))

            @meshsize_from_curvature.setter
            def meshsize_from_curvature(self, value: bool):
                gmsh.option.set_number("Mesh.MeshSizeFromCurvature", int(value))

            @property
            def meshsize_from_points(self) -> bool:
                """Define mesh size based values assigned to points."""
                return bool(gmsh.option.get_number("Mesh.MeshSizeFromPoints"))

            @meshsize_from_points.setter
            def meshsize_from_points(self, value: bool):
                gmsh.option.set_number("Mesh.MeshSizeFromPoints", int(value))

            @property
            def min_nodes_circle(self) -> float:
                """Minimum number of nodes for discretising a circle."""
                return int(gmsh.option.get_number("Mesh.MinimumCircleNodes"))

            @min_nodes_circle.setter
            def min_nodes_circle(self, value: float):
                gmsh.option.set_number("Mesh.MinimumCircleNodes", value)

            @property
            def min_nodes_curve(self) -> float:
                """Minimum number of nodes for discretising a curve."""
                return int(gmsh.option.get_number("Mesh.MinimumCurveNodes"))

            @min_nodes_curve.setter
            def min_nodes_curve(self, value: float):
                gmsh.option.set_number("Mesh.MinimumCurveNodes", value)

        mesh = MeshOptions()

    def __init__(self, name: Optional[str] = None, verbose: bool = False) -> None:
        gmsh.initialize(sys.argv)
        gmsh.model.add(name or f"{self.__class__.__name__}")
        self._verbose = False
        self.verbose = verbose
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
    # Constructors
    # ==============================================================================

    @classmethod
    def from_step(cls, filename: str) -> "Model":
        """
        Construc a model from the data contained in a STEP file.
        """
        model = cls()
        gmsh.open(filename)
        return model

    @classmethod
    def from_brep(cls, brep) -> "Model":
        """
        Construct a model from  a BRep.
        """
        pass

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

    def generate_mesh(self, dim: int = 2) -> None:
        """
        Generate a mesh of the current model.
        """
        self.occ.synchronize()
        self.mesh.generate(dim)

    def refine_mesh(self) -> None:
        """
        Refine the model mesh by uniformly splitting the edges.
        """
        self.mesh.refine()

    def optimize_mesh(
        self,
        algo: OptimizationAlgorithm = OptimizationAlgorithm.Default,
        niter: int = 1,
    ) -> None:
        """
        Optimize the model mesh using the specified method.
        """
        self.mesh.optimize(algo.value, niter=niter)

    def recombine_mesh(self) -> None:
        """
        Recombine the mesh into quadrilateral faces.
        """
        self.mesh.recombine()

    # ==============================================================================
    # Export
    # ==============================================================================

    def mesh_to_vertices_and_faces(
        self,
    ) -> Tuple[Dict[int, List[float]], List[List[int]]]:
        """
        Convert the model mesh to a COMPAS mesh data structure.
        """
        nodes = self.mesh.get_nodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order="C")
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
                    a, b, c = ntags[i * n : i * n + n]
                    faces.append([a, b, c])
            elif etype == 3:
                # quad
                for i, etag in enumerate(etags):
                    n = self.mesh.get_element_properties(etype)[3]
                    a, b, c, d = ntags[i * n : i * n + n]
                    faces.append([a, b, c, d])

        return vertices, faces

    def mesh_to_compas(self) -> Mesh:
        """
        Convert the model mesh to a COMPAS mesh data structure.
        """
        vertices, faces = self.mesh_to_vertices_and_faces()
        return Mesh.from_vertices_and_faces(vertices, faces)

    def mesh_to_openmesh(self) -> Mesh:
        """
        Convert the model mesh to a COMPAS mesh data structure.
        """
        try:
            import openmesh as om  # noqa: F401
        except ImportError:
            print("OpenMesh is not installed. Install using `pip install openmesh`.")
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
            mesh.add_face(*[vertex_index[vertex] for vertex in face])
        return mesh

    def mesh_to_volmesh(self) -> Mesh:
        """
        Convert the model mesh to a COMPAS mesh data structure.
        """
        pass

    def mesh_to_tets(self) -> List[Polyhedron]:
        """
        Convert the model mesh to a COMPAS mesh data structure.
        """
        nodes = self.mesh.get_nodes()
        node_tags = nodes[0]
        node_coords = nodes[1].reshape((-1, 3), order="C")
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
                    vertices = [xyz[index] for index in ntags[i * n : i * n + n]]
                    faces = [[0, 1, 2], [0, 2, 3], [1, 3, 2], [0, 3, 1]]
                    tets.append(Polyhedron(vertices, faces))
        return tets
