from __future__ import annotations

from typing import Dict, Optional

from compas.datastructures import Mesh
from compas_gmsh.models.model import Model


class MeshModel(Model):
    """Model for mesh (re)meshing."""

    @classmethod
    def from_mesh(cls: MeshModel,
                  mesh: Mesh,
                  default_length: float,
                  name: str = 'Mesh',
                  vertex_length: Optional[Dict[int, float]] = None) -> MeshModel:
        model = cls(name)
        vertex_length = vertex_length or {}
        vertex_tag = {}
        for vertex in mesh.vertices():
            point = mesh.vertex_coordinates(vertex)
            size = vertex_length.get(vertex, default_length)
            vertex_tag[vertex] = model.factory.addPoint(*point, size)
        for face in mesh.faces():
            loop = []
            for u, v in mesh.face_halfedges(face):
                tag = model.factory.addLine(vertex_tag[u], vertex_tag[v])
                loop.append(tag)
            tag = model.factory.addCurveLoop(loop)
            # this could be a planar surface if the corresponding face is a triangle
            # and a ruled surface if a quad
            # filling is for ngon
            model.factory.addSurfaceFilling(tag)
        return model
