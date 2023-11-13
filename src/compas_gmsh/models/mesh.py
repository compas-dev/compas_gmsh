from typing import Optional, Union, Dict
from compas.datastructures import Mesh
from compas.utilities import geometric_key_xy
from compas.utilities import geometric_key
from .model import Model


class MeshModel(Model):
    """Model for mesh (re)meshing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vertex_tag = {}

    @classmethod
    def from_mesh(
        cls: "MeshModel",
        mesh: Mesh,
        name: str = "Mesh",
        targetlength: Optional[Union[float, Dict]] = None,
    ) -> "MeshModel":
        """
        Create a mesh model from a mesh.

        Parameters
        ----------
        mesh : :class:`Mesh`
            A COMPAS mesh.
        name : str, optional
            The name of the model.
        target_length : float, optional
            Target value for the length of the mesh edges.

        Returns
        -------
        :class:`MeshModel`

        """
        model: MeshModel = cls(name)

        for vertex in mesh.vertices():
            point = mesh.vertex_coordinates(vertex)
            if targetlength:
                if isinstance(targetlength, dict):
                    length = targetlength.get(vertex)
                else:
                    length = targetlength
                tag = model.occ.add_point(*point, length)
            else:
                tag = model.occ.add_point(*point)
            model.vertex_tag[vertex] = tag

        for face in mesh.faces():
            loop = []
            for u, v in mesh.face_halfedges(face):
                tag = model.occ.add_line(model.vertex_tag[u], model.vertex_tag[v])
                loop.append(tag)
            tag = model.occ.add_curve_loop(loop)
            model.occ.add_surface_filling(tag)

        model.synchronize()
        return model

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
        self.occ.heal_shapes()
        self.occ.synchronize()
        self.mesh.generate(dim)

    def find_point_at_vertex(self, vertex: int) -> int:
        """Find the model point at a vertex of the input mesh.

        Parameters
        ----------
        vertex : int
            A vertex of the input mesh.

        Returns
        -------
        int
            The point identifier.

        """
        return self.vertex_tag[vertex]

    def find_points_at_xyz(self, xyz: list[float], tolerance=None) -> list[int]:
        """Find the model points at or close to a spatial location.

        Parameters
        ----------
        xyz : list of float
            The XYZ coordinates of the location.

        Returns
        -------
        list of int
            The point identifiers.

        """
        points = []
        key = geometric_key(xyz)
        for point in self.points:
            test = geometric_key(self.point_coordinates(point))
            if test == key:
                points.append(point)
        return points

    def find_points_at_xy(self, xyz: list[float], tolerance=None) -> list[int]:
        """Find the model points at or close to a spatial location.

        Parameters
        ----------
        xyz : list of float
            The XY(Z) coordinates of the location.

        Returns
        -------
        list of int
            The point identifiers.

        """
        points = []
        key = geometric_key_xy(xyz[:2])
        for point in self.points:
            test = geometric_key_xy(self.point_coordinates(point)[:2])
            if test == key:
                points.append(point)
        return points

    def mesh_targetlength_at_vertex(self, vertex: int, target: float) -> None:
        """
        Set the target length at a particular mesh vertex.

        Parameters
        ----------
        vertex : int
            The vertex identifier.
        target : float
            The target length value.

        Returns
        -------
        None

        """
        tag = self.vertex_tag[vertex]
        self.occ.mesh.set_size([(0, tag)], target)

    def mesh_targetlength_at_point(self, tag: int, target: float) -> None:
        """
        Set the target length at a particular mesh point.

        Parameters
        ----------
        tag : int
            The point identifier.
        target : float
            The target length value.

        Returns
        -------
        None

        """
        self.occ.mesh.set_size([(0, tag)], target)

    def read_options_from_attributes(self) -> None:
        """Read the model options from the attributes of the mesh data structure.

        Returns
        -------
        None

        """
        pass
