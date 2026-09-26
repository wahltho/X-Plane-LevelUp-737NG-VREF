import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("vref_builder", ROOT / "tools/build_package.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
installer_spec = importlib.util.spec_from_file_location("vref_installer", ROOT / "z_Install.py")
installer = importlib.util.module_from_spec(installer_spec)
installer_spec.loader.exec_module(installer)


class PackageTests(unittest.TestCase):
    def test_standalone_and_mtk_payloads_are_identical(self):
        with tempfile.TemporaryDirectory() as temporary:
            archive = builder.build(Path(temporary) / "vref.zip")
            second = builder.build(Path(temporary) / "vref-again.zip")
            self.assertEqual(archive.read_bytes(), second.read_bytes())
            manifest = json.loads((ROOT / "package-manifest.json").read_text())
            installer = json.loads((ROOT / "installer-manifest.json").read_text())
            with zipfile.ZipFile(archive) as package:
                names = package.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertEqual(json.loads(package.read("package-manifest.json")), manifest)
                for path, expected in installer["files"].items():
                    data = package.read(path)
                    self.assertEqual(len(data), expected["size"])
                    self.assertEqual(hashlib.sha256(data).hexdigest(), expected["sha256"])
                for payload in manifest["modules"][0]["payloads"]:
                    path = payload["path"]
                    self.assertEqual(package.read(path), package.read(f"modules/vref/{path}"))
                self.assertEqual(package.read("installer-manifest.json"),
                                 (ROOT / "installer-manifest.json").read_bytes())

    def test_group_order_keeps_intentional_fixes_last(self):
        catalog = json.loads((ROOT / "catalog/content-package-catalog.preview.json").read_text())
        for package in catalog["packages"]:
            if package["packageId"] not in ("wahltho.levelup-737ng.maintenance", "wahltho.zibo-40535.maintenance"):
                continue
            orders = {member["moduleId"]: member["installationOrder"] for member in package["members"]}
            self.assertEqual(orders["vref"], 65)
            self.assertLess(orders["vref"], min(value for key, value in orders.items() if key.startswith("intentional-fixes")))

    def test_standalone_install_repeat_and_uninstall_preserve_source(self):
        sources = {
            "plugins/xlua/scripts/B738.calc/B738.calc.lua": (
                b"jit.off()\r\n"
                b"function vref30_40(in_gw)\r\n  return 100, 120\r\nend\r\n"
                b"function B738_calc_vref()\r\n  return 120\r\nend\r\n"
                b"function B738_calc_min_max_spd()\r\n"
                b"\tvref_30, vref_x = vref30_40(total_weight_t)\r\nend\r\n"
            ),
            "plugins/xlua/scripts/B738.a_fms/B738.a_fms.lua": (
                b"jit.off()\r\nfunction B738_calc()\r\n"
                b"\tvref_15 = string.format(\"%3d\", B738DR_fms_vref_15)\t-- + B738DR_fms_approach_wind_corr)\r\n"
                b"end\r\n"
            ),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = builder.build(root / "package.zip")
            package = root / "package"
            with zipfile.ZipFile(archive) as zipped:
                zipped.extractall(package)
            aircraft = root / "aircraft"
            for relative, source in sources.items():
                target = aircraft / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source)
            patch_spec_path = package / "patch-spec.json"
            patch_spec = json.loads(patch_spec_path.read_text())
            for target in patch_spec["targets"]:
                baseline = sources[target["path"]].replace(b"\r\n", b"\n")
                target["functions"] = {
                    name: installer.digest(installer.function_bytes(baseline, name))
                    for name in target["functions"]
                }
            patch_spec_path.write_text(json.dumps(patch_spec))
            integrity_path = package / "installer-manifest.json"
            integrity = json.loads(integrity_path.read_text())
            spec_bytes = patch_spec_path.read_bytes()
            integrity["files"]["patch-spec.json"] = {
                "size": len(spec_bytes), "sha256": installer.digest(spec_bytes)
            }
            integrity_path.write_text(json.dumps(integrity))
            with patch.object(installer, "PACKAGE", package), patch.object(sys, "argv", ["z_Install.py", str(aircraft)]):
                self.assertEqual(installer.main(), 0)
                installed = {relative: (aircraft / relative).read_bytes() for relative in sources}
                for relative, data in installed.items():
                    self.assertEqual(data.count(b"-- BEGIN LEVELUP_VREF"), 3 if "B738.calc" in relative else 2)
                    self.assertEqual(data.count(b"\n"), data.count(b"\r\n"))
                self.assertEqual(installer.main(), 0)
                self.assertEqual(installed, {relative: (aircraft / relative).read_bytes() for relative in sources})
                with patch.object(sys, "argv", ["z_Install.py", str(aircraft), "--uninstall"]):
                    self.assertEqual(installer.main(), 0)
            for relative, source in sources.items():
                self.assertEqual((aircraft / relative).read_bytes(), source)
                self.assertFalse((aircraft / relative).with_name("B738.levelup_vref.lua").exists())


if __name__ == "__main__":
    unittest.main()
