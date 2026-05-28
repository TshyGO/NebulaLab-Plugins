from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATE_PLUGINS_PATH = ROOT / ".github" / "scripts" / "validate_plugins.py"


def load_validate_plugins_module():
    spec = importlib.util.spec_from_file_location("validate_plugins_under_test", VALIDATE_PLUGINS_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_plugin(plugin_dir: Path, payload: dict) -> None:
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(payload, ensure_ascii=False),
        encoding="utf-8",
    )
    (plugin_dir / "__init__.py").write_text("# plugin entry\n", encoding="utf-8")


def test_official_plugin_manifest_requires_github_author_metadata(tmp_path: Path):
    module = load_validate_plugins_module()
    plugin_dir = tmp_path / "plugins" / "official" / "example_plugin"
    write_plugin(
        plugin_dir,
        {
            "id": "example-plugin",
            "name": "Example Plugin",
            "version": "1.0.0",
            "author": "Nebula Lab Team",
        },
    )

    errors = module.validate_plugin_dir(plugin_dir)

    assert f"ERROR: {plugin_dir / 'plugin.json'}: official plugins require author_github" in errors


def test_official_plugin_manifest_accepts_github_author_metadata(tmp_path: Path):
    module = load_validate_plugins_module()
    plugin_dir = tmp_path / "plugins" / "official" / "example_plugin"
    write_plugin(
        plugin_dir,
        {
            "id": "example-plugin",
            "name": "Example Plugin",
            "version": "1.0.0",
            "author": "example-user",
            "author_github": "example-user",
            "author_url": "https://github.com/example-user",
        },
    )

    assert module.validate_plugin_dir(plugin_dir) == []
