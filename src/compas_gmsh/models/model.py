import enum
import os
import tempfile
from typing import Self
from typing import cast

import gmsh
import numpy as np
import numpy.typing as npt

from compas.datastructures import Mesh
from compas.geometry import Brep
from compas.geometry import Point
from compas.geometry import Polyhedron
from compas.geometry import Polyline
from compas.geometry import Transformation
from compas.geometry import distance_point_point_sqrd_xy
from compas.geometry import transform_points_numpy
from compas.itertools import linspace
from compas.tolerance import TOL
from compas.typing import PointLike
from compas_gmsh.options import MeshOptions
from compas_gmsh.options import OptimizationAlgorithm

FloatArray = npt.NDArray[np.float64]
IntArray = npt.NDArray[np.uint64]


class MeshElementType(enum.Enum):
    """Gmsh element type identifiers used by the wrapper."""

    Point = 15
    Line = 1
    Triangle = 2
    Quadrangle = 3
    Tetrahedron = 4
    Hexahedron = 5
    Prism = 6
    Pyramid = 7


class Model:
    """Base model for mesh generation.

    Parameters
    ----------
    name
        The name of the model.
    verbose
        Flag indicating if output should be printed to the terminal.

    Attributes
    ----------
    options
        Namespace containing the meshing options.

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
        """Namespace for Gmsh's process-global meshing options."""

        mesh: MeshOptions = MeshOptions()

    def __init__(self, name: str | None = None, verbose: bool = False) -> None:
        gmsh.initialize()
        try:
            gmsh.model.add(name or f"{self.__class__.__name__}")
        except Exception:
            gmsh.finalize()
            raise
        self._verbose = False
        self.verbose = verbose
        self.model: type[gmsh.model] = gmsh.model
        self.mesh: type[gmsh.model.mesh] = gmsh.model.mesh
        self.occ: type[gmsh.model.occ] = gmsh.model.occ

    def destroy(self) -> None:
        """Finalize Gmsh's process-global runtime.

        Calling this method more than once is safe. Finalization invalidates all
        active models in the current Python process.

        """
        if gmsh.is_initialized():
            gmsh.finalize()

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool) -> None:
        self._verbose = bool(value)
        gmsh.option.set_number("General.Terminal", int(value))

    def synchronize(self) -> None:
        """Synchronize the geometry with the underlying OCC model."""
        self.occ.synchronize()

    def heal(self) -> None:
        """Heal the underlying OCC model."""
        self.occ.heal_shapes()

    # ==============================================================================
    # Constructors
    # ==============================================================================

    @classmethod
    def from_step(cls, filepath: str | os.PathLike[str]) -> Self:
        """Construct a model from the data contained in a STEP file.

        Parameters
        ----------
        filepath
            The path to the step file.

        Returns
        -------
        Model

        """
        model = cls()
        try:
            gmsh.open(os.fspath(filepath))
        except Exception:
            model.destroy()
            raise
        return model

    @classmethod
    def from_brep(cls, brep: Brep) -> Self:
        """Construct a model from a b-rep geometry.

        Parameters
        ----------
        brep
            The b-rep geometry.

        Returns
        -------
        Model

        """
        with tempfile.TemporaryDirectory(prefix="compas-gmsh-") as tempdir:
            filepath = os.path.join(tempdir, "geometry.step")
            brep.to_step(filepath)
            return cls.from_step(filepath)

    # ==============================================================================
    # Model entities
    # ==============================================================================

    @property
    def points(self) -> list[int]:
        return [dimtag[1] for dimtag in self.model.get_entities(0)]

    @property
    def curves(self) -> list[int]:
        return [dimtag[1] for dimtag in self.model.get_entities(1)]

    @property
    def surfaces(self) -> list[int]:
        return [dimtag[1] for dimtag in self.model.get_entities(2)]

    @property
    def volumes(self) -> list[int]:
        return [dimtag[1] for dimtag in self.model.get_entities(3)]

    # =============================================================================
    # Model boundaries
    # =============================================================================

    def surface_curves(self, tag: int) -> list[int]:
        """Get the boundary curves of a surface in the model.

        Parameters
        ----------
        tag
            The identifier of the surface.

        Returns
        -------
        list[int]
            The identifiers of the curves of the surface.

        """
        return [dimtag[1] for dimtag in self.model.get_boundary([(2, tag)])]

    def volume_surfaces(self, tag: int) -> list[int]:
        """Get the surfaces of a volume in the model.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        list[int]
            The identifiers of the surfaces of the volume.

        """
        return [dimtag[1] for dimtag in self.model.get_boundary([(3, tag)])]

    def volume_curves(self, tag: int) -> list[int]:
        """Get the curves of a volume in the model.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        list[int]
            The identifiers of the curves of the volume.

        """
        surfaces = self.volume_surfaces(tag)
        curves = []
        for surface in surfaces:
            temp = self.surface_curves(surface)
            curves += [tag for tag in temp if tag > 0]
        return curves

    def volume_points(self, tag: int) -> list[int]:
        """Get the points of a volume in the model.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        list[int]
            The identifiers of the points of the volume.

        """
        dimtags = self.model.get_boundary([(3, tag)], recursive=True)
        return [dimtag[1] for dimtag in dimtags if dimtag[0] == 0]

    # =============================================================================
    # Model geometry representations
    # =============================================================================

    def curve_domain(self, tag: int) -> tuple[float, float]:
        """Get the domain of a curve in the model.

        Parameters
        ----------
        tag
            The identifier of the curve.

        Returns
        -------
        tuple[float, float]
            The domain of the curve.

        """
        u, v = self.model.get_parametrization_bounds(1, tag)
        return u[0], v[0]

    def surface_domain(self, tag: int) -> tuple[tuple[float, float], tuple[float, float]]:
        """Get the domain of a surface in the model.

        Parameters
        ----------
        tag
            The identifier of the surface.

        Returns
        -------
        tuple[tuple[float, float], tuple[float, float]]
            The domain of the surface.

        """
        dmin, dmax = self.model.get_parametrization_bounds(2, tag)
        umin, vmin = dmin
        umax, vmax = dmax
        return (umin, umax), (vmin, vmax)

    def point_coordinates(self, tag: int) -> FloatArray:
        """Get the coordinates of a point in the model.

        Parameters
        ----------
        tag
            The identifier of the point.

        Returns
        -------
        NDArray[np.float64]
            The coordinates of the point.

        """
        return cast(FloatArray, self.model.get_value(0, tag, []))

    def curve_coordinates_at(self, tag: int, u: float) -> FloatArray:
        """Get the coordinates of a point on a curve in the model.

        Parameters
        ----------
        tag
            The identifier of the curve.
        u
            The parameter of the curve.

        Returns
        -------
        NDArray[np.float64]
            The coordinates of the point on the curve.

        """
        return cast(FloatArray, self.model.get_value(1, tag, [u]))

    def surface_coordinates_at(self, tag: int, u: float, v: float) -> FloatArray:
        """Get the coordinates of a point on a surface in the model.

        Parameters
        ----------
        tag
            The identifier of the surface.
        u
            The first parameter of the surface.
        v
            The second parameter of the surface.

        Returns
        -------
        NDArray[np.float64]
            The coordinates of the point on the surface.

        """
        return cast(FloatArray, self.model.get_value(2, tag, [u, v]))

    # =============================================================================
    # Model geometry conversions
    # =============================================================================

    def point_to_point(self, tag: int) -> Point:
        """Get the coordinates of a point in the model.

        Parameters
        ----------
        tag
            The identifier of the point.

        Returns
        -------
        Point
            The point.

        """
        return Point(*self.point_coordinates(tag))

    def curve_to_polyline(self, tag: int, n: int = 100) -> Polyline:
        """Get the coordinates of a point on a curve in the model.

        Parameters
        ----------
        tag
            The identifier of the curve.
        n
            The number of points on the curve.

        Returns
        -------
        Polyline
            The polyline that is a discretisation of the curve.

        """
        u, v = self.curve_domain(tag)
        points = [self.curve_coordinates_at(tag, t) for t in linspace(u, v, n)]
        return Polyline(points)

    # =============================================================================
    # Model exploration
    # =============================================================================

    def find_points_at_xyz(self, xyz: PointLike) -> list[int]:
        """Find the model points at or close to a spatial location.

        Parameters
        ----------
        xyz
            The XYZ coordinates of the location.

        Returns
        -------
        list[int]
            The point identifiers.

        """
        points = []
        key = TOL.geometric_key(xyz)
        for point in self.points:
            test = TOL.geometric_key(self.point_coordinates(point))
            if test == key:
                points.append(point)
        return points

    def find_points_at_xy(self, xyz: PointLike) -> list[int]:
        """Find the model points at or close to a spatial location.

        Parameters
        ----------
        xyz
            The XY(Z) coordinates of the location.

        Returns
        -------
        list[int]
            The point identifiers.

        """
        points = []
        key = TOL.geometric_key_xy(xyz[:2])
        for point in self.points:
            test = TOL.geometric_key_xy(self.point_coordinates(point)[:2])
            if test == key:
                points.append(point)
        return points

    def find_points_within_distance_of_location(self, location: Point, distance: float) -> list[int]:
        """Find the model points within a distance from a given location.

        Parameters
        ----------
        location
            The reference location.
        distance
            The distance from the reference location.

        Returns
        -------
        list[int]
            The tags of the found points.

        """
        points = []
        for point in self.points:
            if location.distance_to_point(self.point_coordinates(point)) < distance:
                points.append(point)
        return points

    def find_points_within_horizontal_distance_of_location(self, location: Point, distance: float) -> list[int]:
        """Find the model points within a horizontal distance from a given location.

        Parameters
        ----------
        location
            The reference location.
        distance
            The horizontal distance from the reference location.

        Returns
        -------
        list[int]
            The tags of the found points.

        """
        points = []
        xy = location[:2]
        d2 = distance**2
        for point in self.points:
            if distance_point_point_sqrd_xy(xy, self.point_coordinates(point)[:2]) < d2:
                points.append(point)
        return points

    # ==============================================================================
    # Meshing
    # ==============================================================================

    def mesh_targetlength_at_point(self, tag: int, target: float) -> None:
        """Set the target length at a particular mesh point.

        Parameters
        ----------
        tag
            The point identifier.
        target
            The target length value.

        """
        self.occ.mesh.set_size([(0, tag)], target)

    def generate_mesh(self, dim: int = 2) -> None:
        """Generate a mesh of the current model.

        Parameters
        ----------
        dim
            The dimension of the mesh.

        Notes
        -----
        The mesh is stored in the model for further refinement and optimisation.
        To retrieve the generated mesh, use `mesh_to_compas`, `mesh_to_openmesh`, or `mesh_to_tets`.
        The geometry is automatically synchronised with the underlying OCC model.
        Therefore, there is no need to call `synchronize` before generating the mesh.
        To influence the meshing process, use the options of the model (`options.mesh`).

        """
        self.occ.synchronize()
        self.mesh.generate(dim)

    def refine_mesh(self) -> None:
        """Refine the model mesh by uniformly splitting the edges."""
        self.mesh.refine()

    def optimize_mesh(
        self,
        algo: OptimizationAlgorithm = OptimizationAlgorithm.Default,
        niter: int = 1,
    ) -> None:
        """Optimize the model mesh using the specified method.

        Parameters
        ----------
        algo
            The optimization algorithm to use.
        niter
            The number of iterations.

        """
        self.mesh.optimize(algo.value, niter=niter)

    def recombine_mesh(self) -> None:
        """Recombine the mesh into quadrilateral faces."""
        self.mesh.recombine()

    # =============================================================================
    # Mesh elements
    # =============================================================================

    def curve_vertices(self, tag: int) -> dict[int, FloatArray]:
        """Get the vertices of a curve.

        Parameters
        ----------
        tag
            The identifier of the curve.

        Returns
        -------
        dict[int, NDArray[np.float64]]
            The vertices of the curve.

        """
        node_tags, raw_node_coords, _ = self.mesh.get_nodes_by_element_type(1, tag)
        node_coords = cast(FloatArray, raw_node_coords)
        return dict(zip(node_tags, node_coords.reshape((-1, 3), order="C")))

    def surface_vertices(self, tag: int) -> dict[int, FloatArray]:
        """Get the vertices of a surface.

        Parameters
        ----------
        tag
            The identifier of the surface.

        Returns
        -------
        dict[int, NDArray[np.float64]]
            The vertices of the surface.

        """
        node_tags, raw_node_coords, _ = self.mesh.get_nodes_by_element_type(2, tag)
        node_coords = cast(FloatArray, raw_node_coords)
        return dict(zip(node_tags, node_coords.reshape((-1, 3), order="C")))

    def surface_faces(self, tag: int) -> list[IntArray]:
        """Get the faces of a surface.

        Parameters
        ----------
        tag
            The identifier of the surface.

        Returns
        -------
        list[NDArray[np.uint64]]
            The faces of the surface.

        """
        faces = []
        elements = self.mesh.get_elements(2, tag)
        for element_type, element_tags, node_tags in zip(*elements):
            element_props = self.mesh.get_element_properties(element_type)
            number_of_nodes = element_props[3]
            for i, element_tag in enumerate(element_tags):
                nodes = node_tags[i * number_of_nodes : (i + 1) * number_of_nodes]
                faces.append(nodes)
        return faces

    def surface_mesh(self, tag: int) -> Mesh:
        """Get the mesh of a surface entity.

        Parameters
        ----------
        tag
            The identifier of the surface.

        Returns
        -------
        Mesh
            The mesh of the surface.

        """
        vertices = self.surface_vertices(tag)
        faces = self.surface_faces(tag)
        mesh = Mesh.from_vertices_and_faces(vertices, faces)
        mesh.remove_unused_vertices()
        return mesh

    def volume_vertices(self, tag: int) -> dict[int, FloatArray]:
        """Get the vertices of a volume.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        dict[int, NDArray[np.float64]]
            The vertices of the volume.

        """
        vertices = {}
        _, downward = self.model.get_adjacencies(3, tag)
        for tag in downward:
            node_tags, raw_node_coords, _ = self.mesh.get_nodes_by_element_type(2, tag)
            node_coords = cast(FloatArray, raw_node_coords)
            vertices.update(dict(zip(node_tags, node_coords.reshape((-1, 3), order="C"))))
        return vertices

    def volume_faces(self, tag: int) -> list[IntArray]:
        """Get the faces of a volume.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        list[NDArray[np.uint64]]
            The faces of the volume.

        """
        _, downward = self.model.get_adjacencies(3, tag)
        faces = []
        for tag in downward:
            elements = self.mesh.get_elements(2, tag)
            for element_type, element_tags, node_tags in zip(*elements):
                element_props = self.mesh.get_element_properties(element_type)
                number_of_nodes = element_props[3]
                for i, element_tag in enumerate(element_tags):
                    faces.append(node_tags[i * number_of_nodes : (i + 1) * number_of_nodes])
        return faces

    def volume_mesh(self, tag: int) -> Mesh:
        """Get the mesh of a volume entity.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        Mesh
            The mesh of the volume.

        """
        vertices = self.volume_vertices(tag)
        faces = self.volume_faces(tag)
        mesh = Mesh.from_vertices_and_faces(vertices, faces)
        mesh.remove_unused_vertices()
        return mesh

    def volume_tets(self, tag: int) -> list[Polyhedron]:
        """Get the tetrahedra of a volume entity.

        Parameters
        ----------
        tag
            The identifier of the volume.

        Returns
        -------
        list[Polyhedron]
            The tetrahedra of the volume.

        """
        raise NotImplementedError

    # ==============================================================================
    # Export
    # ==============================================================================

    def mesh_node_xyz(self) -> dict[int, FloatArray]:
        """Get the coordinates of the mesh nodes.

        Returns
        -------
        dict[int, NDArray[np.float64]]
            A dictionary mapping node tags to node coordinates.

        """
        node_tags, raw_node_coords, _ = self.mesh.get_nodes()
        node_coords = cast(FloatArray, raw_node_coords)
        return dict(zip(node_tags, node_coords.reshape((-1, 3), order="C")))

    def mesh_to_vertices_and_faces(
        self,
    ) -> tuple[dict[int, FloatArray], list[IntArray]]:
        """Convert the model mesh to vertices and faces.

        Returns
        -------
        tuple[dict[int, NDArray[np.float64]], list[NDArray[np.uint64]]]
            A tuple containing the vertices and faces of the mesh.

        """
        vertices = self.mesh_node_xyz()

        # element_types is a list of element types
        # element_tags is a list containing a list of tags for each element type
        # node_tags is a list containing a flattened list of node tags for each element type
        elements = self.mesh.get_elements()
        faces = []
        for element_type, element_tags, node_tags in zip(*elements):
            number_of_nodes = self.mesh.get_element_properties(element_type)[3]
            if element_type in (2, 3):
                for i, element_tag in enumerate(element_tags):
                    face = node_tags[i * number_of_nodes : i * number_of_nodes + number_of_nodes]
                    faces.append(face)

        return vertices, faces

    def mesh_to_triangles(self) -> list[list[Point]]:
        """Convert the model mesh to a list of triangles.

        Returns
        -------
        list[list[Point]]
            A list of triangles.

        """
        # set the element type to triangles
        element_type = 2
        # get all triangle nodes
        tags, raw_coords, _ = self.mesh.get_nodes_by_element_type(element_type, returnParametricCoord=False)
        coords = cast(FloatArray, raw_coords)
        node_xyz = dict(zip(tags, coords.reshape((-1, 3), order="C")))
        # get properties of triangles
        element_props = self.mesh.get_element_properties(element_type)
        # get number of nodes per triangle
        number_of_nodes = element_props[3]
        # get all triangles
        # element_tags is a list of tags
        # node_tags is a flattened list of node tags
        element_tags, raw_node_tags = self.mesh.get_elements_by_type(element_type)
        # reshape the node_tags array to a 2D array
        node_tags = cast(IntArray, raw_node_tags).reshape((-1, number_of_nodes), order="C")
        # every row in node_tags is a triangle face
        triangles = [[Point(*node_xyz[node]) for node in face] for face in node_tags]
        return triangles

    def mesh_to_quads(self) -> list[list[Point]]:
        """Convert the model mesh to a list of quads.

        Returns
        -------
        list[list[Point]]
            A list of quads.

        """
        # set the element type to quads
        element_type = 3
        # get all quad nodes
        tags, raw_coords, _ = self.mesh.get_nodes_by_element_type(element_type, returnParametricCoord=False)
        coords = cast(FloatArray, raw_coords)
        node_xyz = dict(zip(tags, coords.reshape((-1, 3), order="C")))
        # get properties of quads
        element_props = self.mesh.get_element_properties(element_type)
        # get number of nodes per quad
        number_of_nodes = element_props[3]
        # get all quads
        # element_tags is a list of tags
        # node_tags is a flattened list of node tags
        element_tags, raw_node_tags = self.mesh.get_elements_by_type(element_type)
        # reshape the node_tags array to a 2D array
        node_tags = cast(IntArray, raw_node_tags).reshape((-1, number_of_nodes), order="C")
        # every row in node_tags is a quad face
        quads = [[Point(*node_xyz[node]) for node in face] for face in node_tags]
        return quads

    def mesh_to_tets(self) -> list[Polyhedron]:
        """Convert the model mesh to COMPAS tetrahedra.

        Returns
        -------
        list[Polyhedron]
            A list of COMPAS polyhedra.

        """
        # set the element type to tetrahedra
        element_type = 4
        # get all tetrahedra nodes
        tags, raw_coords, _ = self.mesh.get_nodes_by_element_type(element_type, returnParametricCoord=False)
        coords = cast(FloatArray, raw_coords)
        # make a node coordinate map
        node_xyz = dict(zip(tags, coords.reshape((-1, 3), order="C")))
        # get properties of tetrahedra
        element_props = self.mesh.get_element_properties(element_type)
        # get number of nodes per tetrahedron
        number_of_nodes = element_props[3]
        # get all tetrahedra
        element_tags, raw_node_tags = self.mesh.get_elements_by_type(element_type)
        node_tags = cast(IntArray, raw_node_tags).reshape((-1, number_of_nodes), order="C")
        # construct a polyhedron for each tetrahedron
        tets = []
        for nodes in node_tags:
            vertices = [node_xyz[node] for node in nodes]
            faces = [[0, 1, 2], [0, 2, 3], [1, 3, 2], [0, 3, 1]]
            tets.append(Polyhedron(vertices, faces))
        return tets

    def mesh_to_vertices_faces_edges(
        self,
        transformation: Transformation | None = None,
    ) -> tuple[list[list[float]], list[list[int]], list[tuple[int, int]]]:
        """Convert tetrahedra to indexed vertices, boundary faces, and edges.

        Parameters
        ----------
        transformation
            An optional transformation applied to the vertex coordinates.

        Returns
        -------
        tuple[list[list[float]], list[list[int]], list[tuple[int, int]]]
            The vertex coordinates, triangular faces, and edges.

        """
        # set the element type to tetrahedra
        element_type = 4
        # get all tetrahedra nodes
        tags, raw_coords, _ = self.mesh.get_nodes_by_element_type(element_type, returnParametricCoord=False)
        coords = cast(FloatArray, raw_coords)
        # make a node coordinate map
        node_index = {tag: index for index, tag in enumerate(tags)}
        # get properties of tetrahedra
        element_props = self.mesh.get_element_properties(element_type)
        # get number of nodes per tetrahedron
        number_of_nodes = element_props[3]
        # get all tetrahedra
        element_tags, raw_node_tags = self.mesh.get_elements_by_type(element_type)
        node_tags = cast(IntArray, raw_node_tags).reshape((-1, number_of_nodes), order="C")
        # construct the vertices faces and edges
        xyz = coords.reshape((-1, 3), order="C")
        if transformation:
            xyz = transform_points_numpy(xyz, transformation)
        vertices = xyz.tolist()
        faces = []
        edges = []
        for nodes in node_tags:
            faces.append([node_index[nodes[n]] for n in [0, 1, 2]])
            faces.append([node_index[nodes[n]] for n in [0, 2, 3]])
            faces.append([node_index[nodes[n]] for n in [1, 3, 2]])
            faces.append([node_index[nodes[n]] for n in [0, 3, 1]])
            edges.append((node_index[nodes[0]], node_index[nodes[1]]))
            edges.append((node_index[nodes[1]], node_index[nodes[2]]))
            edges.append((node_index[nodes[2]], node_index[nodes[0]]))
            edges.append((node_index[nodes[0]], node_index[nodes[3]]))
            edges.append((node_index[nodes[1]], node_index[nodes[3]]))
            edges.append((node_index[nodes[2]], node_index[nodes[3]]))
        return vertices, faces, edges

    def mesh_to_faces(self) -> list[list[FloatArray]]:
        """Convert tetrahedra to lists of coordinate faces.

        Returns
        -------
        list[list[NDArray[np.float64]]]
            Four triangular coordinate faces per tetrahedron.

        """
        # set the element type to tetrahedra
        element_type = 4
        # get all tetrahedra nodes
        tags, raw_coords, _ = self.mesh.get_nodes_by_element_type(element_type, returnParametricCoord=False)
        coords = cast(FloatArray, raw_coords)
        # make a node coordinate map
        node_xyz = dict(zip(tags, coords.reshape((-1, 3), order="C")))
        # get properties of tetrahedra
        element_props = self.mesh.get_element_properties(element_type)
        # get number of nodes per tetrahedron
        number_of_nodes = element_props[3]
        # get all tetrahedra
        element_tags, raw_node_tags = self.mesh.get_elements_by_type(element_type)
        node_tags = cast(IntArray, raw_node_tags).reshape((-1, number_of_nodes), order="C")
        # construct a polyhedron for each tetrahedron
        tets = []
        for nodes in node_tags:
            vertices = [node_xyz[node] for node in nodes]
            faces = [
                [vertices[0], vertices[1], vertices[2]],
                [vertices[0], vertices[2], vertices[3]],
                [vertices[1], vertices[3], vertices[2]],
                [vertices[0], vertices[3], vertices[1]],
            ]
            tets.append(faces)
        return tets

    def mesh_to_compas(self) -> Mesh:
        """Convert the model mesh to a COMPAS mesh data structure.

        Returns
        -------
        Mesh
            A COMPAS mesh.

        """
        vertices, faces = self.mesh_to_vertices_and_faces()
        return Mesh.from_vertices_and_faces(vertices, faces)

    def mesh_to_openmesh(self) -> object:
        """Convert the model mesh to an OpenMesh data structure.

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
        else:
            raise NotImplementedError

        vertex_index = {}
        for vertex in vertices:
            index = mesh.add_vertex(vertices[vertex])
            vertex_index[vertex] = index
        for face in faces:
            mesh.add_face(*[vertex_index[vertex] for vertex in face])

        return mesh
