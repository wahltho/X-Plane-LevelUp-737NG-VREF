# Zibo / LevelUp 737NG VREF patch

> **Independent, unofficial community patch.** Not affiliated with, endorsed
> by, or supported by Zibo, LevelUp, Laminar Research or Boeing.
> Support is provided **only** through the
> [wahltho Discord server](https://discord.gg/ySS88PMuyC).
> Do not contact official aircraft/simulator support channels about this patch.

Version: **0.1.0-preview.3 — XLua loader repair; simulator validation pending.**
Preview1/2 do not activate the module under the original .35 XLua loader.
See [source review](Documentation/SOURCE_REVIEW_2026_09_26.md).

Separate from the VNAV descent-table patch. Prepared for Zibo/LevelUp's upstream
4.05.35 Lua/plugin arrangement, not the private C++ port. No original aircraft
scripts or plugin binaries are distributed. No FCOM PDF is included.

## Behavior

- Own 737-900ERW/CFM56-7B27 FCOM table instead of the -900 table.
- Retain the FCOM-matching -600/-700/-800/-900 table values.
- Interpolate VREF30/40 without the upstream VREF40+10 cap on VREF30.
- Show/select tabulated landing VREF15 on both FMCs, separately from the
  compiled plugin's existing Flaps15 maneuver reference.
- Correct the kg-to-lb handoff at the Lua speed-envelope VREF lookup.
- Support native Zibo variant ID−1 using the -800 FCOM table and LevelUp
  variant IDs0–4. Other IDs retain upstream calculations.

For native Zibo, VREF30/40 already match the -800 FCOM rows, and the old
VREF30 cap does not clip those rows. The effective landing-reference correction
is FMC VREF15 (3–7 kt lower at the table knots). Its normal VNAV maneuver
target remains VREF40+20. Zibo's separate stall-envelope branch is unchanged.

The existing `laminar/B738/FMS/vref_15` continues to hold VREF40+20 because
the original plugin directly uses it in VNAV. The FMC landing reference is
computed locally in `B738.a_fms.lua`; the same formatted value feeds both
CDU selection handlers. External consumers of the original dataref still see
the maneuver alias. This differs intentionally from the private C++ fix,
where the compiled consumer can also be corrected.

`B738.levelup_vref.lua` is installed in both script directories. Each script
loads the same stateless module locally; no new public datarefs, callback-order
handshake or cached aircraft-specific state is introduced. Load/lookup failure
falls back to upstream values. Normal source guards still reject incompatible
installation targets before modifying the aircraft.

## MTK integration

`package-manifest.json` is a native **schema-3 compatibility package** with
`migrate-marked-block-v1` loader migration, marker-aware hook insertion,
exact-text replacement and `copy-file-v1` module payloads. **MTK 0.21.2 or
newer is required.** This minimum provides the migration operation and safe
blocking of independently changed managed scripts. Older clients reject the
unknown operation; do not bypass that check.
The Toolkit applies these declaratively; it does not execute `z_Install.py`.
`python3 tools/build_package.py /path/to/output.zip` creates a deterministic
ZIP with both standalone root files and MTK's `modules/vref/` payloads.

`catalog/package-entry.json` and `catalog/group-member.json` contain the new
package and optional maintenance-group member (order65, before Intentional Fixes), for both Zibo and
LevelUp. The complete
`catalog/content-package-catalog.preview.json` is a review snapshot based on
the locally inspected MTK catalog1.13.0, with these additions. It is not a new
published catalog version. Merge the two entries into the then-current MTK
catalog at release, assign its next version and publish only after validation.

The repository URL `https://github.com/wahltho/X-Plane-LevelUp-737NG-VREF`
is the public source repository. The previous LevelUp-only package was
`v0.1.0-preview.1`. The live
MTK catalog has not been modified; the included catalog files are preparation
for a separate catalog update.

The repository/package ID, module filename and hook markers keep their
historical LevelUp names to preserve update identity. Preview3 updates both
loaders for XLua's dofile semantics; other hooks retain their preview1 revision.
The standalone installer accepts exact known preview1/2 loaders and module
hashes for upgrades; modified payloads still block. MTK upgrades its own managed
installations from original backups only when the managed scripts still match
the recorded installed hashes. Independently changed managed scripts block
before mutation, because their edits cannot yet be restored safely. Do not
force that upgrade. Uninstall standalone copies with the
standalone installer before adopting MTK ownership.

## Standalone installer (alternative to MTK)

Requires Python3.10 or later. Shut down X-Plane first. Once reviewed and tested:

```bash
python3 z_Install.py "/path/to/Zibo or LevelUp aircraft"
python3 z_Install.py "/path/to/Zibo or LevelUp aircraft" --uninstall
```

Do not combine standalone ownership with an MTK-managed installation; use one
installation method. The standalone tool validates whole affected function
fingerprints against .35, in addition to unique exact-line anchors. This is
stricter than MTK's localized structural checks and may reject other patches
that modify the same functions; such combinations require explicit review.

Before mutation it plans both scripts and both payload copies, checks package
hashes, and saves content-addressed backups below `.levelup-vref-backups` in
the aircraft directory. It preserves existing LF/CRLF and script bytes outside
the marked hooks. Reinstallation is idempotent; modified/partial/duplicate
VREF blocks are rejected. Uninstall removes only known hooks and matching
payloads, preserving unrelated edits. Writes use per-file atomic replacement
and exception rollback; an operating-system crash during a multi-file update
is not transactionally atomic. Keep the backups for recovery.

## Validation status

Local preview3 validation: 9 Python tests pass, including original-script
standalone migration and original XLua namespace loading under LuaJIT.
The real local MTK package/plan/execute/Restore path passes five product/version
lifecycles; three independently changed managed states and 40 corrupt-marker
inputs block without changing aircraft, state or backups. The direct handler
round also covers all 52 fixture cases. No simulator validation is claimed.
Independent source review covers the Lua behavior and current payload integration;
release remains gated on the coordinated final review and compatible MTK release.
See `Documentation/MTK_OPERATION_INTEGRATION_2026_09_26.md` for exact boundaries.

## Support, disclaimer and attribution

Installation questions, bug reports and feature requests belong exclusively
on the [wahltho Discord server](https://discord.gg/ySS88PMuyC).
GitHub Issues and Discussions are not support channels for this project.
See [SUPPORT.md](SUPPORT.md) for the information to include in a report.

For desktop flight simulation only; not for real-world flight planning,
training certification or aircraft operation. This is an independent,
unofficial modification, supplied as-is without warranty. Keep a complete
aircraft backup, shut down X-Plane before applying changes, and use the patch
at your own risk. A reviewed source change or a passing dry test does not
establish correct simulator behavior. Independent source review and focused
installation tests are complete within the documented scope; simulator
validation remains open.

This patch does not correct every variant-specific aircraft performance or
autopilot issue. After an aircraft update, check compatibility and reinstall
through the same installation method; never overwrite an unknown changed
source or restore an old complete Lua file over a newer upstream release.

Zibo, LevelUp, X-Plane and Boeing names identify compatibility and reference
sources only. Their aircraft, manuals and other proprietary assets remain
with their respective rights holders and are not distributed here. The
original patch software is licensed under [MIT](LICENSE); that license does
not grant rights to third-party aircraft or reference material.

Prepared by Thomas W. (wahltho). Packaging approach informed by the existing
LevelUp VNAV descent-table project by wahltho and RandomUser.
