# iPad controller-only build

Date: 2026-10-23. User requested physical Xbox input and no visible touch controls.

## Implementation

`DMControllerOnly` is enabled in this game's package by the `controller_only=1` profile setting. The iOS gamepad view disables touch interaction and keeps every control layer hidden, including when no controller is connected or a controller disconnects. Device-shake input is disabled in this mode. Physical GameController input remains active.

Xbox mapping: B -> Switch A (confirm), A -> Switch B (back), Y -> Switch X, X -> Switch Y; D-pad, both sticks and stick clicks, LB/RB, LT/RT, Menu/Plus and View/Minus are mapped. Disconnect releases the physical input state. Controller connection count is logged.

## Build and signing

- Release iOS arm64 build succeeded with zero warnings and errors.
- Game bundle identifier unchanged: `local.nxnative.powerpro2025.ios`.
- Signed separately with the same valid Apple Development identity and registered-device provisioning profile.
- Strict codesign verification and complete signed-IPA ZIP CRC passed.
- Artifact: `PowerPro2025-iPad-controller-signed.ipa`.
- Source and executable hashes: `ipad-controller-source-provenance.json`.
- Signature and artifact hash: `ipad-controller-signing-validation.json`.
- Build log: `../logs/ipad-controller-build.log`; compiler log: `../build/ios/pkg/build.log`.

## Device acceptance

Update installation succeeded. The new executable launched into nnMain and reached season selection. Screenshot `evidence/ipad-controller-only.png` shows no virtual control overlay. Its own runtime log confirms `controller-only mode on` and a physical extended controller connection count changing from 0 to 1. Actual button, stick and full-match acceptance still require the user to operate the physical controller; no physical input was simulated.

Previous build reached season selection on this device; its screenshot and runtime log are evidence for that earlier executable only.
