#!/usr/bin/env python3
"""Build a deterministic archive for both standalone and MTK installation."""

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def checked_file(relative, expected):
    path = ROOT / relative
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or linked package file: {relative}")
    data = path.read_bytes()
    if len(data) != expected["size"] or hashlib.sha256(data).hexdigest() != expected["sha256"]:
        raise ValueError(f"Package metadata does not match: {relative}")
    return data


def build(output):
    manifest_bytes = (ROOT / "package-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    installer = json.loads((ROOT / "installer-manifest.json").read_text())
    if manifest["schemaVersion"] != 3 or len(manifest["modules"]) != 1:
        raise ValueError("Unexpected MTK package schema")
    if installer["packageId"] != manifest["packageId"] or installer["packageVersion"] != manifest["packageVersion"]:
        raise ValueError("Standalone and MTK package identities differ")
    files = {name: checked_file(name, metadata) for name, metadata in installer["files"].items()}
    if files["package-manifest.json"] != manifest_bytes:
        raise ValueError("Manifest bytes differ")
    module = manifest["modules"][0]
    for payload in module["payloads"]:
        path = payload["path"]
        if files.get(path) != checked_file(path, payload):
            raise ValueError(f"Standalone and MTK payloads differ: {path}")
        files[f"modules/{module['moduleId']}/{path}"] = files[path]
    files["installer-manifest.json"] = (ROOT / "installer-manifest.json").read_bytes()
    for name in ("README.md", "RELEASE_NOTES.md", "LICENSE", "SUPPORT.md"):
        path = ROOT / name
        if path.is_file():
            files[name] = path.read_bytes()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w") as archive:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination ZIP path")
    print(build(parser.parse_args().output))
