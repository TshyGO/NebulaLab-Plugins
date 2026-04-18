from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = ROOT / "themes-index.json"
ID_PATTERN = re.compile(r"^[a-z0-9_-]+$")
SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
ALLOWED_COLOR_SCHEMES = {"light", "dark"}
ALLOWED_SOURCES = {"official", "community"}
SHA256_PATTERN = re.compile(r"^[a-f0-9]{64}$")


def fail(message: str) -> None:
    print(message)
    raise SystemExit(1)


def is_http_url(value: str) -> bool:
    return value.startswith("https://") or value.startswith("http://")


def main() -> None:
    try:
        payload = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"ERROR: Missing file: {INDEX_PATH}")
    except json.JSONDecodeError as exc:
        fail(f"ERROR: themes-index.json is not valid JSON: {exc}")

    if not isinstance(payload, dict):
        fail("ERROR: themes-index.json top-level value must be an object")

    themes = payload.get("themes")
    if not isinstance(themes, list):
        fail("ERROR: themes-index.json must contain a top-level 'themes' array")

    errors: list[str] = []
    for index, item in enumerate(themes):
        label = f"themes[{index}]"
        if not isinstance(item, dict):
            errors.append(f"ERROR: {label} must be an object")
            continue

        theme_id = item.get("id")
        if not isinstance(theme_id, str) or not theme_id:
            errors.append(f"ERROR: {label}.id must be a non-empty string")
        elif not ID_PATTERN.fullmatch(theme_id):
            errors.append(f"ERROR: {label}.id '{theme_id}' must match ^[a-z0-9_-]+$")

        name = item.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"ERROR: {label}.name must be a non-empty string")

        version = item.get("version")
        if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
            errors.append(f"ERROR: {label}.version must match semver x.y.z")

        author = item.get("author")
        if not isinstance(author, str) or not author.strip():
            errors.append(f"ERROR: {label}.author must be a non-empty string")

        source = item.get("source")
        if not isinstance(source, str) or source not in ALLOWED_SOURCES:
            errors.append(f"ERROR: {label}.source must be one of: official, community")

        description = item.get("description")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"ERROR: {label}.description must be a non-empty string")

        color_scheme = item.get("color_scheme")
        if not isinstance(color_scheme, str) or color_scheme not in ALLOWED_COLOR_SCHEMES:
            errors.append(f"ERROR: {label}.color_scheme must be 'light' or 'dark'")

        download_url = item.get("download_url")
        if not isinstance(download_url, str) or not download_url.strip():
            errors.append(f"ERROR: {label}.download_url must be a non-empty string")
        elif not download_url.startswith("https://"):
            errors.append(f"ERROR: {label}.download_url must start with https://")

        sha256 = item.get("sha256")
        if not isinstance(sha256, str) or not SHA256_PATTERN.fullmatch(sha256.lower()):
            errors.append(f"ERROR: {label}.sha256 must be a 64-character lowercase hex string")

        homepage = item.get("homepage")
        if not isinstance(homepage, str) or not homepage.strip():
            errors.append(f"ERROR: {label}.homepage must be a non-empty string")
        elif not homepage.startswith("https://"):
            errors.append(f"ERROR: {label}.homepage must start with https://")

        preview_image_url = item.get("preview_image_url")
        if not isinstance(preview_image_url, str) or not preview_image_url.strip():
            errors.append(f"ERROR: {label}.preview_image_url must be a non-empty string")
        elif not preview_image_url.startswith("https://"):
            errors.append(f"ERROR: {label}.preview_image_url must start with https://")

        min_app_version = item.get("min_app_version")
        if not isinstance(min_app_version, str) or not SEMVER_PATTERN.fullmatch(min_app_version):
            errors.append(f"ERROR: {label}.min_app_version must match semver x.y.z")

        tags = item.get("tags")
        if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag.strip() for tag in tags):
            errors.append(f"ERROR: {label}.tags must be a non-empty string array")

        background_image_url = item.get("background_image_url")
        if background_image_url is not None:
            if not isinstance(background_image_url, str) or not background_image_url.strip():
                errors.append(f"ERROR: {label}.background_image_url must be a non-empty string when provided")
            elif not is_http_url(background_image_url):
                errors.append(f"ERROR: {label}.background_image_url must start with http:// or https://")

        accessibility_notes = item.get("accessibility_notes")
        if not isinstance(accessibility_notes, str) or not accessibility_notes.strip():
            errors.append(f"ERROR: {label}.accessibility_notes must be a non-empty string")

    if errors:
        for error in errors:
            print(error)
        raise SystemExit(1)

    print("themes-index.json validation passed")


if __name__ == "__main__":
    main()
