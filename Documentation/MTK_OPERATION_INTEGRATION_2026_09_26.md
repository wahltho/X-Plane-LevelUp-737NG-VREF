# MTK operation integration — local preview3

Status: local handler and real MTK lifecycle tests PASS within the explicit fail-closed policy for independently changed managed files. Final coordinated publication remains gated. No MTK edits, commit, push or release.

## Implementation

Both loader payloads now use the supplied `migrate-marked-block-v1` operation, with exact legacy full blocks and current content lines. Lookup and FMC-display insertions use `insert-marked-block-v1`, so an independent comment between anchor and existing block does not cause reinsertion. CALC_WEIGHT uses exact replacement followed by an exact-current marker guard. All operations are planned before package writes. No table, numeric or runtime hook-body changes in this integration.

The initial handler run found duplicate CALC_LOOKUP insertion when an independent comment separated anchor and existing block. Switching non-loader insertions to marker identity fixed that source defect; the full handler fixture round then passed.

## Executed handler results

Unchanged local MTK Production handlers with actual generated package payloads: 12 valid install/upgrade cases and their repeat applications PASS; 40 manipulated/duplicate/partial marker cases correctly BLOCKED. These cover both complete original scripts and clean/preview1/preview2/composed states. The test links actual MTK handlers/codec/JSON utilities but does not execute planner, copy-file transaction, persisted state or Restore. Those end-to-end gates remain with MTK ownership work.

## Exact inputs for the MTK thread

Fixture manifest: `/Users/wahltho/Documents/Projects/X-Plane-LevelUp-737NG-VREF/artifacts/mtk-preview3-fixtures/fixtures.json`

Fixture manifest SHA-256: `1306ed6c1e6c4a339541131f8a611abb4b7c7f7c3ff3c6b5958c64b8e6d7b213`

Each descriptor below resolves to `artifacts/mtk-preview3-fixtures/blobs/<sha256>`; descriptor hashes and sizes are also in fixtures.json. For each composed case, seed recordedOriginal and previousInstalled, then run update on input. The expectedRestore MUST retain the independent edits and therefore differ from recordedOriginal.

| Case | Input | Expected update | Expected restore |
| --- | --- | --- | --- |
| B738.calc/preview1-composed-upgrade | 6089dec7e099218573ba0fb82fc8d682db13e47a2da6733fcdd86c00f4e1270c | 82892f6fd34feb4ec4610b6969681f50aa60d033a8f7ba9b3472a25ae9431e72 | 63bea29c8620d7842d524be3f3b673d5bcc65aaff229876a899908d495044101 |
| B738.calc/preview2-composed-upgrade | 6089dec7e099218573ba0fb82fc8d682db13e47a2da6733fcdd86c00f4e1270c | 82892f6fd34feb4ec4610b6969681f50aa60d033a8f7ba9b3472a25ae9431e72 | 63bea29c8620d7842d524be3f3b673d5bcc65aaff229876a899908d495044101 |
| B738.a_fms/preview1-composed-upgrade | 678d581eb890876d7cfcd68ac6c7adaef031e1abde136e38137b4d3c44e0b443 | 4f266afed5a14d20df9dc2e3d2b6745444c8aa2d6086002ca9a6ff06b89bf906 | a098766fb82ac9f2102a6bdf114256fdb055c4f617eeb47d7104aa80e0ae9ef7 |
| B738.a_fms/preview2-composed-upgrade | 678d581eb890876d7cfcd68ac6c7adaef031e1abde136e38137b4d3c44e0b443 | 4f266afed5a14d20df9dc2e3d2b6745444c8aa2d6086002ca9a6ff06b89bf906 | a098766fb82ac9f2102a6bdf114256fdb055c4f617eeb47d7104aa80e0ae9ef7 |

## Reviewed/tested source identities

- `/Users/wahltho/Documents/Projects/X-Plane-LevelUp-737NG-VREF/tools/refresh_metadata.py`: `90b716cf62fd3e7626c20ef7d0bb8160f6b8c34f488bc0f8f8ddc7c815922a03`
- `/Users/wahltho/Documents/Projects/X-Plane-LevelUp-737NG-VREF/package-manifest.json`: `121e0485b392ddddaf8e9a158bed48f8d726c994962fe8c3290bf8eed9993acf`
- `/Users/wahltho/Documents/Projects/X-Plane-LevelUp-737NG-VREF/patches/B738.calc.lua.loader.json`: `09165c5432d5af94ab8d65d39e76af5601d12735560f9ed4f665cf6b9a720088`
- `/Users/wahltho/Documents/Projects/X-Plane-LevelUp-737NG-VREF/patches/B738.a_fms.lua.loader.json`: `247f5615be52eef951f1ac0f3fc8cbc883a11d9b037698f954328dd38a118cb3`
- `/Users/wahltho/Documents/Projects/Level Up Nav Table Updater/src/LevelUp.NavTableUpdater.Core/Content/PatchHandlers/MarkedBlockMigrationPatchHandler.cs`: `8b8ba58882a231b29ea49deb251b085c51f73a3f152194fb9f112e6449c1c4a0`

## Real MTK transaction round (supersedes earlier handler-only limitation)

`tests/mtk_e2e/prepare_packages.py` builds/extracts the current archive and assembles historical preview1/2 packages from their actual Git manifests/payloads. `tests/mtk_e2e/E2E.csproj` references the current MTK Core project; separate build output paths avoid interfering with the MTK thread. Real CompatibilityPackageOperation executes package parsing, planning, file mutation, state persistence, repeat and Restore on private temporary aircraft with full original scripts.

- LevelUp fresh, preview1 upgrade, preview2 upgrade: PASS through repeat and Restore.
- Zibo fresh, preview2 upgrade: PASS through repeat and Restore. Preview1 did not support native Zibo, so no invented historical case.
- LevelUp preview1/preview2 and Zibo preview2 with independent managed-source edits: BLOCKED before mutation; complete aircraft/state/backup snapshots unchanged.
- 40 manipulated, duplicate or partial recognized-marker cases: BLOCKED at transaction level; complete snapshots unchanged.
- Successful installs verify both full scripts and both module payloads byte-for-byte; Restore verifies original scripts and module absence.
- Python suite rerun on final payloads: 9 methods PASS. No simulator test or publication.

The composed fixtures' expected transformation/restore bytes remain useful design oracles, but current transaction acceptance is explicitly BLOCK, not automatic migration. There is no proposed safe rebase based only on prior hashes/backups; preserving an edit cannot be proven from those records alone.

P2 review boundary: marker handlers recognize exact marker lines; this round does not prove rejection of arbitrary whitespace-disguised extra markers or relocated complete blocks. No exhaustive corruption-hardening claim.

## Final independent review

`/root/vref_full_review`: Source-GO within the restricted policy; no further blocking source findings. No reviewer-executed tests. Catalog-group combinations and simulator remain outside this proof.

Current MTK sources exercised in E2E (local dirty checkout):
- `/Users/wahltho/Documents/Projects/Level Up Nav Table Updater/src/LevelUp.NavTableUpdater.Core/Content/CompatibilityPackagePlanBuilder.cs`: `c381dccb99c64a7b68d26658feabaf34e5bf10696455e8474fc2d1e607a95497`
- `/Users/wahltho/Documents/Projects/Level Up Nav Table Updater/src/LevelUp.NavTableUpdater.Core/Content/ContentPatchEngine.cs`: `3fdc51a08b67b7b36cb8e998333bfff70aa7cc709f0f724ee8d9c70130080bc2`
- `/Users/wahltho/Documents/Projects/Level Up Nav Table Updater/src/LevelUp.NavTableUpdater.Core/Content/PatchHandlers/MarkedBlockMigrationPatchHandler.cs`: `8b8ba58882a231b29ea49deb251b085c51f73a3f152194fb9f112e6449c1c4a0`
