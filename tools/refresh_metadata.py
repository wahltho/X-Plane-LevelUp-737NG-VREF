#!/usr/bin/env python3
"""Regenerate declarative MTK payloads and integrity metadata from the hook spec.

Does not execute Lua, the installer, MTK, tests or archive publication.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(relative, document):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def metadata(relative):
    data = (ROOT / relative).read_bytes()
    return {"path": relative, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    spec = json.loads((ROOT / "patch-spec.json").read_text())
    manifest = json.loads((ROOT / "package-manifest.json").read_text())
    manifest["packageVersion"] = spec["version"].removeprefix("v")
    manifest["aircraftFamily"] = "Zibo B737-800X and LevelUp 737NG Series for X-Plane 12"
    manifest["supportedProducts"] = ["zibo-737ng", "levelup-737ng"]
    payloads = [metadata("payload/B738.levelup_vref.lua")]
    targets = []
    for target in spec["targets"]:
        relative = "patches/" + Path(target["path"]).name + ".json"
        replacements = []
        for edit in target["edits"]:
            prefix = [edit["anchor"]] if edit["mode"] == "after" else []
            replacements.append({
                "name": edit["id"], "oldLines": [edit["anchor"]],
                "newLines": prefix + edit["block"],
            })
        write(relative, {"format": "exact-text-replacements-v1", "replacements": replacements})
        payloads.append(metadata(relative))
        targets.extend([
            {"operation": "copy-file-v1", "payload": payloads[0]["path"],
             "relativePath": (Path(target["path"]).parent / "B738.levelup_vref.lua").as_posix(),
             "sourceSha256": spec.get("legacyPayloadSha256", []), "resultSha256": payloads[0]["sha256"]},
            {"operation": "exact-text-replacements-v1", "payload": relative,
             "relativePath": target["path"], "sourceSha256": []},
        ])
    manifest["modules"][0]["payloads"] = payloads
    manifest["modules"][0]["targets"] = targets
    manifest["modules"][0]["description"] = (
        "FCOM landing VREF for native Zibo and LevelUp, including separate 900ER data; "
        "preserves the compiled VNAV maneuver reference.")
    write("package-manifest.json", manifest)
    # The catalog snapshot remains a review artifact; never update the live MTK repository.
    entry = json.loads((ROOT / "catalog/package-entry.json").read_text())
    entry["supportedProducts"] = manifest["supportedProducts"]
    entry["description"] = "FCOM landing-reference speeds for Zibo and LevelUp 737NG, including separate 900ER data. Validation pending."
    write("catalog/package-entry.json", entry)
    member = json.loads((ROOT / "catalog/group-member.json").read_text())
    catalog = json.loads((ROOT / "catalog/content-package-catalog.preview.json").read_text())
    for index, package in enumerate(catalog["packages"]):
        if package["packageId"] == manifest["packageId"]:
            catalog["packages"][index] = entry
        if package["packageId"] in ("wahltho.levelup-737ng.maintenance", "wahltho.zibo-40535.maintenance"):
            package["members"] = [m for m in package["members"] if m["packageId"] != manifest["packageId"]] + [member]
            notice = " VREF tables are optional (prepared preview; validation pending)."
            if notice not in package["description"]:
                package["description"] += notice
    write("catalog/content-package-catalog.preview.json", catalog)
    files = ["z_Install.py", "patch-spec.json", "package-manifest.json", "tools/refresh_metadata.py"]
    files += [p["path"] for p in payloads]
    write("installer-manifest.json", {
        "schemaVersion": 1, "packageId": manifest["packageId"],
        "packageVersion": manifest["packageVersion"],
        "files": {p: {k: v for k, v in metadata(p).items() if k != "path"} for p in files},
    })
    print("Refreshed package metadata; no installation or tests executed.")


if __name__ == "__main__":
    main()
