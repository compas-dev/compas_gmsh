from collections.abc import Iterator

import gmsh
import pytest


@pytest.fixture(autouse=True)
def finalized_gmsh_runtime() -> Iterator[None]:
    """Keep Gmsh's process-global runtime isolated between tests."""
    if gmsh.is_initialized():
        gmsh.finalize()
    yield
    if gmsh.is_initialized():
        gmsh.finalize()
