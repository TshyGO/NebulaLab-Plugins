from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import PurePosixPath


ROOT = PurePosixPath(".")
PATTERNS = [
    re.compile(r"\bos\.system\s*\("),
    re.compile(r"\bsubprocess\.\w+\s*\("),
    re.compile(r"\beval\s*\("),
    re.compile(r"\bexec\s*\("),
    re.compile(r"__import__\s*\("),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_index() -> list[dict]:
    with open("plugins-index.json", "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    plugins = payload.get("plugins")
    if not isinstance(plugins, list):
        fail("plugins-index.json must contain a top-level 'plugins' array")
    return plugins


def download_bytes(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "NebulaLab-Market-Validator/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read()


def ensure_safe_members(archive: zipfile.ZipFile) -> None:
    for member in archive.infolist():
        path = PurePosixPath(member.filename)
        if path.is_absolute():
            fail(f"zip contains absolute path: {member.filename}")
        if any(part == ".." for part in path.parts):
            fail(f"zip contains path traversal entry: {member.filename}")


def detect_prefix(archive: zipfile.ZipFile) -> str:
    names = [PurePosixPath(info.filename) for info in archive.infolist() if not info.is_dir()]
    if not names:
        return ""
    first_parts = {path.parts[0] for path in names if path.parts}
    if len(first_parts) != 1:
        return ""
    first_part = next(iter(first_parts))
    if all(len(path.parts) >= 2 and path.parts[0] == first_part for path in names):
        return f"{first_part}/"
    return ""


def read_text_member(archive: zipfile.ZipFile, member_name: str) -> str:
    try:
        with archive.open(member_name) as fh:
            return fh.read().decode("utf-8")
    except KeyError as exc:
        fail(f"zip is missing required file: {member_name}")
        raise AssertionError from exc


def validate_plugin_asset(entry: dict) -> None:
    plugin_id = entry["id"]
    expected_sha = entry["sha256"].lower()
    raw = download_bytes(entry["download_url"])
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != expected_sha:
        fail(f"{plugin_id}: sha256 mismatch: expected {expected_sha}, got {actual_sha}")

    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile as exc:
        fail(f"{plugin_id}: release asset is not a valid zip file")
        raise AssertionError from exc

    with archive:
        ensure_safe_members(archive)
        prefix = detect_prefix(archive)
        plugin_meta = json.loads(read_text_member(archive, f"{prefix}plugin.json"))
        if plugin_meta.get("id") != plugin_id:
            fail(f"{plugin_id}: plugin.json id does not match index entry")
        if plugin_meta.get("version") != entry["version"]:
            fail(f"{plugin_id}: plugin.json version does not match index entry")

        has_operations = bool(plugin_meta.get("operations"))
        has_importers = bool(plugin_meta.get("importers"))
        panel_file = plugin_meta.get("panel")
        if has_operations or has_importers:
            read_text_member(archive, f"{prefix}__init__.py")
        if panel_file:
            if not isinstance(panel_file, str) or not panel_file.strip():
                fail(f"{plugin_id}: panel must be a non-empty string in plugin.json")
            if not panel_file.lower().endswith(".html"):
                fail(f"{plugin_id}: panel file must end with .html")
            read_text_member(archive, f"{prefix}{panel_file}")
        if not has_operations and not has_importers and not panel_file:
            fail(f"{plugin_id}: plugin must declare operations, importers, or panel")

        for info in archive.infolist():
            if info.is_dir() or not info.filename.endswith(".py"):
                continue
            source = read_text_member(archive, info.filename)
            for pattern in PATTERNS:
                if pattern.search(source):
                    fail(f"{plugin_id}: potentially dangerous pattern found in {info.filename}")


def main() -> None:
    for entry in load_index():
        validate_plugin_asset(entry)
    print("plugin release assets validation passed")


if __name__ == "__main__":
    main()
