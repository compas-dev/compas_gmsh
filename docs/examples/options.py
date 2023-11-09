import gmsh
from compas_gmsh.options import MeshOptions

gmsh.initialize()

options = MeshOptions()

print(options.algorithm)
print(options.lmin)
print(options.lmax)
print(options.mesh_only_empty)
print(options.meshsize_extend_from_boundary)
print(options.meshsize_min)
print(options.meshsize_max)
print(options.meshsize_from_curvature)
print(options.meshsize_from_points)
print(options.min_nodes_circle)
print(options.min_nodes_curve)
