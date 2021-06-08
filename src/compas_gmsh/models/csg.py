from typing import Tuple
from compas_gmsh.models.model import Model
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


_OBJ_FUNC = {
    Box: add_box,
    Sphere: add_sphere,
    Cylinder: add_cylinder
}


class CSGModel(Model):

    def __init__(self, tree, name, **kwargs):
        super().__init__(name, **kwargs)
        self._tree = None
        self.tree = tree

    @property
    def tree(self):
        return self._tree

    @tree.setter
    def tree(self, tree):
        def check(tree):
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

    def add(self, obj):
        otype = type(obj)
        if otype not in _OBJ_FUNC:
            raise Exception(f'Object type is not supported: {otype}')
        dimtag = _OBJ_FUNC[type(obj)](self, obj)
        return dimtag

    def compute_tree(self):
        def walk(tree):
            operation = next(iter(tree))
            operands = tree[operation]
            for index, operand in enumerate(operands):
                if isinstance(operand, dict):
                    operands[index] = walk(operand)
                else:
                    operands[index] = [self.add(operand)]

            if operation == 'union':
                result = self.factory.fuse(operands[:-1], operands[-1:])
                return result[0]

            if operation == 'difference':
                result = self.factory.cut(operands[:-1], operands[-1:])
                return result[0]

            if operation == 'intersection':
                result = self.factory.intersect(operands[:-1], operands[-1:])
                return result[0]

        walk(self.tree)
