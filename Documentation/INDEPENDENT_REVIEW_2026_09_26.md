# Independent whole-package source review — 2026-09-26

Reviewer: independent agent `/root/vref_full_review`; implementation was not authored by this reviewer.
Snapshot: main HEAD 5625655572f6899551c0bce115316bbd157878d5 plus the local prepared preview3 diff.
Method: read-only source/reference review. No tests, Lua execution, installation, build, deploy, commit or publication.

## Verdict: NO-GO for the complete package

One blocking P1 was found in MTK managed-upgrade composition. The original XLua loader defect and the local namespace-based repair were independently confirmed, but that repair is not reliably applied on all supported managed upgrade paths. No additional production-logic blocker was found in the inspected scope. This is source review, not runtime validation.

## P1: composed-current upgrade retains the old loader

`tools/refresh_metadata.py:35–40` generates the loader insertion using only the bare `jit.off()` anchor and does not translate the standalone spec's `legacyBlocks` into a guarded MTK migration.

MTK `src/LevelUp.NavTableUpdater.Core/Content/CompatibilityPackagePlanBuilder.cs:313–325` uses the current managed script when its installed hash differs and structural composition is allowed. `CanComposeFromCurrentTarget` at lines 774–786 permits this for the selected structural script operations. Therefore the earlier assertion that MTK always reconstructs the original backup was incorrect.

Concrete source-derived scenario:
1. Preview2 is installed through MTK.
2. An independent preserved edit or subsequent patch changes either managed Lua script.
3. Preview3 updates that composed current script, rather than rebuilding its clean original.
4. The new loader is inserted after `jit.off()`, ahead of the old loader. The unchanged lookup/display hooks remain accepted as installed.
5. The old loader redeclares `local levelup_vref`; original XLua discards the module return, so this variable is nil and shadows the repaired variable used by downstream functions.
6. The update can succeed while VREF remains inactive.

The current exact-text handler's legacy replacement branch requires no old-anchor match. Merely adding `legacyNewLines` is insufficient because `jit.off()` still matches in the old installation. Renaming the new local variable would conceal the ownership problem rather than solve it.

Required repair contract: absent loader -> fresh insertion; one exact preview1/2 loader -> replace the complete owned block; one exact preview3 loader -> no-op; altered, duplicate or partial markers -> block. Preserve unrelated bytes. Determine a package-compatible guarded migration mechanism before implementation; a change to shared MTK behavior requires its own scoped review.

## Coverage and conclusions

- All 147 cells across the five FCOM tables compared directly with extracted reference pages; no mismatch found. Six supported IDs (native -1 plus LevelUp 0–4), unsupported fallback, finite/positive input checks, endpoints and interpolation inspected.
- Existing nearest-knot publication, both `vref30_40` call sites and the envelope kg-to-klb conversion checked.
- FMC formatter, captain and first-officer selection paths, subsequent invalid/reset behavior checked; shared plugin-facing F15 maneuver reference remains separate. Linux .35 VNAV F15 disassembly inspected.
- Original XLua namespace lifecycle and discarded dofile return confirmed; preview3 raw_table publication/lookup is source-consistent.
- Standalone exact legacy recognition, function fingerprints, EOL preservation, preflight, backups, write ordering and ordinary exception rollback inspected.
- MTK schema/archive generation, group ordering and managed composition inspected. Neighboring descent, W&B, CPDLC, FANS and Intentional Fixes touchpoints inspected; no direct hook/name overlap found.

## Remaining validation gates

No executable evidence was produced by this review. After the migration blocker is corrected, obtain independent review of the final changed source. Future focused cases must cover fresh install, unchanged owned upgrade, composed-current upgrade retaining an unrelated edit, repeat installation, altered/duplicate legacy rejection and uninstall retaining unrelated edits, for both scripts. Original-XLua loading and both product families still need executable validation; simulator evidence remains separate.

The review changed no production or package files. This report is persisted by the parent agent from the independent review findings.

## Final follow-up — restricted-policy Source-GO

Independent reviewer `/root/vref_full_review` reviewed the final payload integration and actual MTK planner after the MTK owner introduced the fail-closed mixed-source policy. Verdict: **Source-GO within that explicit policy**. Unchanged managed states migrate; changed managed sources block before mutation, closing the identified Restore-loss path for this package. The reviewer inspected the real CompatibilityPackageOperation E2E harness; no additional blocking source findings in scope. Parent-confirmed final run: 5 lifecycle scenarios PASS, 3 mixed states safely BLOCKED, 40 corrupt-marker transactions safely BLOCKED. Complete evidence and exact fixture hashes: MTK_OPERATION_INTEGRATION_2026_09_26.md.

Limits: synthetic aircraft identification metadata around complete original scripts; no full catalog-group/neighbor-package execution and no simulator proof. Exact-line marker matching has a documented P2 hardening boundary for whitespace-disguised extra markers and relocated complete blocks. No broad corruption-immunity claim. Commit, publication and matching MTK distribution remain separately gated.
