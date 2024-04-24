********************************************************************************
Installation
********************************************************************************

Releases
========

:mod:`compas_gmsh` can be installed with ``pip``.

.. code-block:: bash

    pip install compas_gmsh

Several examples use the COMPAS Viewer for visualisation.
To install :mod:`compas_viewer` in the same environment

.. code-block:: bash

    pip install compas_viewer


Development Version
===================

To install a development version, clone the repo and install from local source.

.. code-block:: bash

    conda create -n gmsh -c conda-forge compas
    conda activate gmsh
    git clone https://github.com/compas-dev/compas_gmsh.git
    cd compas_gmsh
    pip install -e ".[dev]"
