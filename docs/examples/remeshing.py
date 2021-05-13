import compas
from compas.datastructures import Mesh
from compas_gmsh.models import MeshModel
from compas_view2.app import App

mesh = Mesh.from_obj(compas.get('tubemesh.obj'))

model = MeshModel.from_mesh(mesh, name='tubemesh')

model.length_min = 0.1
model.length_max = 0.5
model.generate_mesh()

viewer = App()
viewer.add(model.mesh_to_compas())
viewer.run()
