# Full match and save/restart acceptance — 2026-10-23

## Result and scope

Completed one 2025 exhibition match: Giants 0–8 SoftBank Hawks, regulation nine innings, home ninth omitted by the game's normal rule. The detailed score screen shows Giants 6 hits/0 errors and Hawks 14 hits/1 error. The game awarded 216 PP, increasing the saved total from 300 to 516. A fresh process loaded the same isolated save and visibly displayed 516 PP in the item shop. Both diagnostic processes exited normally with return code 0.

The first six innings used the game's built-in automatic progression. From inning seven, keyboard inputs exercised batting, pitching, fielding throws, pause/options and pitcher changes with the rookie preset's automatic running/catching assistance. No score, progress or save bytes were patched. This establishes this exhibition path, not nine manually played innings or a completed physical-Xbox match. Xbox mapping remains B-confirm/A-back; the user's earlier mapping confirmation is separate evidence.

## Build and platform

- Game: 0100D1C01C194000, 1.13.0/v983040, main build 3f2f70da19fa2114d6fa4c622cfad459.
- Apple M2, macOS 27.0, arm64; minimum packaged macOS/iPadOS 26.0.
- Source base e37af0dc87b3866a0a1cc311cf793eea882414c5 with local changes; run metadata records the exact diff and module hashes.
- Diagnostic host SHA-256: 1ba46b014de7c1506672731de7a291895d0b14905eb671a314da625e204d7a15.
- Shader chain c55da66bdedf. Final package hashes: `dist/package-validation.json`.
- Match run: 20261023T113955+0800, 1259.504 seconds including menus; reload: 20261023T120117+0800, 350.641 seconds including UI checks.
- Isolated state: `sessions/fullmatch-20261023/save`. Originals and other sessions retained.

## Save evidence

- The match run logged four successful atomic commits, eight save writes total, including post-match commits after PP award/help dismissal.
- SYSTEM.DAT changed from `cef6d368a48472869b3f16384a26fb2aa1cf8197f40bdbdfb7ea9f102c6cf9b1` to `e180215efec94f39aab9b5aa5e7e1877b3ec543b21a72b07e73c7b854d6e80c2`. PLAYER.DAT and ARRANGE.DAT stayed byte-identical.
- The fresh process read SYSTEM.DAT in two successful ranges: offset 0/800 bytes, offset 800/3300 bytes; together 4100 bytes.
- The item-shop screenshot `dist/evidence/fullmatch-reloaded-516.png` confirms the newly earned 516 PP. This is saved system/award state, not an in-progress match resume or a persisted exhibition score-history claim.
- Before/after snapshots and manifests remain under the isolated session directory.

## Runtime observations and limits

- No [RED] failure lines or crash in the match run. Visual results include field, crowds, batting, pitching, scoring, substitutions, hero scene and score menus.
- Actual audio output opened and callbacks continued throughout. In 58 reported windows (116000 callbacks), 8 underruns produced 85.4 ms of zero padding. This is not proof of glitch-free listening or perfect audiovisual synchronization; no subjective listening acceptance was collected.
- Visible uniform numbers and portions of names rendered in close-ups; this does not certify every player, uniform or camera angle.
- Standalone packaged Mac App was separately opened after the match and visibly reached season selection; its save directory remains separate. Screenshot: `dist/evidence/mac-zero-warning-package-boot.png`.
- iPad IPA rebuilt and CRC/resource checks passed, unsigned; no iPad installation or hardware boot/input/audio/save acceptance. Repository instructions leave signing/sideloading and device testing to the user.

## Evidence

`dist/evidence/fullmatch-score.png`, `fullmatch-hero.png`, `fullmatch-earned-points.png`, `fullmatch-reloaded-516.png`, match/reload logs and metadata, and zero-warning compiler logs. Source, original game packages, keys and saves remain local; no commit, upload, signing or device installation.
