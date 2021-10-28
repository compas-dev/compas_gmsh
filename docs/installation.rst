********************************************************************************
Installation
********************************************************************************

Releases
========

:mod:`compas_gmsh` can be installed with ``pip`` in a ``conda`` environment with the required dependencies.

.. code-block:: bash

    conda create -n gmsh compas compas_view2 --yes
    conda activate gmsh
    pip install compas_gmsh

.. note::

    :mod:`compas_view2` is not strictly required but very useful for visualising the results of the example scripts.


Development Version
===================

To install a development version, clone the repo and install from local source.

.. code-block:: bash

    conda create -n gmsh compas compas_view2 --yes
    conda activate gmsh
    git clone https://github.com/compas-dev/compas_gmsh.git
    cd compas_gmsh
    pip install -r requirements-dev.txt
