# LevelUp 737NG VREF patch

> **Independent, unofficial community patch.** Not affiliated with, endorsed
> by, or supported by Zibo, LevelUp, Laminar Research or Boeing.
> Support is provided **only** through the
> [wahltho Discord server](https://discord.gg/ySS88PMuyC).
> Do not contact official aircraft/simulator support channels about this patch.

First preview: **0.1.0-preview.1 — experimental, not simulator validated.**

Separate from the VNAV descent-table patch. Prepared for LevelUp's upstream
4.05.35 Lua/plugin arrangement, not the private C++ port. No original aircraft
scripts or plugin binaries are distributed. No FCOM PDF is included.

## Behavior

- Own 737-900ERW/CFM56-7B27 FCOM table instead of the -900 table.
- Retain the FCOM-matching -600/-700/-800/-900 table values.
- Interpolate VREF30/40 without the upstream VREF40+10 cap on VREF30.
- Show/select tabulated landing VREF15 on both FMCs, separately from the
  compiled plugin's existing Flaps15 maneuver reference.
- Correct the kg-to-lb handoff at the Lua speed-envelope VREF lookup.
- Support LevelUp variant IDs 0–4. Other IDs retain upstream calculations.

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
`exact-text-replacements-v1` hooks and `copy-file-v1` module payloads.
The Toolkit applies these declaratively; it does not execute `z_Install.py`.

`catalog/package-entry.json` and `catalog/group-member.json` contain the new
package and optional LevelUp maintenance-group member (order80). The complete
`catalog/content-package-catalog.preview.json` is a review snapshot based on
the locally inspected MTK catalog1.13.0, with these additions. It is not a new
published catalog version. Merge the two entries into the then-current MTK
catalog at release, assign its next version and publish only after validation.

The repository URL `https://github.com/wahltho/X-Plane-LevelUp-737NG-VREF`
is the public source repository. The first package is published as the
`v0.1.0-preview.1` GitHub prerelease, with ZIP and SHA-256 assets. The live
MTK catalog has not been modified; the included catalog files are preparation
for a separate catalog update.

## Standalone installer (alternative to MTK)

Requires Python3.10 or later. Shut down X-Plane first. Once reviewed and tested:

```bash
python3 z_Install.py "/path/to/LevelUp aircraft"
python3 z_Install.py "/path/to/LevelUp aircraft" --uninstall
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

Prepared source and manifests only. No installer execution, Lua execution,
automated tests, build, aircraft installation or simulator validation has run.
No independent review of this Lua package yet. The C++ Source-GO does not
certify this separate package. See `Documentation/PATCH_READINESS.md` for the
owner chain, open review gates and proposed focused validation.

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
establish correct simulator behavior. The current preparation has neither
independent Lua-package review nor executable/simulator validation.

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
