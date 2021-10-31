from typing import Tuple
from typing import List
from compas_gmsh.models.model import Model

import compas.geometry
from compas.geometry import Box
from compas.geometry import Sphere
from compas.geometry import Cylinder


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
    tag = self.occ.addCylinder(x0, y0, z0, dx, dy, dz, R)
    return 3, tag


def add_sphere(self, sphere: Sphere) -> Tuple[int, int]:
    """Add a sphere to the model."""
    x, y, z = sphere.point
    R = sphere.radius
    tag = self.occ.addSphere(x, y, z, R)
    return 3, tag


def add_box(self, box: Box) -> Tuple[int, int]:
    """Add a box to the model."""
    x0, y0, z0 = box.frame.point
    x = x0 - 0.5 * box.xsize
    y = y0 - 0.5 * box.ysize
    z = z0 - 0.5 * box.zsize
    tag = self.occ.addBox(x, y, z, box.xsize, box.ysize, box.zsize)
    return 3, tag


_SHAPE_FUNC = {
    Box: add_box,
    Sphere: add_sphere,
    Cylinder: add_cylinder
}


class CSGModel(Model):
    """Model for shape generation through Constructive Solid Geometry.

    Parameters
    ----------
    tree : dict
        The CSG tree as a dictionary mapping operations to operands.
        The operations have to be one of `{'union', 'intersection', 'difference'}`.
        The operands have to be lists of shapes or lists of dicts that are CSG trees themselves.
        At every level of the tree, there can be only one operation.
    name : str
        The name of the model.

    """

    def __init__(self, tree: dict, name: str, **kwargs) -> None:
        super().__init__(name, **kwargs)
        self._tree = None
        self.tree = tree

    @property
    def tree(self) -> dict:
        """dict :
        The CSG tree as a dictionary mapping operations to operands.
        The operations have to be one of `{'union', 'intersection', 'difference'}`.
        The operands have to be lists of shapes or lists of dicts that are CSG trees themselves.
        At every level of the tree, there can be only one operation.
        """
        return self._tree

    @tree.setter
    def tree(self, tree: dict) -> None:
        def check(tree: dict) -> None:
            if len(tree) > 1:
                raise Exception('The tree can only have 1 operation per level.')
            operation = next(iter(tree))
            operands = tree[operation]
            for operand in operands:
                if isinstance(operand, dict):
                    check(operand)
        try:
            check(tree)
        except Exception:
            raise
        else:
            self._tree = tree

    def add(self, shape: compas.geometry.Shape) -> Tuple[int, int]:
        """Add a shape to the underlying OCC model.

        Parameters
        ----------
        shape : :class:`compas.geometry.Shape`
            A geometric shape.

        Returns
        -------
        tuple(int, int)
            A "dimtag", a dimension and a tag that together uniquely identify the shape in the OCC model.
        """
        stype = type(shape)
        if stype not in _SHAPE_FUNC:
            raise Exception(f'Shape type is not supported: {stype}')
        dimtag = _SHAPE_FUNC[type(shape)](self, shape)
        return dimtag

    def compute_tree(self) -> None:
        """Comute the compound shape resulting from the operations on shape primitives in the tree."""
        def walk(tree: dict) -> List[Tuple[int, int]]:
            operation = next(iter(tree))
            operands = tree[operation]

            for index, operand in enumerate(operands):
                if isinstance(operand, dict):
                    operands[index] = walk(operand)
                elif isinstance(operand, list):
                    operands[index] = [self.add(o) for o in operand]
                else:
                    operands[index] = self.add(operand)

            if operation == 'union':
                result = self.occ.fuse(operands[:-1], operands[-1:])
                return result[0][0]

            if operation == 'difference':
                result = self.occ.cut(operands[:-1], operands[-1:])
                return result[0][0]

            if operation == 'intersection':
                result = self.occ.intersect(operands[:-1], operands[-1:])
                return result[0][0]

        walk(self.tree)
