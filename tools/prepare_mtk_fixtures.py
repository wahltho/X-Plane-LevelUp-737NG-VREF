#!/usr/bin/env python3
"""Generate private full-source VREF migration fixtures; no aircraft/MTK writes."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location('vref_installer', ROOT / 'z_Install.py')
installer = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(installer)
DEFAULT_UPSTREAM = Path('/Users/wahltho/dev/Zibo Mod/Original/Zibo Mod Original/B738X_XP12_4_05_35')
VERSIONS = {'preview1': 'v0.1.0-preview.1', 'preview2': '5625655572f6899551c0bce115316bbd157878d5'}


def historical(revision, path):
    return subprocess.check_output(['git', 'show', revision + ':' + path], cwd=ROOT)


def generate(destination, upstream):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    spec = json.loads((ROOT / 'patch-spec.json').read_text())
    old_specs = {label: json.loads(historical(rev, 'patch-spec.json')) for label, rev in VERSIONS.items()}
    def blob(data):
        sha = hashlib.sha256(data).hexdigest()
        relative = 'blobs/' + sha
        path = destination / relative
        path.parent.mkdir(exist_ok=True)
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Fixture content-address collision')
        if not path.exists():
            path.write_bytes(data)
        return {'path': relative, 'sha256': sha, 'size': len(data)}
    current_module = blob((ROOT / 'payload/B738.levelup_vref.lua').read_bytes())
    old_modules = {label: blob(historical(rev, 'payload/B738.levelup_vref.lua')) for label, rev in VERSIONS.items()}
    cases = []
    contracts = []
    for i, target in enumerate(spec['targets']):
        clean = (upstream / target['path']).read_bytes()
        eol = installer.normalized(clean)[1]
        # Inside the first guarded function as well as before all VREF hooks.
        function_anchor = ('function ' + next(iter(target['functions'])) + '(').encode()
        def foreign(data):
            lines = data.splitlines(keepends=True)
            pos = next(j for j, line in enumerate(lines) if line.startswith(function_anchor))
            lines.insert(pos + 1, b'    -- independent MTK fixture edit INSIDE function' + eol)
            return b'-- independent MTK fixture edit BEFORE script' + eol + b''.join(lines)
        current = installer.patch_source(clean, target, False)
        base_id = Path(target['path']).parent.name
        def add(label, source, expected, restore, previous=None, module_before=None):
            cases.append({'id': base_id + '/' + label, 'scriptPath': target['path'],
                'modulePath': str(Path(target['path']).with_name('B738.levelup_vref.lua')),
                'input': blob(source), 'expected': blob(expected) if expected is not None else None,
                'expectedRestore': blob(restore) if restore is not None else None,
                'recordedOriginal': blob(clean) if previous is not None else None,
                'previousInstalled': blob(previous) if previous is not None else None,
                'moduleBefore': module_before, 'moduleAfter': current_module if expected is not None else None,
                'moduleAfterRestore': None,
                'mustBlockWithoutAnyWrites': expected is None})
        add('fresh', clean, current, clean)
        add('current-repeat', current, current, clean, current, current_module)
        for label, old_spec in old_specs.items():
            old = installer.patch_source(clean, old_spec['targets'][i], False)
            add(label + '-upgrade', old, current, clean, old, old_modules[label])
            add(label + '-composed-upgrade', foreign(old), foreign(current), foreign(clean), old, old_modules[label])
        # Guard every owned block, including unchanged non-loader blocks.
        for label, installed, target_spec, module_before in [
            ('preview2', installer.patch_source(clean, old_specs['preview2']['targets'][i], False), old_specs['preview2']['targets'][i], old_modules['preview2']),
            ('current', current, target, current_module)]:
            for edit in target_spec['edits']:
                block = installer.block_bytes(edit).replace(b'\n', eol)
                faults = {
                    'modified': installed.replace(block, block.replace(b'-- package-version|', b'-- modified-version|', 1), 1),
                    'duplicate': installed.replace(block, block + block, 1),
                    'missing-begin': installed.replace(edit['block'][0].encode() + eol, b'', 1),
                    'missing-end': installed.replace(edit['block'][-1].encode() + eol, b'', 1),
                }
                for fault, broken in faults.items():
                    add(label + '-' + edit['id'] + '-' + fault, broken, None, None, installed, module_before)
        contracts.append({'scriptPath': target['path'], 'edits': [
            {'id': edit['id'], 'mode': edit['mode'], 'anchorLines': [edit['anchor']],
             'beginMarker': edit['block'][0], 'endMarker': edit['block'][-1],
             'currentContentLines': edit['block'][1:-1],
             'legacyContentLines': [block[1:-1] for block in edit.get('legacyBlocks', [])],
             'restoreLines': [edit['anchor']] if edit['mode'] == 'replace' else []}
            for edit in target['edits']]})
    manifest = {'fixtureSchema': 1, 'packageVersion': spec['version'],
        'patchSpecSha256': hashlib.sha256((ROOT / 'patch-spec.json').read_bytes()).hexdigest(),
        'historicalRefs': VERSIONS, 'sourceKind': 'complete original .35 scripts, native line endings',
        'note': 'Expected states only; no MTK API field names or operation ID are agreed by this fixture.',
        'markerContracts': contracts, 'cases': cases}
    (destination / 'fixtures.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'{len(cases)} cases: {destination / "fixtures.json"}')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/mtk-preview3-fixtures')
    parser.add_argument('--upstream', type=Path, default=DEFAULT_UPSTREAM)
    args = parser.parse_args()
    generate(args.output, args.upstream)
