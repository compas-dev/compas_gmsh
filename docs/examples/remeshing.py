"""Remesh a planar COMPAS mesh with a uniform target length."""

from compas.datastructures import Mesh
from compas_gmsh.models import MeshModel

source = Mesh.from_meshgrid(dx=5.0, nx=5)
model = MeshModel.from_mesh(source, name="remeshing", targetlength=0.25)
try:
    model.generate_mesh(2)
    remeshed = model.mesh_to_compas()
    print(remeshed.number_of_vertices(), remeshed.number_of_faces())
finally:
    model.destroy()
