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
