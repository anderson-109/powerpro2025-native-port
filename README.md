# PowerPro 2025 native Apple port — private source backup

This repository contains a source snapshot of the local nxnative compatibility-layer work for Powerful Pro Baseball 2024–2025, update 1.13.0 (`0100D1C01C194000`), plus validation reports. It is an experimental local port and does not establish complete game compatibility.

## Layout

- `nxnative/`: modified source and upstream tools, with original licenses retained. Baseline: seedds/nxnative commit `e37af0dc87b3866a0a1cc311cf793eea882414c5`. This is a source snapshot, not an upstream Git-history mirror.
- `0100D1C01C194000-work/`: local preparation/build/packaging helpers and version-specific profile metadata. Keep this directory next to nxnative when using the helpers.
- `validation/`: Mac match/save/restart evidence summaries, iPad controller-only implementation and physical-device match/restart observations.
- `EXPORT_MANIFEST.json`: snapshot file hashes and upstream attribution.

## Verified observations

The Mac build completed one exhibition match with mixed automatic/keyboard operation and a save/restart test displaying 516 PP. The iPad controller-only build was signed and installed locally; the user reported completing a physical-Xbox match. After restarting the iPad app, the item shop visibly showed 948 PP. Touch controls remain disabled. Xbox B confirms and A returns.

The initial iPad no-sound symptom resolved after the user adjusted device mute/output settings. Some session audio-underrun counters were nonzero; completely glitch-free full-match audio is not established. Intermediate analog center-clamp equivalence remains unvalidated. The iPad final-score screen was not captured. Read the validation reports for evidence boundaries.

## Local inputs required

No original game packages, executable game modules, RomFS, game artwork, translated shader binaries, Apple signing identities/profiles, encryption keys, saves, or app archives are included. Extract and build using your own local inputs and environment. The upstream tools and their third-party runtime libraries retain their original licenses; see nxnative/LICENSE and the third-party directories.

The helpers retain local toolchain assumptions (for example Homebrew/.NET paths). Adjust those to your machine. Generated profile metadata contains `<WORKSPACE>` in provenance comments. Build output, screenshots and diagnostic logs referenced in validation reports remain local and are not part of this source backup. Do not interpret missing evidence links as uploaded assets.
