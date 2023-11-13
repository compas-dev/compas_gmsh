import compas
from compas.geometry import Box
from compas_gmsh.models import ShapeModel
from compas_view2.app import App

b1 = Box.from_corner_corner_height([0, 0, 0], [1, 1, 0], 1)
b2 = Box.from_corner_corner_height([1.1, 0, 0], [2, 1, 0], 1)

model = ShapeModel(name="arch")

model.add_box(b1)
model.add_box(b2)

model.generate_mesh()
mesh = model.mesh_to_compas()

compas.json_dump(mesh, 'test.json')

viewer = App(width=1600, height=900)

viewer.view.camera.rz = 0
viewer.view.camera.rx = -55
viewer.view.camera.tx = -2.5
viewer.view.camera.ty = 0
viewer.view.camera.distance = 7

viewer.add(mesh)

viewer.run()
