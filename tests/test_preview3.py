"""Focused tests against original .35 scripts; never touch installed aircraft."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sys

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = Path(os.environ.get('VREF_UPSTREAM_ROOT', '/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/B738X_XP12_4_05_35'))
LUA = os.environ.get('VREF_LUA51', '/Users/wahltho/dev/xlua2/build/luajit-upgrade-mac/luajit-c6ffc141a876/work/arm64/src/luajit')
spec = importlib.util.spec_from_file_location('vref_installer', ROOT / 'z_Install.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
SPEC = json.loads((ROOT / 'patch-spec.json').read_text())


def git_bytes(revision, path):
    return subprocess.check_output(['git', 'show', revision + ':' + path], cwd=ROOT)


class Preview3Tests(unittest.TestCase):
    def test_original_sources_fresh_repeat_restore_and_foreign_bytes(self):
        for target in SPEC['targets']:
            original = (ORIGINAL / target['path']).read_bytes()
            for eol in (b'\n', b'\r\n'):
                source = original.replace(b'\r\n', b'\n').replace(b'\n', eol)
                foreign = b'-- independent patch retained' + eol
                source = foreign + source
                with self.subTest(script=target['path'], eol=eol):
                    installed = installer.patch_source(source, target, False)
                    self.assertEqual(installer.patch_source(installed, target, False), installed)
                    self.assertEqual(installer.patch_source(installed, target, True), source)

    def test_known_released_upgrades_and_foreign_edit(self):
        for revision in ('v0.1.0-preview.1', '5625655572f6899551c0bce115316bbd157878d5'):
            old = json.loads(git_bytes(revision, 'patch-spec.json'))
            for target, previous in zip(SPEC['targets'], old['targets']):
                source = (ORIGINAL / target['path']).read_bytes()
                old_installed = installer.patch_source(source, previous, False)
                foreign = b'-- independently added after preview install' + installer.normalized(source)[1]
                for addition in (b'', foreign):
                    with self.subTest(revision=revision, script=target['path'], composed=bool(addition)):
                        updated = installer.patch_source(addition + old_installed, target, False)
                        self.assertEqual(updated, installer.patch_source(addition + source, target, False))
                        self.assertEqual(installer.patch_source(updated, target, True), addition + source)

    def test_reject_bad_blocks(self):
        for target in SPEC['targets']:
            source = (ORIGINAL / target['path']).read_bytes().replace(b'\r\n', b'\n')
            for legacy in (False, True):
                candidate = copy.deepcopy(target)
                if legacy:
                    candidate['edits'][0]['block'] = candidate['edits'][0]['legacyBlocks'][0]
                installed = installer.patch_source(source, candidate, False)
                for edit in candidate['edits']:
                    block = installer.block_bytes(edit)
                    faults = (
                        installed.replace(block, block + block, 1),
                        installed.replace(block, block.replace(b'-- package-version|', b'-- changed-version|', 1), 1),
                        installed.replace((edit['block'][-1] + '\n').encode(), b'', 1),
                        installed.replace((edit['block'][0] + '\n').encode(), b'', 1),
                    )
                    for index, broken in enumerate(faults):
                        with self.subTest(script=target['path'], legacy=legacy, hook=edit['id'], fault=index):
                            with self.assertRaises(ValueError):
                                installer.patch_source(broken, target, False)

    def test_failed_second_target_does_not_write_first(self):
        with tempfile.TemporaryDirectory() as directory:
            aircraft = Path(directory)
            snapshots = {}
            for target in SPEC['targets']:
                path = aircraft / target['path']
                path.parent.mkdir(parents=True)
                data = (ORIGINAL / target['path']).read_bytes()
                if 'a_fms' in target['path']:
                    data = data.replace(b'function B738_calc()', b'function B738_calc_changed()', 1)
                path.write_bytes(data)
                snapshots[path] = data
            with patch.object(sys, 'argv', ['z_Install.py', str(aircraft)]):
                with self.assertRaises(ValueError):
                    installer.main()
            for path, before in snapshots.items():
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse(path.with_name('B738.levelup_vref.lua').exists())
            self.assertFalse((aircraft / '.levelup-vref-backups').exists())

    def test_original_xlua_namespace_loader(self):
        # Execute original init.lua unchanged under LuaJIT's Lua 5.1 API.
        # XLuaGetCode is filesystem-backed; no simulator/dataref runtime is modeled.
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for index, target in enumerate(SPEC['targets']):
                for version, loader in [('current', target['edits'][0]['block']),
                                        ('legacy', target['edits'][0]['legacyBlocks'][0])]:
                    (folder / f'{index}-{version}.lua').write_text('\n'.join(loader) + '\nreturn levelup_vref\n')
            script = r'''
local init, root, fixtures = arg[1], arg[2], arg[3]
dofile(init)
function XLuaGetCode(name) return assert(loadfile(root .. '/payload/' .. name)) end
local function load_hook(index, version)
 local ns = create_namespace()
 ns.dofile = get_run_file_in_namespace(ns)
 ns.raw_table = get_raw_table_in_namespace(ns)
 local fn = assert(loadfile(fixtures .. '/' .. index .. '-' .. version .. '.lua'))
 setfenv(fn, ns)
 return fn(), ns
end
local first, ns1 = load_hook(0, 'current')
local second, ns2 = load_hook(1, 'current')
assert(first and second and first ~= second)
assert(ns1.B738_levelup_vref_module == first)
assert(ns2.B738_levelup_vref_module == second)
assert(_G.B738_levelup_vref_module == nil)
for _, api in ipairs({first, second}) do
 local r30, r40, r15 = api.calculate(140, 4)
 assert(r30 == 140 and r40 == 136 and r15 == 147)
 assert(api.calculate(0, 4) == nil and api.calculate(140, 5) == nil)
 assert(api.calculate(140, -1) == api.calculate(140, 0))
end
-- The released loader is demonstrably inactive even with a loadable payload.
assert(load_hook(0, 'legacy') == nil)
assert(load_hook(1, 'legacy') == nil)
-- A failed reload cannot inherit the previous API namespace slot.
local broken = assert(loadfile(fixtures .. '/0-current.lua'))
setfenv(broken, ns1)
function XLuaGetCode() error('injected read failure') end
assert(broken() == nil and ns1.B738_levelup_vref_module == nil)
print('Original XLua init + LuaJIT loader checks PASS (no simulator)')
'''
            (folder / 'loader.lua').write_text(script)
            result = subprocess.run([LUA, str(folder / 'loader.lua'), str(ORIGINAL / 'plugins/xlua/init.lua'), str(ROOT), str(folder)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            print(result.stdout.strip())


if __name__ == '__main__':
    unittest.main()
