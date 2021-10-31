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
                  name: str = 'Mesh') -> None:
        model = cls(name)
        for vertex in mesh.vertices():
            point = mesh.vertex_coordinates(vertex)
            model.vertex_tag[vertex] = model.occ.addPoint(*point)
        for face in mesh.faces():
            loop = []
            for u, v in mesh.face_halfedges(face):
                tag = model.occ.addLine(model.vertex_tag[u], model.vertex_tag[v])
                loop.append(tag)
            tag = model.occ.addCurveLoop(loop)
            model.occ.addSurfaceFilling(tag)
        model.heal()
        return model

    def heal(self):
        self.occ.synchronize()
        self.occ.healShapes()

    def vertex_target(self, vertex, target):
        tag = self.vertex_tag[vertex]
        self.occ.mesh.setSize([(0, tag)], target)
