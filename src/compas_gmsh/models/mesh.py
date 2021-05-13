from __future__ import annotations

from compas.datastructures import Mesh
from compas_gmsh.models.model import Model


class MeshModel(Model):
    """Model for mesh (re)meshing."""

    @classmethod
    def from_mesh(cls: MeshModel, mesh: Mesh, name: str = 'Mesh') -> MeshModel:
        model = cls(name)
        vertex_tag = {}
        for vertex in mesh.vertices():
            point = mesh.vertex_coordinates(vertex)
            vertex_tag[vertex] = model.factory.addPoint(*point)
        for face in mesh.faces():
            loop = []
            for u, v in mesh.face_halfedges(face):
                tag = model.factory.addLine(vertex_tag[u], vertex_tag[v])
                loop.append(tag)
            tag = model.factory.addCurveLoop(loop)
            model.factory.addSurfaceFilling(tag)
        return model
