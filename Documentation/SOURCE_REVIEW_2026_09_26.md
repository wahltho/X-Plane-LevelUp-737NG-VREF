# Focused source review — 2026-09-26

Baseline: 5625655572f6899551c0bce115316bbd157878d5, clean main on entry.
Self-review, not independent. No tests, installer/Lua/MTK execution, build,
deploy, commit, push or release in this review. Earlier recorded package tests
remain historical evidence; they did not validate original XLua module loading.

## P1 — original XLua discards the module return value

Original .35 plugins/xlua/init.lua:449–460 defines dofile through
get_run_file_in_namespace: setfenv(chunk, ns); chunk(), without return.
The previous payload's return table is discarded. Both loaders receive nil,
log inactive and retain the old upstream calculations. Both preview1 and
preview2 are affected under the original runtime. Standard Lua dofile behavior
was incorrectly assumed during initial implementation.

Fixed locally in prepared preview3: register B738_levelup_vref_module through
raw_table and publish the API in the caller's private XLua namespace. Clear
that slot before dofile, then read the API from it. Evidence: init.lua:375–411
(namespace_write), 449–460 (dofile), 471–474 (raw_table), 499–501 (binding).
No public dataref or cross-script cache/ordering dependency is introduced.
Each script retains its own local data and fallback handling.

## Upgrade ownership

Standalone accepts exact preview1/2 loader blocks as legacy blocks, restores
the original source and installs the new loader. Only exact known previous
module hashes are accepted; foreign modifications still block.
MTK reconstructs owned original script backups before applying new operations
(CompatibilityPackagePlanBuilder). Fresh declarative patches therefore suffice
for managed upgrades. Adopting an old standalone installation is unsupported:
uninstall standalone before switching to MTK. A naive legacyNewLines entry
that retains jit.off would conflict with the handler's old-anchor matching;
no such ambiguous migration was added.

## Other focused checks

- Native-1 maps to800; unsupported variants remain upstream. Table entries,
  weight conversion, endpoint saturation and shared interpolation unchanged.
- Both FMC selectors consume formatted vref_15; plugin-facing FMS/vref_15
  retains its maneuver alias. Later upstream invalid/reset display logic remains.
- Envelope conversion affects only the helper input. Native800 retains its
  separate stall-model branch.
- MTK copy operations allow missing files as well as exact known old hashes.
- Installer plans all targets before writes, keeps outside bytes/EOL and
  rejects modified markers/payloads. Ordinary exceptions roll back; OS-crash
  atomicity across multiple files is not claimed.

Static repair only. Required next checks: original XLua namespace/dofile
loading, both scripts/products, prior-package upgrades and MTK reconstruction
from owned backups. No executable or independent Source-GO for preview3 yet.

## Superseding independent finding

The "MTK reconstructs owned original script backups" statement above is not
unconditional: composed-current upgrades use current modified bytes. The
independent review rejected this migration. See INDEPENDENT_REVIEW_2026_09_26.md
and MTK_REQUIRED_CONTRACT_2026_09_26.md for the blocking update/Restore contract
and the subsequently executed focused tests. Preview3 has no Source-GO.
