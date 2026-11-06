from typing import Self
from typing import cast

from compas.datastructures import Mesh

from .model import Model


class MeshModel(Model):
    """Model for mesh (re)meshing."""

    def __init__(self, name: str | None = None, verbose: bool = False) -> None:
        super().__init__(name=name, verbose=verbose)
        self.vertex_tag: dict[int, int] = {}

    @classmethod
    def from_mesh(
        cls,
        mesh: Mesh,
        name: str = "Mesh",
        targetlength: float | dict[int, float] | None = None,
    ) -> Self:
        """Create a mesh model from a mesh.

        Parameters
        ----------
        mesh
            A COMPAS mesh.
        name
            The name of the model.
        targetlength
            Target value for the length of the mesh edges.

        Returns
        -------
        MeshModel

        """
        model = cls(name)

        for vertex in mesh.vertices():
            point = mesh.vertex_point(vertex)
            x, y, z = point
            if targetlength:
                if isinstance(targetlength, dict):
                    length = targetlength.get(vertex)
                else:
                    length = targetlength
                tag = model.occ.add_point(x, y, z, meshSize=cast(float, length))
            else:
                tag = model.occ.add_point(x, y, z)
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

    def find_point_at_vertex(self, vertex: int) -> int:
        """Find the model point at a vertex of the input mesh.

        Parameters
        ----------
        vertex
            A vertex of the input mesh.

        Returns
        -------
        int
            The point identifier.

        """
        return self.vertex_tag[vertex]

    def mesh_targetlength_at_vertex(self, vertex: int, target: float) -> None:
        """Set the target length at a particular mesh vertex.

        Parameters
        ----------
        vertex
            The vertex identifier.
        target
            The target length value.

        """
        tag = self.vertex_tag[vertex]
        self.occ.mesh.set_size([(0, tag)], target)

    def read_options_from_attributes(self) -> None:
        """Read the model options from the attributes of the mesh data structure."""
        pass
