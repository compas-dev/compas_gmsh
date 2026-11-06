from collections.abc import Callable
from typing import cast

from compas.geometry import Box
from compas.geometry import Cylinder
from compas.geometry import Shape
from compas.geometry import Sphere

from .model import Model

type DimTag = tuple[int, int]
type CSGTree = dict[str, list[object]]
type ShapeAdder = Callable[[Model, Shape], DimTag]


def add_cylinder(self: Model, cylinder: Cylinder) -> DimTag:
    """Add a cylinder to the model."""
    H = cylinder.height
    R = cylinder.radius
    base = cylinder.plane.point
    normal = cylinder.plane.normal
    start = base + normal.scaled(-0.5 * H)
    vector = normal.scaled(H)
    x0, y0, z0 = start
    dx, dy, dz = vector
    tag = self.occ.addCylinder(x0, y0, z0, dx, dy, dz, R)
    return 3, tag


def add_sphere(self: Model, sphere: Sphere) -> DimTag:
    """Add a sphere to the model."""
    x, y, z = sphere.base
    R = sphere.radius
    tag = self.occ.addSphere(x, y, z, R)
    return 3, tag


def add_box(self: Model, box: Box) -> DimTag:
    """Add a box to the model."""
    x0, y0, z0 = box.frame.point
    x = x0 - 0.5 * box.xsize
    y = y0 - 0.5 * box.ysize
    z = z0 - 0.5 * box.zsize
    tag = self.occ.addBox(x, y, z, box.xsize, box.ysize, box.zsize)
    return 3, tag


_SHAPE_FUNC: dict[type[Shape], ShapeAdder] = {
    Box: cast(ShapeAdder, add_box),
    Sphere: cast(ShapeAdder, add_sphere),
    Cylinder: cast(ShapeAdder, add_cylinder),
}


class CSGModel(Model):
    """Model for shape generation through Constructive Solid Geometry.

    Parameters
    ----------
    tree
        The CSG tree as a dictionary mapping operations to operands.
        The operations have to be one of `{"union", "intersection", "difference"}`.
        The operands have to be lists of shapes or lists of dicts that are CSG trees themselves.
        At every level of the tree, there can be only one operation.
    name
        The name of the model.

    Attributes
    ----------
    tree
        The CSG tree as a dictionary mapping operations to operands.
        The operations have to be one of `{"union", "intersection", "difference"}`.
        The operands have to be lists of shapes or lists of dicts that are CSG trees themselves.
        At every level of the tree, there can be only one operation.

    """

    def __init__(self, tree: CSGTree, name: str, verbose: bool = False) -> None:
        super().__init__(name, verbose=verbose)
        self._tree: CSGTree = {}
        self.tree = tree

    @property
    def tree(self) -> CSGTree:
        return self._tree

    @tree.setter
    def tree(self, tree: CSGTree) -> None:
        def check(tree: CSGTree) -> None:
            if len(tree) > 1:
                raise Exception("The tree can only have 1 operation per level.")
            operation = next(iter(tree))
            operands = tree[operation]
            for operand in operands:
                if isinstance(operand, dict):
                    check(cast(CSGTree, operand))

        try:
            check(tree)
        except Exception:
            raise
        else:
            self._tree = tree

    def add(self, shape: Shape) -> DimTag:
        """Add a shape to the underlying OCC model.

        Parameters
        ----------
        shape
            A geometric shape.

        Returns
        -------
        tuple[int, int]
            A "dimtag", a dimension and a tag that together uniquely identify the shape in the OCC model.

        """
        stype = type(shape)
        if stype not in _SHAPE_FUNC:
            raise Exception(f"Shape type is not supported: {stype}")
        dimtag = _SHAPE_FUNC[type(shape)](self, shape)
        return dimtag

    def compute_tree(self) -> None:
        """Compute the compound shape described by the CSG tree."""

        def walk(tree: CSGTree) -> DimTag | None:
            operation = next(iter(tree))
            operands = tree[operation]

            for index, operand in enumerate(operands):
                if isinstance(operand, dict):
                    operands[index] = walk(cast(CSGTree, operand))
                elif isinstance(operand, list):
                    operands[index] = [self.add(cast(Shape, item)) for item in operand]
                else:
                    operands[index] = self.add(cast(Shape, operand))

            if operation == "union":
                result = self.occ.fuse(operands[:-1], operands[-1:])
                return result[0][0]

            if operation == "difference":
                result = self.occ.cut(operands[:-1], operands[-1:])
                return result[0][0]

            if operation == "intersection":
                result = self.occ.intersect(operands[:-1], operands[-1:])
                return result[0][0]

            return None

        walk(self.tree)
