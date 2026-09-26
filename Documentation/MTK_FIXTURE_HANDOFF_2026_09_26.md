# VREF preview3: concrete MTK migration fixtures

Prepared only; package operation selection awaits the actual MTK contract. No MTK repository write, commit, push or release. The existing manifest remains NO-GO and must not be published.

## Files and reproduction

Generator: `tools/prepare_mtk_fixtures.py`.
Oracle validation: `tests/test_mtk_fixtures.py`.
Local generated inputs and expected outputs: `artifacts/mtk-preview3-fixtures/fixtures.json`, with content-addressed files in its sibling `blobs/` directory. These contain complete original upstream scripts and remain ignored/private, not redistribution payloads.

Run `python3 tools/prepare_mtk_fixtures.py` to regenerate (optional --upstream and --output). Run `python3 -m unittest discover -s tests -v` for the fixture checks plus the prior standalone/XLua suite.

## 52 cases / two original script paths

For each `B738.calc` and `B738.a_fms`:
- `fresh`: original -> current -> original on removal.
- `current-repeat`: current -> exact no-op -> original on removal.
- `preview1-upgrade` and `preview2-upgrade`: known owned old state -> current -> original.
- `preview1-composed-upgrade` and `preview2-composed-upgrade`: known old installation plus independent edits both before the script and inside a relevant function -> current with those edits -> unpatched baseline with those edits.
- For old preview2 and current blocks, every owned hook has modified-content, duplicate, missing-begin and missing-end cases. All must block before any script, module or persistent ownership state is changed.

Preview1 and preview2 have the same loader text but different table module bytes; the fixtures keep those exact module bytes separately. This matters for payload-copy ownership/upgrade tests. The historical preview2 source is commit 5625655572f6899551c0bce115316bbd157878d5; its tag is unavailable locally.

## Machine-readable contract

Each case contains:
- `scriptPath`, `modulePath`: aircraft-relative install targets.
- `input`: actual current source bytes at update time.
- `previousInstalled`: bytes matching the last owned installation before any independent change; null on fresh install.
- `recordedOriginal`: old clean baseline recorded by the prior installation; null on fresh install.
- `expected`: exact script bytes after successful install/update; null for blocked cases.
- `expectedRestore`: exact script bytes after successful restore/removal; null for blocked cases. For composed cases this intentionally differs from `recordedOriginal`.
- `moduleBefore`, `moduleAfter`: exact old/current module bytes; null means absent (or no successful update for blocked cases). Successful full removal expects module absence.
- `mustBlockWithoutAnyWrites`: includes no module replacement and no state/backup transaction commit.

Every file descriptor has relative path, SHA-256 and byte size. Resolve paths relative to fixtures.json. Source uses its original per-file EOL. Import both script cases as a joint package transaction for all-or-nothing checks, not only per-file handler tests.

`markerContracts` provides each hook's current body, exact accepted legacy bodies, markers, anchor and restoration lines. This is semantic fixture data, not an agreed MTK JSON schema or operation ID. The CALC_WEIGHT hook is a replacement: its removal must restore the original call line. Other hooks are insertions and remove to no body. The unchanged non-loader blocks also need validation before any writes; guarding only the loaders is insufficient for the requested modified/duplicate/partial rejection.

## End-to-end acceptance still required

Consume the fixtures through real package parsing, planning, mutation, state persistence, repeat and Restore; assert actual complete scripts/modules and expected transaction behavior. For composed cases verify that a second ordinary update does not reconstruct from a stale baseline and discard retained changes. Old MTK versions must reject the versioned operation before file mutation. Preserve the original .35 XLua loading check as a separate downstream proof.

Current oracle checks only prove fixture integrity and owned-block removal equivalence. They do not prove MTK implementation correctness. Production metadata will switch only once the MTK operation ID, fields, version gate and Restore ownership semantics are supplied. Then rerun the complete MTK path and independently review the final VREF diff before publication.
