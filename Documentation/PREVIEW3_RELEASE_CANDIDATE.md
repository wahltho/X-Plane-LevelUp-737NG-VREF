# Preview3 release candidate

Minimum supported managed installer: X-Plane 737NG Maintenance Toolkit **0.21.2**.
Final MTK source tested: `fc7b27832968b6c9561a476d2fae85513f8bebd6` on clean main.

Final verification: Python suite 9/9 PASS; real MTK full package install/update,
repeat and Restore 5/5 PASS; independent managed-source changes 3/3 BLOCKED
without mutations; corrupt-marker transactions 40/40 BLOCKED without mutations.
Independent Source-GO within that restricted policy is recorded in
INDEPENDENT_REVIEW_2026_09_26.md. Simulator and complete neighboring catalog-group
combinations remain unverified. Live catalog is not activated by this package.

Prepared release asset:
`dist/X-Plane-LevelUp-737NG-VREF-v0.1.0-preview.3.zip`
Size: 26636 bytes.
SHA-256: `37b168d9f44ce1cd4580beb54b2b8cf26ac7f526c46e14292f2e1c486958f4b3`.
Companion: `dist/SHA256SUMS.txt`.
25 unique entries; archive CRC and manifest/payload integrity checked. No full
upstream Lua scripts, FCOM PDF or plugin binaries included. Public support and
disclaimers remain Discord-only and simulator-only.

Publication gate: no preview3 tag/release until the coordinating MTK thread
confirms that the MTK 0.21.2 release assets are successfully online. Source
commit/push is separately authorized. This report records the candidate, not
proof of a published release.
