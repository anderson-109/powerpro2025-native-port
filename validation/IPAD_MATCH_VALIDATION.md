# iPad physical-Xbox match acceptance — in progress

Device: iPad Air 13-inch M2. Bundle: local.nxnative.powerpro2025.ios. Build: controller-only signed IPA; see dist/ipad-controller-source-provenance.json and dist/ipad-controller-signing-validation.json.

Initial screenshot: dist/evidence/ipad-match-start.png shows Giants vs Hawks, bottom of inning 1, 0–0, with no virtual controller UI. The user confirmed Xbox operation earlier. This match requires the user's physical controller operation; the assistant did not simulate Xbox input.

Audio: user initially reported no sound. Source inspection found AVAudioSessionCategorySoloAmbient, which respects system silent mode. After asking the user to disable mute, raise media volume and check speaker routing without restarting the game, the user replied that sound was restored. No code or app replacement was necessary for this symptom. Callback statistics alone were not treated as proof of audible output. One sampled callback batch showed 89 underruns / 445 ms zero-padding around a presentation disruption; most sampled batches had zero. Full-match subjective audio acceptance remains pending.

Original current device saves were copied read-only to before-save and hashed in before-save-manifest.json. Three files: 2025-SYSTEM/00/SYSTEM.DAT, 2025-PLAYER/00/PLAYER.DAT and 2025-ARRANGE/00/ARRANGE.DAT.

Pending: user finishes match; capture final score and earned/persistent state; capture post-match device log and save snapshot; verify committed save writes; restart only after saving finishes; verify new-process reads and restored in-game state. No claim of completed iPad match or save/reload acceptance yet.

## Post-match update

The user reported the match completed. The captured screen is already back at the main menu, so the final score was not captured and is not independently claimed. Post-match SYSTEM.DAT differs from the pre-match snapshot; PLAYER.DAT and ARRANGE.DAT are unchanged. Post-match files are preserved in after-save, with after-save-manifest.json.

The game was then restarted using devicectl --terminate-existing. The new runtime enters nnMain, reports controller-only mode and reconnects one extended physical controller. It is waiting for the user to proceed through the opening and show the loaded 2025 shop PP total. Restart success is established; persisted in-game state acceptance is still pending.

Audio log summary: 181 sampled batches / 362,000 callbacks; three nonzero-underrun batches at callbacks 84,000, 92,000 and 96,000, totalling 240 underruns / 1,192.3 ms zero padding. Subsequent sampled batches through callback 362,000 reported zero underruns. These are cumulative session counters, not exact full-match audio-quality measurements. User feedback on full-match subjective audio remains pending. The one HID center-clamp diagnostic reports unvalidated intermediate-stick policy; it does not show an input crash or establish full analog equivalence.


## Restart/load result

The user reported 948 PP after restart. The independently captured `dist/evidence/ipad-reloaded-948.png` shows the 2025 item shop with 948 PP and no virtual controls. This establishes functional loading of persistent system/PP state in a fresh process after the reported physical-Xbox match. It does not establish an exact earned-PP delta because no pre-match PP screenshot was captured, nor an in-progress match resume.

A further device save snapshot is in reloaded-save. PLAYER.DAT and ARRANGE.DAT remain byte-identical to post-match. SYSTEM.DAT changed again during restart/menu navigation (now 4,283 bytes); therefore byte-for-byte persistence of that file is not claimed. There is no observed save-error dialog or startup reset; actual 948 PP display is the functional acceptance evidence.

The user confirmed that sound returned after adjusting iPad mute/output settings. No additional full-match subjective audio response was provided, so a completely glitch-free audio claim remains unsupported. No additional app rebuild was required during this acceptance run.
