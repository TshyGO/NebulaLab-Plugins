from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = ROOT / "plugins"
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: plugin.json must contain an object")
    return payload


def discover_plugin_dirs(root: Path) -> list[Path]:
    plugin_dirs: list[Path] = []
    for path in root.rglob("plugin.json"):
        if "__pycache__" in path.parts:
            continue
        plugin_dirs.append(path.parent)
    return sorted(plugin_dirs)


def extract_panel_candidates(config: dict[str, Any]) -> list[str]:
    candidates: list[str] = []
    panel = config.get("panel")
    if isinstance(panel, str) and panel.strip():
        candidates.append(panel.strip())
    elif isinstance(panel, dict):
        for key in ("file", "path", "entry", "html"):
            value = panel.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(value.strip())
    elif panel is True:
        candidates.append("panel.html")

    for key in ("panel_file", "panel_path", "panel_entry"):
        value = config.get(key)
        if isinstance(value, str) and value.strip():
            candidates.append(value.strip())

    if "panel.html" not in candidates:
        candidates.append("panel.html")
    return candidates


def validate_plugin_dir(plugin_dir: Path) -> list[str]:
    errors: list[str] = []
    plugin_json = plugin_dir / "plugin.json"
    if not plugin_json.exists():
        return [f"ERROR: {plugin_dir}: missing plugin.json"]

    try:
        payload = load_json(plugin_json)
    except ValueError as exc:
        return [f"ERROR: {exc}"]

    for field in ("id", "name", "version"):
        value = payload.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"ERROR: {plugin_json}: missing required string field '{field}'")

    version = payload.get("version")
    if isinstance(version, str) and not SEMVER_PATTERN.fullmatch(version):
        errors.append(f"ERROR: {plugin_json}: version must match semver x.y.z")

    init_file = plugin_dir / "__init__.py"
    if init_file.exists():
        if init_file.stat().st_size == 0:
            errors.append(f"ERROR: {init_file}: file exists but is empty")
        return errors

    panel_candidates = extract_panel_candidates(payload)
    if not any((plugin_dir / candidate).is_file() for candidate in panel_candidates):
        joined = ", ".join(panel_candidates)
        errors.append(
            f"ERROR: {plugin_dir}: missing __init__.py and no panel file found (checked: {joined})"
        )

    return errors


def main() -> None:
    if not PLUGINS_DIR.exists():
        print(f"ERROR: Missing plugins directory: {PLUGINS_DIR}")
        raise SystemExit(1)

    plugin_dirs = discover_plugin_dirs(PLUGINS_DIR)
    if not plugin_dirs:
        print("ERROR: No plugins with plugin.json were found under plugins/")
        raise SystemExit(1)

    errors: list[str] = []
    for plugin_dir in plugin_dirs:
        errors.extend(validate_plugin_dir(plugin_dir))

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print(f"Validated {len(plugin_dirs)} plugin(s)")


if __name__ == "__main__":
    main()
