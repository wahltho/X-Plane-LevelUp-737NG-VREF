"""Validate fixture oracles, not the MTK implementation that will consume them."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('fixture_builder', ROOT / 'tools/prepare_mtk_fixtures.py')
fixtures = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixtures)


class FixtureOracleTests(unittest.TestCase):
    def test_complete_cases_integrity_and_restore_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = fixtures.generate(root, fixtures.DEFAULT_UPSTREAM)
            targets = {item['path']: item for item in json.loads((ROOT / 'patch-spec.json').read_text())['targets']}
            self.assertEqual(len(manifest['cases']), 56)
            self.assertEqual(len({case['id'] for case in manifest['cases']}), 56)
            def read(descriptor):
                data = (root / descriptor['path']).read_bytes()
                self.assertEqual(len(data), descriptor['size'])
                self.assertEqual(hashlib.sha256(data).hexdigest(), descriptor['sha256'])
                return data
            successes = rejected = 0
            for case in manifest['cases']:
                with self.subTest(case=case['id']):
                    for field in ('input', 'expected', 'expectedRestore', 'recordedOriginal', 'previousInstalled', 'moduleBefore', 'moduleAfter'):
                        if case[field] is not None:
                            read(case[field])
                    source = read(case['input'])
                    target = targets[case['scriptPath']]
                    if case['mustBlockWithoutAnyWrites']:
                        rejected += 1
                        with self.assertRaises(ValueError):
                            fixtures.installer.strip_ours(fixtures.installer.normalized(source)[0], target['edits'])
                    else:
                        successes += 1
                        expected = read(case['expected'])
                        restored = read(case['expectedRestore'])
                        clean, eol = fixtures.installer.normalized(expected)
                        self.assertEqual(fixtures.installer.strip_ours(clean, target['edits']).replace(b'\n', eol), restored)
                        # Original and expected contain the same foreign bytes after owned blocks are removed.
                        clean_input, input_eol = fixtures.installer.normalized(source)
                        self.assertEqual(fixtures.installer.strip_ours(clean_input, target['edits']).replace(b'\n', input_eol), restored)
                        if 'composed' in case['id']:
                            self.assertIn(b'INSIDE function', expected)
                            self.assertIn(b'INSIDE function', restored)
                            self.assertNotEqual(read(case['recordedOriginal']), restored)
            self.assertEqual((successes, rejected), (16, 40))


if __name__ == '__main__':
    unittest.main()
