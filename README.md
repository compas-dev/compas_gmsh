# COMPAS Gmsh

![build](https://github.com/compas-dev/compas_gmsh/workflows/build/badge.svg)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_gmsh.svg)](https://github.com/compas-dev/compas_gmsh)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compas_gmsh.svg)](https://pypi.python.org/project/compas_gmsh)
[![PyPI - Latest Release](https://img.shields.io/pypi/v/compas_gmsh.svg)](https://pypi.python.org/project/compas_gmsh)

A COMPAS-friendly interface to the official Gmsh Python SDK.

## Installation

```console
$ python -m pip install compas_gmsh
```

This installs the separately distributed official `gmsh` package from PyPI.
`compas_gmsh` supports Python 3.12 through 3.14 and Gmsh 4.13.1 through 4.x.
See the [installation guide](https://compas-dev.github.io/compas_gmsh/installation/)
for the framework-verified platform matrix.

## Getting Started

Start with the [tutorial](https://compas-dev.github.io/compas_gmsh/tutorial/).

## License

The `compas_gmsh` wrapper is released under the MIT License.
It depends on the separately installed Gmsh runtime, which is distributed by
the Gmsh project under GPL-2.0-or-later. The wrapper does not bundle Gmsh.
See [Gmsh's license information](https://gmsh.info/#License) for the runtime's
terms. If a future distribution bundles or modifies Gmsh, it requires a new
license review.
