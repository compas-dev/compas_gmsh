from compas.datastructures import Mesh
from compas_gmsh.models.model import Model


class MeshModel(Model):
    """Model for mesh (re)meshing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vertex_tag = {}

    @classmethod
    def from_mesh(cls: 'MeshModel',
                  mesh: Mesh,
                  name: str = 'Mesh',
                  targetlength: float = 1.0) -> None:
        model = cls(name)
        model.vertex_tag = {}
        for vertex in mesh.vertices():
            point = mesh.vertex_coordinates(vertex)
            model.vertex_tag[vertex] = model.occ.add_point(*point, targetlength)
        for face in mesh.faces():
            loop = []
            for u, v in mesh.face_halfedges(face):
                tag = model.occ.add_line(model.vertex_tag[u], model.vertex_tag[v])
                loop.append(tag)
            tag = model.occ.add_curve_loop(loop)
            model.occ.add_surface_filling(tag)
        return model

    def heal(self):
        self.occ.synchronize()
        self.occ.heal_shapes()

    def mesh_targetlength_at_vertex(self, vertex, target):
        tag = self.vertex_tag[vertex]
        self.occ.mesh.set_size([(0, tag)], target)
