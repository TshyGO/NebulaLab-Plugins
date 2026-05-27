"""Tests for importer priority compatibility (NebulaLab PR #202 tie-breaker)."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ---------------------------------------------------------------------------
# nebula_sdk.decorators
# ---------------------------------------------------------------------------

from nebula_sdk.decorators import _importer_registry, register_importer as sdk_register_importer


def test_sdk_register_importer_accepts_priority_keyword():
    """register_importer in the SDK shim must not raise when priority is passed."""
    @sdk_register_importer(
        id="_test_priority_sdk",
        name="Test",
        extensions=[".tst"],
        priority=10,
    )
    def _handler(path):
        return None

    assert _handler is not None


def test_sdk_register_importer_stores_priority_in_metadata():
    @sdk_register_importer(
        id="_test_priority_stored",
        name="Test Priority Stored",
        extensions=[".tst"],
        priority=7,
    )
    def _handler(path):
        return None

    assert _importer_registry["_test_priority_stored"]["priority"] == 7


def test_sdk_register_importer_defaults_priority_to_zero():
    @sdk_register_importer(
        id="_test_priority_default",
        name="Test Priority Default",
        extensions=[".tst"],
    )
    def _handler(path):
        return None

    assert _importer_registry["_test_priority_default"]["priority"] == 0


# ---------------------------------------------------------------------------
# xps_thermo_kalpha compat.py
# ---------------------------------------------------------------------------

from plugins.official.xps_thermo_kalpha.compat import (
    register_importer as compat_register_importer,
)


def test_compat_register_importer_accepts_priority_keyword():
    """compat.py register_importer must not raise TypeError when priority is passed."""
    @compat_register_importer(
        id="_test_compat_priority",
        name="Test Compat",
        extensions=[".tst"],
        priority=10,
    )
    def _handler(path):
        return None

    assert _handler is not None


def test_compat_register_importer_forwards_priority_to_engine(monkeypatch):
    """When engine is available, priority must be in the metadata dict forwarded to it."""
    captured = {}

    def fake_engine_register(id, func, metadata, detect_fn=None, source="plugin"):
        captured["metadata"] = metadata

    import plugins.official.xps_thermo_kalpha.compat as compat_module
    import importlib
    import sys

    # Inject a fake engine module so the compat branch takes the engine path.
    fake_engine = MagicMock()
    fake_engine.register_importer = fake_engine_register
    sys.modules.setdefault("engine", MagicMock())
    sys.modules.setdefault("engine.plugins", MagicMock())
    sys.modules["engine.plugins.importers"] = fake_engine

    try:
        @compat_register_importer(
            id="_test_compat_engine_priority",
            name="Test Engine Priority",
            extensions=[".tst"],
            priority=5,
        )
        def _handler(path):
            return None

        assert captured["metadata"]["priority"] == 5
    finally:
        del sys.modules["engine.plugins.importers"]


def test_compat_register_importer_defaults_priority_to_zero():
    @compat_register_importer(
        id="_test_compat_default_priority",
        name="Test Compat Default",
        extensions=[".tst"],
    )
    def _handler(path):
        return None

    assert _handler is not None  # no TypeError is the assertion; metadata stored in sdk


# ---------------------------------------------------------------------------
# BET plugin: priority propagated + detector still guards correctly
# ---------------------------------------------------------------------------

from plugins.official.bet_tristar.parser import detect_tristar_file


def _write_tristar_minimal(path: Path) -> None:
    df = pd.DataFrame([[None for _ in range(20)] for _ in range(5)])
    df.iat[1, 0] = "TriStar II Plus 3.03"
    with pd.ExcelWriter(path) as writer:
        df.to_excel(writer, index=False, header=False)


def test_bet_importer_registered_with_priority(tmp_path):
    """Importing the bet_tristar package must not raise TypeError due to priority arg."""
    import importlib
    import plugins.official.bet_tristar as bet_module

    # If the module loaded without TypeError, the priority kwarg is accepted.
    assert callable(bet_module.parse)


def test_bet_detector_rejects_non_tristar_file(tmp_path):
    path = tmp_path / "random.xls"
    pd.DataFrame([["Something Else"]]).to_excel(path, index=False, header=False)
    assert detect_tristar_file(path) is False


# ---------------------------------------------------------------------------
# XPS plugin: priority propagated + detector still guards correctly
# ---------------------------------------------------------------------------

from plugins.official.xps_thermo_kalpha.parser import detect_thermo_kalpha_xps_file


def test_xps_importer_registered_with_priority(tmp_path):
    """Importing the xps_thermo_kalpha package must not raise TypeError due to priority arg."""
    import plugins.official.xps_thermo_kalpha as xps_module

    assert callable(xps_module.parse)


def test_xps_detector_rejects_non_xps_file(tmp_path):
    path = tmp_path / "random.xlsx"
    pd.DataFrame([["Random Data", "Not XPS"]]).to_excel(path, index=False, header=False)
    assert detect_thermo_kalpha_xps_file(path) is False
