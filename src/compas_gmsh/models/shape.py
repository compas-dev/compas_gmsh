from __future__ import annotations

from typing import Tuple

from compas.geometry import Cylinder
from compas.geometry import Sphere
from compas.geometry import Box

from compas_gmsh.models.model import Model


class ShapeModel(Model):
    """Model for shape combinations."""

    def add_cylinder(self, cylinder: Cylinder) -> Tuple[int, int]:
        """Add a cylinder to the model."""
        H = cylinder.height
        R = cylinder.radius
        base = cylinder.plane.point
        normal = cylinder.plane.normal
        start = base + normal.scaled(-0.5 * H)
        vector = normal.scaled(H)
        x0, y0, z0 = start
        dx, dy, dz = vector
        tag = self.factory.addCylinder(x0, y0, z0, dx, dy, dz, R)
        return 3, tag

    def add_sphere(self, sphere: Sphere) -> Tuple[int, int]:
        """Add a sphere to the model."""
        x, y, z = sphere.point
        R = sphere.radius
        tag = self.factory.addSphere(x, y, z, R)
        return 3, tag

    def add_box(self, box: Box) -> Tuple[int, int]:
        """Add a box to the model."""
        x0, y0, z0 = box.frame.point
        x = x0 - 0.5 * box.xsize
        y = y0 - 0.5 * box.ysize
        z = z0 - 0.5 * box.zsize
        tag = self.factory.addBox(x, y, z, box.xsize, box.ysize, box.zsize)
        return 3, tag

    def boolean_intersection(self, A: Tuple[int, int], B: Tuple[int, int]) -> Tuple[int, int]:
        """Boolean intersection of two shapes.

        Parameters
        ----------
        A : tuple
            The dimension and tag of the first shape.
        B : tuple
            The dimension and tag of the second shape.

        Results
        -------
        tuple
            The dimension and tag of the resulting shape.
        """
        result = self.factory.intersect([A], [B])
        dimtags = result[0]
        return dimtags[0]

    def boolean_union(self, A: Tuple[int, int], B: Tuple[int, int]) -> Tuple[int, int]:
        """Boolean union of two shapes."""
        result = self.factory.fuse([A], [B])
        dimtags = result[0]
        return dimtags[0]

    def boolean_difference(self, A: Tuple[int, int], B: Tuple[int, int]) -> Tuple[int, int]:
        """Boolean difference of two shapes."""
        result = self.factory.cut([A], [B])
        dimtags = result[0]
        return dimtags[0]
