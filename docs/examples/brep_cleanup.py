"""Import a BRep while deterministically finalizing the Gmsh runtime."""

from compas.geometry import Box
from compas.geometry import Brep
from compas_gmsh.models import Model

brep = Brep.from_box(Box(1.0))
model = Model.from_brep(brep)
try:
    model.generate_mesh(3)
    tetrahedra = model.mesh_to_tets()
    print(len(tetrahedra))
finally:
    model.destroy()
