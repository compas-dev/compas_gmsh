# Examples

The repository contains checked examples for the package's core contracts:

- [`plate.py`](examples/plate.py) generates a planar mesh;
- [`tets.py`](examples/tets.py) generates a tetrahedral solid mesh; and
- [`brep_cleanup.py`](examples/brep_cleanup.py) demonstrates deterministic
  lifecycle cleanup for BRep import.

The examples are headless and do not write into the repository. If an
application exports a mesh or geometry file, it should use a caller-selected
path or a scoped temporary directory.
