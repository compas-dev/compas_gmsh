# COMPAS GMSH

![build](https://github.com/compas-dev/compas_gmsh/workflows/build/badge.svg)
[![GitHub - License](https://img.shields.io/github/license/compas-dev/compas_gmsh.svg)](https://github.com/compas-dev/compas_gmsh)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/compas_gmsh.svg)](https://pypi.python.org/project/compas_gmsh)
[![PyPI - Latest Release](https://img.shields.io/pypi/v/compas_gmsh.svg)](https://pypi.python.org/project/compas_gmsh)

COMPAS friendly interface for Gmsh.

## Installation

```bash
pip install compas_gmsh
```

### Linux

On linux, you may have to install gmsh and it's python bindings manually.

```bash
conda create -n gmsh-dev gmsh python-gmsh -y
conda activate gmsh-dev
pip install compas_gmsh
```

Or use the environment file in this repo

```bash
conda env create -f environment-linux.yml
```

## Getting Started

Have a look at some of the first [examples in the documentation](https://compas.dev/compas_gmsh/latest/examples.html).

## License

`compas_gmsh` provides a COMPAS friendly interface to `Gmsh`.
`Gmsh` is released under GPL-2.0-or-later.
