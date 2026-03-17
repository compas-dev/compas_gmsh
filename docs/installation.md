# Installation

## Stable

```bash
pip install compas_gmsh
```

Several examples use the COMPAS Viewer for visualisation.
To install `compas_viewer` in the same environment

```bash
pip install compas_viewer
```

## Development

To get the latest version, and install developer tools,
use a local clone of the repo.

```bash
conda create -n gmsh -c conda-forge compas
conda activate gmsh
git clone https://github.com/compas-dev/compas_gmsh.git
cd compas_gmsh
pip install -e ".[dev]"
```
