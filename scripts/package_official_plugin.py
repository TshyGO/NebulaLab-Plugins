from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_PLUGINS_DIR = ROOT / "plugins" / "official"
INDEX_PATH = ROOT / "plugins-index.json"
DEFAULT_OUTPUT_DIR = ROOT / "dist" / "plugins"
DEFAULT_RELEASE_TAG = "plugins"
DEFAULT_REPO = "TshyGO/NebulaLab-Plugins"

EXCLUDE_PATTERNS = (
    "__pycache__/*",
    "*.pyc",
    "*.pyo",
    ".pytest_cache/*",
    ".DS_Store",
)


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path} is not valid JSON: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path} must contain a JSON object")
    return payload


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def discover_plugin_dir(plugin: str) -> Path:
    direct = OFFICIAL_PLUGINS_DIR / plugin
    if direct.is_dir():
        return direct

    matches: list[Path] = []
    for candidate in OFFICIAL_PLUGINS_DIR.iterdir():
        if not candidate.is_dir():
            continue
        manifest = candidate / "plugin.json"
        if not manifest.is_file():
            continue
        payload = load_json(manifest)
        if payload.get("id") == plugin:
            matches.append(candidate)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        fail(f"multiple official plugins use id {plugin!r}: {matches}")
    fail(f"official plugin not found by folder or id: {plugin}")


def should_exclude(relative: Path) -> bool:
    posix = relative.as_posix()
    return any(fnmatch.fnmatch(posix, pattern) for pattern in EXCLUDE_PATTERNS)


def iter_package_files(plugin_dir: Path) -> list[Path]:
    files: list[Path] = []
    for path in plugin_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(plugin_dir)
        if should_exclude(relative):
            continue
        files.append(path)
    return sorted(files)


def build_zip(plugin_dir: Path, output_dir: Path) -> tuple[Path, str]:
    manifest = load_json(plugin_dir / "plugin.json")
    plugin_id = manifest.get("id")
    version = manifest.get("version")
    if not isinstance(plugin_id, str) or not plugin_id:
        fail(f"{plugin_dir / 'plugin.json'} is missing string field 'id'")
    if not isinstance(version, str) or not version:
        fail(f"{plugin_dir / 'plugin.json'} is missing string field 'version'")

    output_dir.mkdir(parents=True, exist_ok=True)
    archive_path = output_dir / f"{plugin_id}-{version}.zip"
    package_root = plugin_dir.name

    files = iter_package_files(plugin_dir)
    if not files:
        fail(f"no package files found in {plugin_dir}")

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file_path in files:
            relative = file_path.relative_to(plugin_dir)
            archive.write(file_path, f"{package_root}/{relative.as_posix()}")

    digest = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    return archive_path, digest


def update_index(plugin_id: str, version: str, digest: str, asset_name: str, repo: str, release_tag: str) -> None:
    payload = load_json(INDEX_PATH)
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        fail("plugins-index.json must contain a top-level 'plugins' array")

    entry = next((item for item in plugins if isinstance(item, dict) and item.get("id") == plugin_id), None)
    if entry is None:
        fail(f"plugins-index.json does not contain official plugin id {plugin_id!r}")

    entry["version"] = version
    entry["download_url"] = f"https://github.com/{repo}/releases/download/{release_tag}/{asset_name}"
    entry["sha256"] = digest
    dump_json(INDEX_PATH, payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Package a NebulaLab official plugin release zip.")
    parser.add_argument("plugin", help="Official plugin folder name or plugin.json id.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="GitHub repo used for download_url.")
    parser.add_argument("--release-tag", default=DEFAULT_RELEASE_TAG)
    parser.add_argument("--update-index", action="store_true", help="Update plugins-index.json for this plugin.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    plugin_dir = discover_plugin_dir(args.plugin)
    manifest = load_json(plugin_dir / "plugin.json")
    plugin_id = manifest["id"]
    version = manifest["version"]

    archive_path, digest = build_zip(plugin_dir, args.output_dir)
    if args.update_index:
        update_index(plugin_id, version, digest, archive_path.name, args.repo, args.release_tag)

    print(json.dumps({
        "plugin_id": plugin_id,
        "version": version,
        "archive": str(archive_path),
        "sha256": digest,
        "upload_command": f"gh release upload {args.release_tag} {archive_path} --repo {args.repo} --clobber",
        "index_updated": bool(args.update_index),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
