from typing import Tuple
from typing import List
from typing import Dict
from typing import Optional

import sys
import gmsh

from compas.geometry import Polyhedron
from compas.datastructures import Mesh

from compas_gmsh.options import OptimizationAlgorithm
from compas_gmsh.options import MeshOptions

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
    options.mesh.algorithm : MeshAlgorithm, optional
        The meshing algorithm to use.
    options.mesh.lmin : float, optional
        The minimum characteristic edge length for meshing.
    options.mesh.lmax : float, optional
        The maximum characteristic edge length for meshing.
    options.mesh.mesh_only_empty : bool, optional
        Mesh only parts without existing mesh.
    options.mesh.meshsize_extend_from_boundary : bool, optional
        Compute mesh size from the boundary inwards.
    options.mesh.meshsize_min : float, optional
        Minimum size of mesh elements.

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
        Construct a model from  a Brep.
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

        Parameters
        ----------
        dim : int, optional
            The dimension of the mesh.

        Returns
        -------
        None
            The mesh is stored in the model for further refinement and optimisation.
            To retrieve the generated mesh, use :meth:`mesh_to_compas`, :meth:`mesh_to_openmesh`, or :meth:`mesh_to_tets`.

        Notes
        -----
        The geometry is automatically synchronised with the underlying OCC model.
        Therefore, there is no need to call :meth:`synchronize` before generating the mesh.
        To influence the meshing process, use the options of the model (:attr:`options.mesh`).

        """
        self.occ.synchronize()
        self.mesh.generate(dim)

    def refine_mesh(self) -> None:
        """
        Refine the model mesh by uniformly splitting the edges.

        Returns
        -------
        None
            Refinement is applied to the internally stored mesh.

        """
        self.mesh.refine()

    def optimize_mesh(
        self,
        algo: OptimizationAlgorithm = OptimizationAlgorithm.Default,
        niter: int = 1,
    ) -> None:
        """
        Optimize the model mesh using the specified method.

        Parameters
        ----------
        algo : OptimizationAlgorithm, optional
            The optimization algorithm to use.
        niter : int, optional
            The number of iterations.

        Returns
        -------
        None
            Optimisation is applied to the internally stored mesh.

        """
        self.mesh.optimize(algo.value, niter=niter)

    def recombine_mesh(self) -> None:
        """
        Recombine the mesh into quadrilateral faces.

        Returns
        -------
        None
            Recombination is applied to the internally stored mesh.

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

        Returns
        -------
        tuple[dict, list]
            A tuple containing the vertices and faces of the mesh.

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

        Returns
        -------
        :class:`Mesh`
            A COMPAS mesh.

        """
        vertices, faces = self.mesh_to_vertices_and_faces()
        return Mesh.from_vertices_and_faces(vertices, faces)

    def mesh_to_openmesh(self) -> None:  # type: ignore
        """
        Convert the model mesh to a COMPAS mesh data structure.

        Returns
        -------
        openmesh.TriMesh or openmesh.PolyMesh
            An OpenMesh mesh.

        """
        try:
            import openmesh  # type: ignore
        except ImportError:
            print("OpenMesh is not installed. Install using `pip install openmesh`.")
            raise

        vertices, faces = self.mesh_to_vertices_and_faces()

        if len(faces[0]) == 3:
            mesh = openmesh.TriMesh()
        elif len(faces[0]) == 4:
            mesh = openmesh.PolyMesh()

        vertex_index = {}
        for vertex in vertices:
            index = mesh.add_vertex(vertices[vertex])
            vertex_index[vertex] = index
        for face in faces:
            mesh.add_face(*[vertex_index[vertex] for vertex in face])

        return mesh

    def mesh_to_tets(self) -> List[Polyhedron]:
        """
        Convert the model mesh to a COMPAS mesh data structure.

        Returns
        -------
        list[:class:`Polyhedron`]
            A list of COMPAS polyhedra.

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
