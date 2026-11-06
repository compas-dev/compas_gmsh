# Installation

## Requirements

`compas_gmsh` supports Python 3.12 through 3.14, COMPAS 3.x, NumPy 1.26 or
newer, and Gmsh 4.13.1 through 4.x.

The framework-verified targets are:

| Operating system | Architecture | Platform floor |
| --- | --- | --- |
| Windows | x86-64 | Windows 10 |
| Linux | x86-64 | glibc 2.28 |
| macOS | ARM64 | macOS 12 |

Gmsh also publishes a macOS x86-64 SDK for macOS 10.15 or newer. That target is
upstream-supported but is not currently framework-verified because a dependable
blocking runner is unavailable. Other architectures and source-built Gmsh
installations are best-effort.

## Install from PyPI

```console
$ python -m pip install compas_gmsh
```

This is the canonical installation path. It installs the official `gmsh` PyPI
SDK as a runtime dependency. Do not install both the PyPI SDK and Conda's Gmsh
Python bindings in the same environment.

For a uv-managed application:

```console
$ uv add compas_gmsh
```

## Development

Clone the repository and synchronize its locked development environment:

```console
$ git clone https://github.com/compas-dev/compas_gmsh.git
$ cd compas_gmsh
$ uv sync --frozen --group docs
$ uv run invoke check
$ uv run invoke test
$ uv run invoke docs
```

The committed `uv.lock` defines the tested development environment. It does not
change the compatibility ranges published in package metadata.

## Runtime license

The `compas_gmsh` wrapper is MIT-licensed. The official Gmsh runtime is a
separate distribution licensed by the Gmsh project under GPL-2.0-or-later.
Installing `compas_gmsh` installs that separate runtime dependency; the wrapper
wheel does not bundle it. See [Gmsh's license information](https://gmsh.info/#License).
