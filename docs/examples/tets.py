"""Generate a tetrahedral mesh for a simple OCC solid."""

from compas_gmsh.models import Model

model = Model(name="box")
try:
    model.occ.add_box(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    model.generate_mesh(3)
    tetrahedra = model.mesh_to_tets()
    print(len(tetrahedra))
finally:
    model.destroy()
