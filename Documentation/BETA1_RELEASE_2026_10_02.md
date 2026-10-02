# VREF Beta1 release — 2026-10-02

## Scope and approval

User requested promotion of Preview to Beta and MTK-compatible publication, then explicitly assigned the live catalog update to the MTK thread after the patch release. This task publishes **v0.1.0-beta.1** in the existing public repository. It does not modify or publish the MTK catalog or application.

The reviewed Preview3 runtime is unchanged: `payload/B738.levelup_vref.lua`, all `patches/` payloads, every hook block/function fingerprint in `patch-spec.json`, and `z_Install.py` are byte-identical to tag `v0.1.0-preview.3`. The package version, documentation and candidate catalog display metadata are changed. Module/private hook revisions intentionally retain Preview3/earlier markers to preserve exact migration identity. Beta is a distribution status; no new numeric behavior or simulator proof is claimed.

## MTK delivery contract

Native schema3 compatibility archive, package ID `wahltho.levelup-737ng.vref`, module `vref`, products `zibo-737ng` and `levelup-737ng`, optional/defaultEnabled=false, installation order65 before Intentional Fixes70. Minimum managed installer is **0.21.2** for `migrate-marked-block-v1`; the MTK thread must raise the live catalog minimum to at least that version when adding this source. Current E2E ran against MTK main `75450f5c0fe189b756eccb1f28e18c5936ca2c1b`.

MTK `GitHubContentPatchReleaseSource.GetLatestAsync` uses `releases/latest` and rejects GitHub `prerelease=true`. To use the existing tested engine, this explicit Beta uses a **regular GitHub Release**, with Beta in its tag/title/catalog name. This is a technical discovery flag, not a Stable flight-validation claim. The catalog entry remains optional. No client change or new beta-channel implementation is introduced.

## Verification

- Python unittest discovery: **9 methods PASS**, including original XLua init/LuaJIT loader, standalone install/repeat/uninstall and generated fixture integrity.
- Extended fixture generator adds exact Preview3 upgrade/composed cases to the existing surface: **56 cases**,16 valid transformation/oracle cases and40 malformed-marker cases.
- Actual current MTK `CompatibilityPackageOperation`: **7 lifecycle scenarios PASS** (LevelUp fresh/Preview1/2/3; Zibo fresh/Preview2/3), each through repeat and full Restore.
- **5 independently changed managed states BLOCKED** before mutation; complete aircraft/state/backup snapshots unchanged.
- **40 corrupted-marker transactions BLOCKED** with unchanged aircraft/state/backup bytes.
- Runtime/payload diff against the independently reviewed Preview3 tag: empty; no numeric/model/hook behavior changed.

Exact commands, timings and logs: `artifacts/beta1-validation/` (ignored local artifacts). One initial fixture-generator command used a positional output argument and exited2 before generation; corrected to its existing `--output` option. The Python tests were not repeated; all remaining checks passed. No live aircraft or simulator was touched. No complete neighboring catalog-group combination or simulator validation is claimed.

## Handoff to the MTK thread

After the source release is public, merge only `catalog/package-entry.json` and `catalog/group-member.json` into the then-current live catalog, adding optional VREF to both product groups. Preserve existing members/policies and order65 before Intentional Fixes. The full `catalog/content-package-catalog.preview.json` is a historical1.13.0-base review snapshot, not a replacement for the live catalog. Assign and publish a new catalog version separately, with minimumToolkitVersion>=0.21.2.

Release asset pattern: `X-Plane-LevelUp-737NG-VREF-v*.zip`. In-archive manifest: `package-manifest.json`, schema3. Source release: `v0.1.0-beta.1`. Retain package/module identity. Standalone-managed ownership must be removed with the standalone uninstaller before adopting MTK; independently modified managed files remain blocked. Discord-only support and all unofficial/simulator-only/as-is disclaimers are retained.

## Publication

Release URL: https://github.com/wahltho/X-Plane-LevelUp-737NG-VREF/releases/tag/v0.1.0-beta.1

Archive: `X-Plane-LevelUp-737NG-VREF-v0.1.0-beta.1.zip`, 27438bytes,25 unique entries. SHA-256: `b72f955df0aede36d53d96054dd202498cba295fdea60d886c9793cb2c185550`.

Remote readback is retained under `artifacts/beta1-validation/publication.json` after upload. A published package is not yet live MTK-catalog availability; that next step belongs to the MTK thread.
