# Lua package preparation

Current correction: preview3 fixes the original-XLua module activation blocker
found during source review. See SOURCE_REVIEW_2026_09_26.md. Earlier statements
about preview1/2 module loading are superseded; executable validation is open.

## Reference and scope

Reference scripts: original B738X_XP12_4_05_35; the locally supplied
LevelUp V2.S1.50A calc.lua is identical after newline normalization.
Reference data: FCOM printed PI.10.4, PI.20.6, PI.40.4, PI.50.4, PI.70.4;
PDF pages874/1028/1360/1518/1836. 900ER uses the 900ERW/7B27 table.
The five tables are transcribed in the stateless payload with source labels.
Native Zibo ID-1 uses the same800 table. Existing aliases/MAX/BBJ IDs outside
-1 and0–4 remain upstream; no new performance
data is invented for them. No changes to AP logic, plugin binary or ACF.

## Owner-chain closure design

| Surface | Contract |
| --- | --- |
| Inputs | APPROACH gross weight in1000lb, runtime variant-1/0–4; envelope input locally converted from1000kg |
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
Zibo/LevelUp variants. Surrounding stall/mass formulas retain kg. The800 envelope
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
- Standalone install/repeat/uninstall passes with a synthetic CRLF aircraft;
  missing/duplicate/modified markers, real upstream functions, rollback and
  unrelated patch preservation remain open.
- MTK native parser/planner, catalog-group composition, install/restore and
  ownership behavior; no claim of MTK install validation from schema inspection.
- FCOM knots/midpoints/endpoints, all variants, invalid/reset and variant
  switch, FMC F15 selection, no unintended VNAV maneuver-speed reduction.
- Lua runtime and simulator validation. Focused archive/catalog and synthetic
  standalone lifecycle tests pass; production MTK loader accepts the ZIP.
- User authorized public GitHub repository, initial commit/push and first
  preview release. This publication does not close the validation gates above.
  Live MTK catalog publication and aircraft installation are separate.

## Native-Zibo extension (preview2)

Zibo's native b737_variant initializer/reset is -1 in the reconstructed
plugin. The upstream Lua fallback uses the800 table for it. The payload now
explicitly supports -1 and maps it to the same model as LevelUp0; invalid
other IDs still return nil. No table entries or hooks change. Native Zibo's
F30/F40 outputs retain their table values; the meaningful change is tabulated
F15 in FMC display/selection, without changing the plugin-facing F15 alias.
This avoids lowering its normal VNAV Flaps15 maneuver reference.

MTK supportedProducts includes both families; the optional vref member is
included in both maintenance-group catalog previews. Package ID, repository,
payload filename and hook revision are intentionally retained for updates.
The standalone installer accepts the exact released preview1 module hash;
all other foreign payloads still block. MTK copy target sourceSha256 includes
that known old module. No new hook body or legacy hook replacement is needed.

tools/refresh_metadata.py derives both MTK hook payloads and all integrity
metadata from the canonical spec and table module. `tools/build_package.py`
assembles and verifies the dual-layout archive. Focused archive/catalog and
synthetic standalone lifecycle tests plus production MTK loader smoke passed.
Independent review and simulator validation remain open.
Add native-1/unknown-negative checks, preview1-to2 upgrade/restore, and both
MTK group paths to the validation matrix before a production release.

## Independent review / MTK dependency update

Prepared preview3 remains **NO-GO**. See INDEPENDENT_REVIEW_2026_09_26.md and
MTK_REQUIRED_CONTRACT_2026_09_26.md. Focused Python suite 8/8 methods passes;
original XLua namespace loading is exercised under LuaJIT. The direct MTK
handler probe reproduces the composed-current upgrade failure in both scripts.
No complete MTK migration/Restore or simulator claim; shared handler/ownership
support must be agreed before this package can safely complete that lifecycle.

## Final restricted-policy validation (supersedes migration NO-GO above)

Local source now independently GO for unchanged managed upgrades and fail-closed
rejection of independently changed managed Lua sources. Real MTK E2E: 5 complete
install/update/repeat/Restore scenarios PASS, 3 composed states safely BLOCKED,
40 corrupt-marker transactions safely BLOCKED. Python 9/9 PASS. See
MTK_OPERATION_INTEGRATION_2026_09_26.md and the final independent review addendum.
No commit/push/release or simulator validation; coordinated release gate remains.
