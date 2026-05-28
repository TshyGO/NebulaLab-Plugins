from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VALIDATE_INDEX_PATH = ROOT / ".github" / "scripts" / "validate_index.py"


def load_validate_index_module():
    spec = importlib.util.spec_from_file_location("validate_index_under_test", VALIDATE_INDEX_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE_INDEX = {
    "version": "1.0",
    "updated": "2026-05-28",
    "plugins": [
        {
            "id": "example-plugin",
            "name": "Example Plugin",
            "version": "1.0.0",
            "author": "example-user",
            "author_github": "example-user",
            "author_url": "https://github.com/example-user",
            "source": "official",
            "download_url": "https://github.com/TshyGO/NebulaLab-Plugins/releases/download/plugins/example-plugin-1.0.0.zip",
            "homepage": "https://github.com/TshyGO/NebulaLab-Plugins/tree/main/plugins/official/example_plugin",
            "sha256": "a" * 64,
        }
    ],
}


def run_validator(tmp_path: Path, payload: dict):
    module = load_validate_index_module()
    index_path = tmp_path / "plugins-index.json"
    index_path.write_text(module.json.dumps(payload), encoding="utf-8")
    module.INDEX_PATH = index_path
    module.main()


def test_official_plugins_require_github_author_metadata(tmp_path):
    payload = copy.deepcopy(BASE_INDEX)
    del payload["plugins"][0]["author_github"]

    with pytest.raises(SystemExit):
        run_validator(tmp_path, payload)


def test_official_plugin_author_url_must_match_github_handle(tmp_path):
    payload = copy.deepcopy(BASE_INDEX)
    payload["plugins"][0]["author_url"] = "https://github.com/someone-else"

    with pytest.raises(SystemExit):
        run_validator(tmp_path, payload)


def test_official_plugin_author_github_rejects_consecutive_hyphens(tmp_path):
    payload = copy.deepcopy(BASE_INDEX)
    payload["plugins"][0]["author_github"] = "example--user"
    payload["plugins"][0]["author_url"] = "https://github.com/example--user"

    with pytest.raises(SystemExit):
        run_validator(tmp_path, payload)


def test_official_plugin_accepts_valid_github_author_metadata(tmp_path):
    run_validator(tmp_path, copy.deepcopy(BASE_INDEX))
