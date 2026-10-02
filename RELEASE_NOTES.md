# v0.1.0-beta.1

Public Beta for Zibo B737-800X and LevelUp 737NG, including dedicated 900ER
landing-reference tables. Requires **MTK 0.21.2 or newer** for managed install.

- Promotes the reviewed Preview3 runtime unchanged: identical tables, module,
  loaders and remaining hooks. No new flight behavior is introduced.
- Adds explicit Preview3-to-Beta install/update, repeat and Restore coverage
  for both products, including rejection of independently changed managed files.
- Includes native MTK schema-3 payloads and a prepared optional catalog entry.
  The MTK thread publishes the live catalog update after this source release.
- Uses a regular GitHub Release because MTK compatibility archives use
  `releases/latest` and reject the GitHub prerelease flag. The release is
  explicitly **Beta**, not simulator-validated Stable software.

Simulator validation remains open. Keep a full aircraft backup and close
X-Plane before installation. Do not mix standalone and MTK ownership.
Support only through https://discord.gg/ySS88PMuyC . Independent, unofficial,
as-is; not affiliated with Zibo, LevelUp, Laminar Research or Boeing. Simulator
use only; original aircraft scripts, binaries and manuals are not distributed.

# v0.1.0-preview.3

Requires **X-Plane 737NG Maintenance Toolkit 0.21.2 or newer** for managed
installation. Simulator validation remains open.

Fixes a source-confirmed activation blocker in preview1/2: the original XLua
dofile discards return values, so the previous loader always fell back to the
upstream calculations. The table API now passes through a private raw_table
namespace slot. Includes exact standalone migration from the prior loaders
and payloads. MTK uses the new versioned marker migration contract; unchanged
managed installations upgrade and Restore, while independently changed managed
scripts block before mutation. Hook insertion uses marker identity, preserving
independent content between anchors and blocks. Focused standalone/XLua tests
and real local MTK lifecycle tests pass; simulator validation and coordinated
publication remain open.

# v0.1.0-preview.2

- Adds native Zibo737-800X (variant-1) using the existing800 FCOM table.
- Corrects native-Zibo FMC landing VREF15 while retaining the compiled
  plugin's Flaps15 maneuver-speed reference.
- Adds native MTK support for both Zibo and LevelUp maintenance groups.
- Retains package identity and existing hooks; permits exact preview1
  table-module upgrades and preserves rejection of unknown modified modules.
- Focused archive/catalog and standalone synthetic-aircraft install/repeat/
  uninstall tests pass; MTK's production loader accepts the schema-3 ZIP.
  Full MTK install/restore, Lua runtime, independent review and simulator
  validation remain open.

# v0.1.0-preview.1

First experimental LevelUp 737NG VREF package for the upstream .35 Lua/plugin
arrangement. **This is a prerelease, not a validated production release.**

## Changes

- Separate FCOM 900ERW/CFM56-7B27 reference table.
- FCOM VREF30/40 interpolation without the old VREF30 cap.
- Tabulated FMC landing VREF15 while preserving the original plugin's
  separate Flaps15 maneuver-speed contract.
- Correct kg-to-lb conversion at the Lua speed-envelope VREF lookup.
- Standalone Python installer with backups and uninstall support.
- Native MTK schema-3 manifest, declarative payloads and catalog preparation.

## Installation and status

Download and extract `X-Plane-LevelUp-737NG-VREF-v0.1.0-preview.1.zip`.
Verify it against the accompanying `SHA256SUMS.txt` and read `README.md` before
installing. Close X-Plane and back up the aircraft. The standalone installer
requires Python3.10+ and the aircraft root argument. MTK catalog availability
requires a separate catalog publication; the included catalog is only a preview.
Do not mix standalone and MTK ownership of the same installation.

No independent review, automated installer/Lua/MTK tests or simulator flight
validation has been performed on this Lua package. Archive integrity checks
are not behavior tests. The private C++ patch's review does not validate this
separate implementation. Unknown source functions are rejected by the standalone
installer. Compatibility with other patches is not yet validated.

## Support and disclaimer

Support exclusively on the [wahltho Discord server](https://discord.gg/ySS88PMuyC).
Do not contact official Zibo, LevelUp or Laminar Research support about this patch.
Independent and unofficial; not affiliated with, endorsed by or supported by
Zibo, LevelUp, Laminar Research or Boeing. For desktop simulation only, never
real-world flight operations. Supplied as-is without warranty; use at your own
risk. Original aircraft scripts, plugin binaries and manuals are not included.
