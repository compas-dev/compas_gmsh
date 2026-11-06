# Tutorial

Gmsh uses process-global runtime state. Create a model, perform the meshing
work, and always call `destroy` in a `finally` block.

## Planar meshing

The following example builds a square with Gmsh's OCC kernel, generates a
two-dimensional triangular mesh, and converts it to a COMPAS mesh.

```python
from compas_gmsh.models import Model

model = Model(name="square")
try:
    points = [
        model.occ.add_point(0.0, 0.0, 0.0),
        model.occ.add_point(1.0, 0.0, 0.0),
        model.occ.add_point(1.0, 1.0, 0.0),
        model.occ.add_point(0.0, 1.0, 0.0),
    ]
    curves = [model.occ.add_line(points[index], points[(index + 1) % 4]) for index in range(4)]
    loop = model.occ.add_curve_loop(curves)
    model.occ.add_plane_surface([loop])

    model.generate_mesh(2)
    mesh = model.mesh_to_compas()
finally:
    model.destroy()
```

`generate_mesh` synchronizes the OCC model before meshing. The conversion
retains the Gmsh node connectivity and returns an ordinary COMPAS `Mesh`.

## Solid meshing

For a three-dimensional mesh, add a closed OCC solid and request dimension 3.

```python
from compas_gmsh.models import Model

model = Model(name="box")
try:
    model.occ.add_box(0.0, 0.0, 0.0, 1.0, 1.0, 1.0)
    model.generate_mesh(3)
    tetrahedra = model.mesh_to_tets()
finally:
    model.destroy()
```

`mesh_to_tets` returns one COMPAS `Polyhedron` per first-order tetrahedral
element. The wrapper currently assumes the four-node tetrahedron element type;
high-order elements require separate handling.

## Importing a BRep

`Model.from_brep` exchanges geometry through the core `Brep.to_step` contract.
The temporary directory and STEP file exist only while Gmsh opens the model and
are removed on both success and failure.

```python
model = Model.from_brep(brep)
try:
    model.generate_mesh(3)
finally:
    model.destroy()
```

The BRep must provide a working STEP exporter, normally through a geometry
plugin such as COMPAS OCC. This optional native integration is not required for
ordinary `compas_gmsh` installation or planar/solid OCC meshing.
