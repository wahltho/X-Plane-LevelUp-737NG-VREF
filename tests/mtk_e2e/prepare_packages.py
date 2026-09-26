import importlib.util
import json
from pathlib import Path
import subprocess
import zipfile
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/mtk-e2e-packages'
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location('builder', ROOT / 'tools/build_package.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
with zipfile.ZipFile(builder.build(OUT / 'current.zip')) as archive:
    archive.extractall(OUT / 'current')
for label, revision in [('preview1', 'v0.1.0-preview.1'), ('preview2', '5625655572f6899551c0bce115316bbd157878d5')]:
    def git(path): return subprocess.check_output(['git','show',revision+':'+path],cwd=ROOT)
    raw = git('package-manifest.json')
    manifest = json.loads(raw)
    directory = OUT / label
    directory.mkdir(exist_ok=True)
    (directory / 'package-manifest.json').write_bytes(raw)
    for module in manifest['modules']:
        for payload in module['payloads']:
            path = directory / 'modules' / module['moduleId'] / payload['path']
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(git(payload['path']))
print(OUT)
