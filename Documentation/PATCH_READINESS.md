# Lua package preparation

## Reference and scope

Reference scripts: original B738X_XP12_4_05_35; the locally supplied
LevelUp V2.S1.50A calc.lua is identical after newline normalization.
Reference data: FCOM printed PI.10.4, PI.20.6, PI.40.4, PI.50.4, PI.70.4;
PDF pages874/1028/1360/1518/1836. 900ER uses the 900ERW/7B27 table.
The five tables are transcribed in the stateless payload with source labels.
Existing aliases/MAX/BBJ IDs outside0–4 remain upstream; no new performance
data is invented for them. No changes to AP logic, plugin binary or ACF.

## Owner-chain closure design

| Surface | Contract |
| --- | --- |
| Inputs | APPROACH gross weight in1000lb, runtime variant0–4; envelope input locally converted from1000kg |
| Producer | Pure calculate() interpolates all three rows from the same bracket; saturates endpoints; no scalar tuning |
| F30/F40 | Hook at start of vref30_40 returns unrounded FCOM references, retaining existing publisher rounding |
| Plugin F15 | B738_calc_vref continues publishing F40+20; compiled VNAV consumer remains on its existing maneuver contract |
| Landing F15 | B738_calc formatter overrides only vref_15 text from FCOM, rounded to nearest knot; both CDU selections share that text |
| Invalid/reset | Existing zero/invalid-display code remains; payload rejects nonfinite/nonpositive mass and unsupported variants; no new state survives reset |
| Recompute | Both Lua scripts compute from current weight and variant, not cached cross-script data |
| Other consumers | Envelope and F40-based approach/manoeuvre consumers intentionally receive corrected ER reference; existing offset policies retained |
| Packaging | Two scripts and two identical payload copies; native MTK schema3 module and alternative Python installer |

Direct RE proof: original Linux .35 vnav_calc_speed at0x1ac57a–0x1ac5e0
reads FMS/vref_15 and copies it to flaps_speed when nonzero. Only zero falls
back to pfd_flaps_15. Evidence is stored in the RE repository as
Documentation/zibomod_re/VREF15_VNAV_40535_2026_09_26.md and its disassembly.
Mac/Windows equivalence was not separately checked for this package.

The kg/lb error is already in upstream Lua: total_weight_t is sim mass/1000
in kg; vref30_40 expects klb. The hook corrects this call for supported
LevelUp variants. Surrounding stall/mass formulas retain kg. The800 envelope
uses its separate stall-model branch, not the lookup output.

## Derived from the descent installer

Retained: separate table/helper file, small marked hooks, package version,
backups, newline preservation and repeat installation. Added: exact unique
anchors, affected-function fingerprints for standalone installation, planning
all target files before writes, content-addressed backups and exception
rollback. Native MTK manifest/schema3 replaces the descent-only legacy adapter;
the Toolkit does not need a new operation type for this package.

Standalone patch-spec.json is the canonical hook description. MTK exact-text
payloads are generated from it. installer-manifest.json protects the standalone
payload set; package-manifest.json describes native MTK module ownership.
Catalog data is prepared locally, not added to the live MTK repository.

## Open gates — not yet validated

- Independent review of Lua semantics, XLua local module environment, both
  FMC selection paths and original-plugin consumer separation.
- Source compatibility/composition with VNAV, W&B, FANS and optional MTK
  modules; especially modules touching B738_calc_min_max_spd or B738_calc.
- Standalone LF/CRLF install/reinstall/uninstall, missing/duplicate/modified
  markers, unsupported functions, rollback and unrelated patch preservation.
- MTK native parser/planner, catalog-group composition, install/restore and
  ownership behavior; no claim of MTK install validation from schema inspection.
- FCOM knots/midpoints/endpoints, all variants, invalid/reset and variant
  switch, FMC F15 selection, no unintended VNAV maneuver-speed reduction.
- Lua syntax and simulator validation. No tests have been run or authorized.
- User authorized public GitHub repository, initial commit/push and first
  preview release. This publication does not close the validation gates above.
  Live MTK catalog publication and aircraft installation are separate.
