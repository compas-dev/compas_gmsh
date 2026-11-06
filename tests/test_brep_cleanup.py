import shutil
from pathlib import Path
from typing import cast

import gmsh
import pytest
from compas.geometry import Brep
from compas_gmsh.models import Model


class StepExporter:
    """Small duck-typed STEP exporter used to isolate file ownership."""

    def __init__(self, source: Path) -> None:
        self.source = source
        self.exported_path: Path | None = None

    def to_step(self, filepath: str) -> None:
        self.exported_path = Path(filepath)
        shutil.copyfile(self.source, self.exported_path)


class InvalidStepExporter:
    """STEP exporter that produces input rejected by Gmsh."""

    def __init__(self) -> None:
        self.exported_path: Path | None = None

    def to_step(self, filepath: str) -> None:
        self.exported_path = Path(filepath)
        self.exported_path.write_text("not a STEP file", encoding="utf-8")


def test_from_brep_removes_intermediate_after_success() -> None:
    exporter = StepExporter(Path(__file__).parent / "fixtures" / "line.step")

    model = Model.from_brep(cast(Brep, exporter))
    try:
        assert model.curves
        assert exporter.exported_path is not None
        assert not exporter.exported_path.exists()
    finally:
        model.destroy()


def test_from_brep_removes_intermediate_and_finalizes_after_failure() -> None:
    exporter = InvalidStepExporter()

    with pytest.raises(Exception):
        Model.from_brep(cast(Brep, exporter))

    assert exporter.exported_path is not None
    assert not exporter.exported_path.exists()
    assert not gmsh.is_initialized()
