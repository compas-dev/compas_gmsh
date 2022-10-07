from typing import Tuple, List

from compas.geometry import Cylinder
from compas.geometry import Sphere
from compas.geometry import Box

from compas_gmsh.models.model import Model


class ShapeModel(Model):
    """
    Model for shape combinations.
    """

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
        tag = self.occ.add_cylinder(x0, y0, z0, dx, dy, dz, R)
        return 3, tag

    def add_sphere(self, sphere: Sphere) -> Tuple[int, int]:
        """Add a sphere to the model."""
        x, y, z = sphere.point
        R = sphere.radius
        tag = self.occ.add_sphere(x, y, z, R)
        return 3, tag

    def add_box(self, box: Box) -> Tuple[int, int]:
        """Add a box to the model."""
        x0, y0, z0 = box.frame.point
        x = x0 - 0.5 * box.xsize
        y = y0 - 0.5 * box.ysize
        z = z0 - 0.5 * box.zsize
        tag = self.occ.add_box(x, y, z, box.xsize, box.ysize, box.zsize)
        return 3, tag

    def boolean_intersection(
        self,
        A: List[Tuple[int, int]],
        B: List[Tuple[int, int]],
        remove_objects: bool = True,
        remove_tools: bool = True,
    ) -> List[Tuple[int, int]]:
        """
        Boolean intersection of two sets of shapes.

        Parameters
        ----------
        A : list of tuple
            The *dimtags* of the *object* shapes.
        B : tuple
            The *dimtags* of the *tool* shapes.

        Results
        -------
        list of tuple
            The dimtags of the resulting shapes.

        Notes
        -----
        The *objects* are the shapes to which the boolean operation should be applied.
        The *tools* are the shapes used to perform the operation.

        """
        result = self.occ.intersect(
            A, B, removeObject=remove_objects, removeTool=remove_tools
        )
        dimtags = result[0]
        return dimtags

    def boolean_union(
        self,
        A: List[Tuple[int, int]],
        B: List[Tuple[int, int]],
        remove_objects: bool = True,
        remove_tools: bool = True,
    ) -> List[Tuple[int, int]]:
        """
        Boolean union of two sets of shapes.

        Parameters
        ----------
        A : list of tuple
            The *dimtags* of the *object* shapes.
        B : tuple
            The *dimtags* of the *tool* shapes.

        Results
        -------
        list of tuple
            The dimtags of the resulting shapes.

        Notes
        -----
        The *objects* are the shapes to which the boolean operation should be applied.
        The *tools* are the shapes used to perform the operation.

        """
        result = self.occ.fuse(
            A, B, removeObject=remove_objects, removeTool=remove_tools
        )
        dimtags = result[0]
        return dimtags

    def boolean_difference(
        self,
        A: List[Tuple[int, int]],
        B: List[Tuple[int, int]],
        remove_objects: bool = True,
        remove_tools: bool = True,
    ) -> List[Tuple[int, int]]:
        """
        Boolean difference of two sets of shapes.

        Parameters
        ----------
        A : list of tuple
            The *dimtags* of the *object* shapes.
        B : tuple
            The *dimtags* of the *tool* shapes.

        Results
        -------
        list of tuple
            The dimtags of the resulting shapes.

        Notes
        -----
        The *objects* are the shapes to which the boolean operation should be applied.
        The *tools* are the shapes used to perform the operation.

        """
        result = self.occ.cut(
            A, B, removeObject=remove_objects, removeTool=remove_tools
        )
        dimtags = result[0]
        return dimtags

    def boolean_fragment(
        self,
        A: List[Tuple[int, int]],
        B: List[Tuple[int, int]],
        remove_objects: bool = True,
        remove_tools: bool = True,
    ) -> List[Tuple[int, int]]:
        """
        Boolean fragment of two sets of shapes.

        Parameters
        ----------
        A : list of tuple
            The *dimtags* of the *object* shapes.
        B : tuple
            The *dimtags* of the *tool* shapes.

        Results
        -------
        list of tuple
            The dimtags of the resulting shapes.

        Notes
        -----
        The *objects* are the shapes to which the boolean operation should be applied.
        The *tools* are the shapes used to perform the operation.

        """
        result = self.occ.fragment(
            A, B, removeObject=remove_objects, removeTool=remove_tools
        )
        dimtags = result[0]
        return dimtags
