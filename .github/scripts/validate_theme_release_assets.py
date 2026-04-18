from __future__ import annotations

import hashlib
import io
import json
import urllib.request
import zipfile
from pathlib import PurePosixPath


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def load_index() -> list[dict]:
    with open("themes-index.json", "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    themes = payload.get("themes")
    if not isinstance(themes, list):
        fail("themes-index.json must contain a top-level 'themes' array")
    return themes


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


def validate_theme_asset(entry: dict) -> None:
    theme_id = entry["id"]
    expected_sha = entry["sha256"].lower()
    raw = download_bytes(entry["download_url"])
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != expected_sha:
        fail(f"{theme_id}: sha256 mismatch: expected {expected_sha}, got {actual_sha}")

    try:
        archive = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile as exc:
        fail(f"{theme_id}: release asset is not a valid zip file")
        raise AssertionError from exc

    with archive:
        ensure_safe_members(archive)
        prefix = detect_prefix(archive)
        theme_meta = json.loads(read_text_member(archive, f"{prefix}theme.json"))
        if theme_meta.get("id") != theme_id:
            fail(f"{theme_id}: theme.json id does not match index entry")
        if theme_meta.get("version") != entry["version"]:
            fail(f"{theme_id}: theme.json version does not match index entry")
        if theme_meta.get("color_scheme") != entry["color_scheme"]:
            fail(f"{theme_id}: theme.json color_scheme does not match index entry")
        if theme_meta.get("background_image_url") != entry.get("background_image_url"):
            fail(f"{theme_id}: theme.json background_image_url does not match index entry")


def main() -> None:
    for entry in load_index():
        validate_theme_asset(entry)
    print("theme release assets validation passed")


if __name__ == "__main__":
    main()
