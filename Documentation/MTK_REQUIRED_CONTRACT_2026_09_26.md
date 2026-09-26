# Preview3 migration: MTK dependency and focused validation

Status: BLOCKED / source NO-GO. No production source changes were made during this follow-up. Preview3 remains local, uncommitted and unpublished. MTK source was read and linked into a diagnostic executable, not edited. GSE is outside scope.

## Existing contract cannot express the requested lifecycle

Independent reviewer `/root/vref_full_review` checked this conclusion against all relevant existing operations:

- `exact-text-replacements-v1`: a fresh insertion keeps `jit.off()`. That old anchor remains inside a legacy installation, while the legacy branch requires zero old matches. It has no owned-marker state guard. Simply adding legacyNewLines is insufficient.
- `insert-marked-block-v1`: safely handles absent and exact current blocks, and rejects modified/duplicate/partial blocks, but rejects every legacy body.
- `vnav-manifest-v1`: replaces a marked body without requiring its exact known contents; fails the requirement to reject edited blocks.
- Composing these operations does not provide conditional absent/current/legacy branches with the required rejection semantics.

## Minimal requested MTK scope (do not implement in parallel here)

1. Add a versioned marked-block migration operation, for example `migrate-marked-block-v1`, with current content, exact approved legacy content arrays, begin/end markers, anchor and before/after position. State handling: zero markers -> unique-anchor insertion; one exact current block -> unchanged bytes; one exact known legacy block -> replace only that complete block; anything partial/duplicated/modified -> fail before mutation. Validate all marker counts, ordering, and the candidate content. Preserve all unrelated bytes and supported line endings.
2. Use the new operation identifier as the capability gate. An older client must reject the unknown operation even for locally opened archives. An optional field on an old handler or only a catalog minimum version would not reliably enforce this.
3. Address composed-current Restore ownership separately before permitting the complete requested scenario. Planner lines 313–325 intentionally start from current bytes after independent changes. `ContentPatchEngine.BuildFileState` lines 573–598 normally retains the previous original backup while updating the installed hash; uninstall planner lines 650–683 then permits restoration of that older whole-file backup. A loader migration alone must not claim it preserves independent changes through Restore.
4. Smallest safe interim scope: migrate unchanged owned old installations and fail closed for composed-current upgrades. This does NOT fulfill the requested automatic upgrade-with-independent-edit case. Full support requires an independently reviewed way to derive the original baseline with only this package's owned blocks removed, retain unrelated edits, and bind that baseline to update/repeat/restore state. Reusing the composed pre-update file as an "original" is also insufficient because it still contains the old VREF hooks.

Once an agreed handler/ownership contract is implemented by MTK, adapt VREF's metadata generator and both script targets to that contract, regenerate integrity metadata, and rerun the end-to-end MTK cases. Do not silently weaken these gates to publish preview3.

## Tests actually executed

`python3 -m unittest discover -s tests -v`: **8 test methods PASS** (existing 3 plus 5 focused methods, each containing subcases).

- Full original .35 calc and FMS source: fresh insertion, repeat, removal preserving source under LF and CRLF, with an unrelated prefix retained.
- Preview1 and preview2 source snapshots: standalone upgrade with/without an additional independent edit, final equality to clean current installation, removal retaining independent edit. Preview2 uses its exact local commit 5625655572f6899551c0bce115316bbd157878d5 because its tag is absent locally.
- Both current/legacy states, every hook: duplicate, modified, missing begin and missing end rejected.
- Invalid second original target: preflight raises before writing the first target, module or backup.
- Original .35 init.lua executed unchanged under LuaJIT 2.1 (Lua 5.1 API). Actual production loader blocks execute in two original XLua namespaces with only XLuaGetCode mapped to file loading. New module APIs load independently; original loader yields nil; failed reload clears the old slot. This is NOT simulator runtime or full FMS/AP execution.
- Existing archive, catalog ordering and synthetic installer main lifecycle checks remain green.

Initial test-run errors were fixture-only: an added CRLF comment on a native-LF fixture and a locally unavailable preview2 tag. These were corrected in tests; no product change was made in response.

`dotnet run --project tests/mtk_probe/Probe.csproj -- <VREF repo>`: actual MTK handler/codec/JSON source files linked unchanged. Both loader paths reproduce the legacy-shadowing migration bug. Fresh/repeat pass; existing marked handler safely rejects legacy/modified/duplicate/partial states. Diagnostic exit zero means the expected bug was reproduced, NOT that migration passes.

Limits: the MTK planner, mutation engine, backup/restore and complete package installation were not executed in this probe. End-to-end MTK upgrade/Restore remains blocked pending the contract above. Standalone injected write-failure rollback and complete simulator validation were not added or claimed. No release/commit/push performed.
