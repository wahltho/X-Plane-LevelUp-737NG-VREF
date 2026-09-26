#!/usr/bin/env python3
"""Prepare/restore marked LevelUp VREF hooks; never replace whole upstream scripts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(data: bytes) -> tuple[bytes, bytes]:
    crlf = data.count(b"\r\n")
    if crlf and data.count(b"\n") != crlf:
        raise ValueError("Mixed line endings: refusing to normalize user content")
    clean = data.replace(b"\r\n", b"\n")
    if b"\r" in clean:
        raise ValueError("Unsupported CR-only line ending")
    return clean, b"\r\n" if crlf else b"\n"


def function_bytes(source: bytes, name: str) -> bytes:
    anchor = ("function " + name + "(").encode("ascii")
    starts = [i for i, line in enumerate(source.splitlines(keepends=True))
              if line.startswith(anchor)]
    if len(starts) != 1:
        raise ValueError("Missing/ambiguous function: " + name)
    lines = source.splitlines(keepends=True)
    start = starts[0]
    end = next((i for i in range(start + 1, len(lines))
                if lines[i].startswith(b"function ")), len(lines))
    return b"".join(lines[start:end])


def block_bytes(edit: dict) -> bytes:
    return ("\n".join(edit["block"]) + "\n").encode("ascii")


def strip_ours(source: bytes, edits: list[dict]) -> bytes:
    for edit in edits:
        block = block_bytes(edit)
        begin, end = edit["block"][0].encode(), edit["block"][-1].encode()
        counts = source.count(begin), source.count(end)
        if counts == (0, 0):
            continue
        if counts != (1, 1) or source.count(block) != 1:
            raise ValueError("Modified/duplicate/incomplete VREF block: " + edit["id"])
        restore = (edit["anchor"] + "\n").encode("ascii") if edit["mode"] == "replace" else b""
        source = source.replace(block, restore, 1)
    if b"LEVELUP_VREF" in source:
        raise ValueError("Unknown VREF markers remain; refusing mixed package versions")
    return source


def patch_source(source: bytes, target: dict, uninstall: bool) -> bytes:
    source, eol = normalized(source)
    source = strip_ours(source, target["edits"])
    for name, expected in target["functions"].items():
        if digest(function_bytes(source, name)) != expected:
            raise ValueError("Unsupported or modified upstream function: " + name)
    if not uninstall:
        for edit in target["edits"]:
            anchor = (edit["anchor"] + "\n").encode("ascii")
            # Exact complete lines, never substring matches or commented lookalikes.
            lines = source.splitlines(keepends=True)
            indices = [i for i, line in enumerate(lines) if line == anchor]
            if len(indices) != 1:
                raise ValueError("Missing/ambiguous patch anchor: " + edit["id"])
            replacement = block_bytes(edit)
            if edit["mode"] == "after":
                replacement = anchor + replacement
            lines[indices[0]] = replacement
            source = b"".join(lines)
    return source.replace(b"\n", eol)


def atomic_write(path: Path, data: bytes, mode: int = 0o644) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".levelup-vref-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("aircraft", type=Path, help="LevelUp aircraft root (not the scripts directory)")
    parser.add_argument("--uninstall", action="store_true", help="Remove only this package's known marked hooks")
    args = parser.parse_args()
    root = args.aircraft.resolve(strict=True)
    manifest = json.loads((PACKAGE / "installer-manifest.json").read_text(encoding="utf-8"))
    for relative, expected in manifest["files"].items():
        data = (PACKAGE / relative).read_bytes()
        if digest(data) != expected["sha256"] or len(data) != expected["size"]:
            raise ValueError("Package integrity mismatch: " + relative)
    spec = json.loads((PACKAGE / "patch-spec.json").read_text(encoding="utf-8"))
    module = (PACKAGE / "payload/B738.levelup_vref.lua").read_bytes()
    # Plan every target and payload before creating backups or changing the aircraft.
    changes: list[tuple[Path, bytes | None, bytes | None, int]] = []
    for target in spec["targets"]:
        path = root / target["path"]
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Missing/unsafe aircraft script: " + str(path))
        old = path.read_bytes()
        new = patch_source(old, target, args.uninstall)
        if new != old:
            changes.append((path, old, new, path.stat().st_mode & 0o777))
        payload = path.parent / "B738.levelup_vref.lua"
        if payload.is_symlink():
            raise ValueError("Refusing symlink payload: " + str(payload))
        previous = payload.read_bytes() if payload.exists() else None
        if previous is not None and previous != module:
            raise ValueError("Different existing VREF payload; refusing overwrite: " + str(payload))
        desired = None if args.uninstall else module
        if previous != desired:
            changes.append((payload, previous, desired, payload.stat().st_mode & 0o777 if previous is not None else 0o644))
    if not changes:
        print("No changes needed.")
        return 0
    backup_root = root / ".levelup-vref-backups"
    if backup_root.is_symlink():
        raise ValueError("Refusing symlink backup directory")
    for path, old, _, _ in changes:
        if old is not None:
            backup = backup_root / digest(old) / path.relative_to(root)
            backup.parent.mkdir(parents=True, exist_ok=True)
            if backup.exists():
                if backup.read_bytes() != old:
                    raise ValueError("Backup collision: " + str(backup))
            else:
                atomic_write(backup, old)
    # Stop X-Plane first. Detect edits made after planning before the first write.
    for path, old, _, _ in changes:
        current = path.read_bytes() if path.exists() else None
        if current != old:
            raise ValueError("Target changed during preparation: " + str(path))
    applied = []
    try:
        # Payload files precede script hooks on install; hooks precede removal on uninstall.
        ordered = sorted(changes, key=lambda item: (item[0].name != "B738.levelup_vref.lua") != args.uninstall)
        for path, old, new, mode in ordered:
            if new is None:
                path.unlink()
            else:
                atomic_write(path, new, mode)
            applied.append((path, old, mode))
    except Exception:
        errors = []
        for path, old, mode in reversed(applied):
            try:
                if old is None:
                    path.unlink(missing_ok=True)
                else:
                    atomic_write(path, old, mode)
            except Exception as error:
                errors.append(str(error))
        if errors:
            print("ROLLBACK INCOMPLETE; restore from " + str(backup_root) + ": " + "; ".join(errors), file=sys.stderr)
        raise
    print(("Removed" if args.uninstall else "Installed") + " LevelUp VREF hooks; restart X-Plane.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as error:
        print("ERROR: " + str(error), file=sys.stderr)
        raise SystemExit(1)
