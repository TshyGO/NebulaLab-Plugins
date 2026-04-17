from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "plugins-index.json"
ID_PATTERN = re.compile(r"^[a-z0-9_-]+$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
ALLOWED_SOURCES = {"official", "community"}
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def main() -> None:
    try:
        payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"ERROR: Missing file: {INDEX_PATH}")
    except json.JSONDecodeError as exc:
        fail(f"ERROR: plugins-index.json is not valid JSON: {exc}")

    if not isinstance(payload, dict):
        fail("ERROR: plugins-index.json top-level value must be an object")

    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        fail("ERROR: plugins-index.json must contain a top-level 'plugins' array")

    errors: list[str] = []
    for index, item in enumerate(plugins):
        label = f"plugins[{index}]"
        if not isinstance(item, dict):
            errors.append(f"ERROR: {label} must be an object")
            continue

        plugin_id = item.get("id")
        if not isinstance(plugin_id, str) or not plugin_id:
            errors.append(f"ERROR: {label}.id must be a non-empty string")
        elif not ID_PATTERN.fullmatch(plugin_id):
            errors.append(f"ERROR: {label}.id '{plugin_id}' must match ^[a-z0-9_-]+$")

        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"ERROR: {label}.name must be a non-empty string")

        version = item.get("version")
        if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
            errors.append(f"ERROR: {label}.version must match semver x.y.z")

        download_url = item.get("download_url")
        if not isinstance(download_url, str) or not download_url.strip():
            errors.append(f"ERROR: {label}.download_url must be a non-empty string")
        elif not download_url.startswith("https://"):
            errors.append(f"ERROR: {label}.download_url must start with https://")

        source = item.get("source")
        if not isinstance(source, str) or source not in ALLOWED_SOURCES:
            errors.append(f"ERROR: {label}.source must be one of: official, community")

        homepage = item.get("homepage")
        if not isinstance(homepage, str) or not homepage.strip():
            errors.append(f"ERROR: {label}.homepage must be a non-empty string")
        elif not homepage.startswith("https://"):
            errors.append(f"ERROR: {label}.homepage must start with https://")

        sha256 = item.get("sha256")
        if not isinstance(sha256, str) or not SHA256_PATTERN.fullmatch(sha256.lower()):
            errors.append(f"ERROR: {label}.sha256 must be a 64-character lowercase hex string")

        if source == "community":
            source_url = item.get("source_url")
            if not isinstance(source_url, str) or not source_url.strip():
                errors.append(f"ERROR: {label}.source_url is required for community plugins")
            elif not source_url.startswith("https://"):
                errors.append(f"ERROR: {label}.source_url must start with https://")

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print("plugins-index.json validation passed")


if __name__ == "__main__":
    main()
