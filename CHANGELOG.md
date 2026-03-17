# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.6] 2026-03-17

### Added

* Added `compas_gmsh.models.Model.find_points_within_distance_of_location`.
* Added `compas_gmsh.models.Model.find_points_within_horizontal_distance_of_location`.

### Changed

* Changed doc system to mkdocs.

### Removed


## [0.4.5] 2025-12-02

### Added

### Changed

* Fixed bug related to implicit healing of shapes in `compas_gmsh.models.mesh.MeshModel.generate`.

### Removed


## [0.4.4] 2025-06-24

### Added

* Added support for `.brep` files for easier exchange with OCC geometries.

### Changed

### Removed


## [0.4.3] 2025-06-13

### Added

* Added implementation for `compas_gmsh.models.Model.from_brep`.

### Changed

### Removed


## [0.4.2] 2024-05-13

### Added

### Changed

* Updated github workflows to latest version.

### Removed


## [0.4.1] 2022-10-07

### Added

### Changed

### Removed


## [0.4.0] 2022-10-07

### Added

* Added `compas_gmsh.models.Model.options.mesh.algorithm`.
* Added `compas_gmsh.models.Model.options.mesh.lmin`.
* Added `compas_gmsh.models.Model.options.mesh.lmax`.
* Added `compas_gmsh.models.Model.options.mesh.mesh_only_empty`.
* Added `compas_gmsh.models.Model.options.mesh.meshsize_extend_from_boundary`.
* Added `compas_gmsh.models.Model.options.mesh.meshsize_min`.
* Added `compas_gmsh.models.Model.options.mesh.meshsize_max`.
* Added `compas_gmsh.models.Model.options.mesh.meshsize_from_curvature`.
* Added `compas_gmsh.models.Model.options.mesh.meshsize_from_points`.
* Added `compas_gmsh.models.Model.options.mesh.min_nodes_circle`.
* Added `compas_gmsh.models.Model.options.mesh.min_nodes_curve`.
* Added `compas_gmsh.models.Model.from_step`.

### Changed

### Removed

* Removed `compas_gmsh.models.Model.mesh_lmin`.
* Removed `compas_gmsh.models.Model.mesh_lmax`.

