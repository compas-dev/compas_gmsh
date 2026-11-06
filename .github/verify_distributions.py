import sys
import tarfile
import zipfile
from email.message import Message
from email.parser import BytesParser
from pathlib import Path

from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet
from packaging.utils import canonicalize_name

EXPECTED_REQUIREMENTS = {
    "compas": SpecifierSet(">=3,<4"),
    "gmsh": SpecifierSet(">=4.13.1,<5"),
    "numpy": SpecifierSet(">=1.26"),
}


def find_distributions(directory: Path) -> tuple[Path, Path]:
    """Return the single wheel and source distribution in a directory."""
    wheels = sorted(directory.glob("*.whl"))
    sdists = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise ValueError("Expected exactly one wheel and one source distribution.")
    if not wheels[0].stat().st_size or not sdists[0].stat().st_size:
        raise ValueError("Distribution files must not be empty.")
    return wheels[0], sdists[0]


def read_wheel_metadata(archive: zipfile.ZipFile) -> Message:
    """Read the single metadata file from a wheel archive."""
    metadata_names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
    if len(metadata_names) != 1:
        raise ValueError("Wheel must contain exactly one METADATA file.")
    return BytesParser().parsebytes(archive.read(metadata_names[0]))


def verify_wheel(wheel: Path) -> None:
    """Verify wheel contents and published compatibility metadata."""
    if not wheel.name.endswith("-py3-none-any.whl"):
        raise ValueError("The wrapper wheel must remain a pure-Python wheel.")

    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
        required = {
            "compas_gmsh/__init__.py",
            "compas_gmsh/models/model.py",
            "compas_gmsh/py.typed",
        }
        if not required.issubset(names):
            raise ValueError("Wheel is missing package code or py.typed.")
        if not any(name.endswith(".dist-info/licenses/LICENSE.MIT") for name in names):
            raise ValueError("Wheel is missing the MIT wrapper license.")
        if any(name.endswith("LICENSE.GPL") for name in names):
            raise ValueError("Wheel must not contain the obsolete GPL license file.")
        metadata = read_wheel_metadata(archive)

    if metadata["Requires-Python"] != ">=3.12":
        raise ValueError("Wheel has an unexpected Requires-Python value.")
    if metadata["License-Expression"] != "MIT":
        raise ValueError("Wheel has an unexpected license expression.")

    requirements = {}
    for value in metadata.get_all("Requires-Dist", []):
        requirement = Requirement(value)
        if requirement.marker is None:
            requirements[canonicalize_name(requirement.name)] = requirement.specifier
    if requirements != EXPECTED_REQUIREMENTS:
        raise ValueError("Wheel has unexpected runtime dependencies.")


def verify_sdist(sdist: Path) -> None:
    """Verify source distribution contents."""
    with tarfile.open(sdist) as archive:
        names = set(archive.getnames())
    roots = {name.split("/", 1)[0] for name in names}
    if len(roots) != 1:
        raise ValueError("Source distribution must have one root directory.")
    root = roots.pop()
    required = {
        f"{root}/LICENSE.MIT",
        f"{root}/README.md",
        f"{root}/pyproject.toml",
        f"{root}/src/compas_gmsh/__init__.py",
        f"{root}/src/compas_gmsh/py.typed",
        f"{root}/tests/fixtures/line.step",
    }
    if not required.issubset(names):
        raise ValueError("Source distribution is missing required project files.")
    if f"{root}/LICENSE.GPL" in names or f"{root}/environment-linux.yml" in names:
        raise ValueError("Source distribution contains an obsolete dependency authority or license file.")


def verify_distributions(directory: Path) -> None:
    """Verify the built wheel and source distribution."""
    wheel, sdist = find_distributions(directory)
    verify_wheel(wheel)
    verify_sdist(sdist)


if __name__ == "__main__":
    verify_distributions(Path(sys.argv[1]))
