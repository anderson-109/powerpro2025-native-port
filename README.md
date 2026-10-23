# PowerPro 2025 native Apple port — source and validation

This repository contains a source snapshot of the local nxnative compatibility-layer work for Powerful Pro Baseball 2024–2025, update 1.13.0 (`0100D1C01C194000`), plus validation reports. It is an experimental local port and does not establish complete game compatibility.

## Upstream attribution and dependencies

This work builds on the projects below. Their original authors retain credit and their original licenses apply. Versions below come from the checked-in source notices/project declarations or the local build environment; they are not claims about the newest upstream release. A source URL alone does not establish an exact imported commit.

### Core lineage and incorporated code

| Project / GitHub source | Use in this port | Version / provenance | License and local evidence |
|---|---|---|---|
| [nxnative — seedds/nxnative](https://github.com/seedds/nxnative) | Main ARM64 rewrite, Horizon compatibility host, NVN-to-Metal and iOS shell | Baseline [e37af0d](https://github.com/seedds/nxnative/commit/e37af0dc87b3866a0a1cc311cf793eea882414c5), with local modifications | MIT; [license](nxnative/LICENSE), [upstream acknowledgements](nxnative/README.md#acknowledgements) |
| [d2r-mobile — jhaizhou-ops/d2r-mobile](https://github.com/jhaizhou-ops/d2r-mobile) | Original native-execution approach and generic code from which nxnative originated | Indirect lineage through nxnative; exact imported revision not recorded here | MIT; credited in [nxnative README](nxnative/README.md#acknowledgements) |
| [Ryujinx / Ryubing](https://github.com/Ryubing) | Maxwell shader translation to SPIR-V: Ryujinx.Graphics.Shader, Ryujinx.Common and Spv.Generator | Vendored subset identified as 1.3.2; local changes documented in its README. The vendored notice identifies the GitHub organization, not a still-available exact repository URL | MIT; [source and changes](nxnative/dm/third_party/ryujinx/README.md), [license](nxnative/dm/third_party/ryujinx/LICENSE.txt). Also see the [current non-GitHub upstream](https://git.ryujinx.app/projects/Ryubing) |
| [MacNativeGames — ly05010419/MacNativeGames](https://github.com/ly05010419/MacNativeGames) | Adapted GPU 8-bit index widening, in-pass clear triangles and vertex-counter lowering | Imported revision not recorded; attribution is in nvn_mtl.m and dmsh_xlate/Program.cs | MIT; [retained license](nxnative/dm/third_party/macnativegames/LICENSE) |
| [deko3d — devkitPro/deko3d](https://github.com/devkitPro/deko3d) | Texture layout size algorithm ported from source/dk_image.cpp | Imported revision not recorded | zlib; [notice and implementation](nxnative/dm/gfx/nvn/nvn_tex.c) |
| [libvpx — webmproject/libvpx](https://github.com/webmproject/libvpx) | VP9 movie decoder | Vendored v1.17.0, upstream commit prefix 6df3ec3; this port has local warning fixes, so this snapshot is modified | BSD-3-Clause; [provenance](nxnative/dm/third_party/libvpx/README.md), [license](nxnative/dm/third_party/libvpx/LICENSE), [patent grant](nxnative/dm/third_party/libvpx/PATENTS) |
| [stb — nothings/stb](https://github.com/nothings/stb) | stb_vorbis movie audio decoder; stb_image/stb_image_write in the FLIP verification tool | stb_vorbis 1.22 / commit prefix 1ee679c; FLIP's copies identify stb_image 2.23 and stb_image_write 1.13 | MIT or public domain; [Vorbis notice](nxnative/dm/third_party/stb_vorbis/README.md), [license](nxnative/dm/third_party/stb_vorbis/LICENSE); image-header notices remain in flip/tool |
| [Vulkan-Headers — KhronosGroup/Vulkan-Headers](https://github.com/KhronosGroup/Vulkan-Headers) | Header declarations for the host's Vulkan layer; retained shared infrastructure, not evidence that PowerPro uses Vulkan | Vendored 1.4.363 | Apache-2.0 OR MIT; [provenance](nxnative/dm/third_party/vulkan-headers/README.md), [license](nxnative/dm/third_party/vulkan-headers/LICENSE.md) |
| [FLIP — NVlabs/flip](https://github.com/NVlabs/flip) | Optional image-difference verification tool | Exact vendored revision not recorded | BSD-3-Clause; [license](nxnative/dm/third_party/flip/LICENSE) |
| [TinyEXR — syoyo/tinyexr](https://github.com/syoyo/tinyexr) | EXR support inside the FLIP command-line verification tool | Exact vendored revision not recorded | BSD-3-Clause notice in [vendored header](nxnative/dm/third_party/flip/tool/tinyexr.h) |

`nvn.h` separately retains an MIT notice naming h1k421. Its precise original GitHub repository is not recorded in this snapshot, so no guessed repository is attributed; see the [header notice](nxnative/dm/gfx/nvn/include/nvn.h).

### Extraction, shader and build tools

| Package / GitHub source | Purpose | Local version or constraint | License / evidence |
|---|---|---|---|
| [LibHac — Thealexbarney/LibHac](https://github.com/Thealexbarney/LibHac) | NSP reading and base/update layering | NuGet 0.19.0 declared in [nx_extract.csproj](nxnative/dm/tools/nx_extract/nx_extract.csproj) | MIT package; historical GitHub URL returned 404 during link checking; [package page](https://www.nuget.org/packages/LibHac/0.19.0) |
| [SPIRV-Cross — KhronosGroup/SPIRV-Cross](https://github.com/KhronosGroup/SPIRV-Cross) | SPIR-V to Metal Shading Language | External command; exact installed revision not pinned in this README | Apache-2.0; upstream license applies |
| [Capstone — capstone-engine/capstone](https://github.com/capstone-engine/capstone) | ARM64 disassembly and rewriting support | Python package 5.0.9 observed locally | BSD-style Capstone license; see upstream LICENSE.TXT |
| [python-lz4 — python-lz4/python-lz4](https://github.com/python-lz4/python-lz4) | LZ4 decompression | Python package 4.4.5 observed locally | BSD bindings / bundled LZ4 license notices |
| [fontTools — fonttools/fonttools](https://github.com/fonttools/fonttools) | Nintendo button-symbol font generation | Python package 4.67.0 observed locally | MIT |
| [backports.zstd — rogdham/backports.zstd](https://github.com/rogdham/backports.zstd) | Zstandard support with Python before 3.14 | Python package 1.8.0 observed locally | PSF-2.0 package notice; bundled Zstandard retains its notices |
| [Zstandard — facebook/zstd](https://github.com/facebook/zstd) | External zstd command used by build tooling | External command; exact installed revision not pinned here | BSD-3-Clause OR GPL-2.0 upstream |
| [NSZ — nicoboss/nsz](https://github.com/nicoboss/nsz) | Preparation-only NSZ-to-NSP decompression; original NSZ retained locally | Python package 5.0.0 observed locally | See upstream LICENSE; not an app runtime component |
| [python-zstandard — indygreg/python-zstandard](https://github.com/indygreg/python-zstandard) | Python Zstandard support used in preparation tooling | Python package 0.25.0 observed locally | BSD-3-Clause package notice |
| [PyCryptodome — Legrandin/pycryptodome](https://github.com/Legrandin/pycryptodome) | Cryptographic operations in local preparation tooling | Installed distribution reports 4.1.0; package metadata, not a claim of upstream release status | Local metadata: BSD-2-Clause AND Unlicense AND MIT |
| [XcodeGen — yonaskolb/XcodeGen](https://github.com/yonaskolb/XcodeGen) | Generates the iOS Xcode project from project.yml | External build tool | MIT |
| [.NET — dotnet/sdk](https://github.com/dotnet/sdk) | Builds extraction and shader-translation tools | .NET SDK 10; net10.0 project targets | MIT SDK source; runtime/components keep their own notices |
| [Python — python/cpython](https://github.com/python/cpython) | Local build and packaging orchestration | Local virtual environment uses Python 3.13.0 | PSF license |
| [Homebrew — Homebrew/brew](https://github.com/Homebrew/brew) | Local tool installation | Build-environment tool | BSD-2-Clause |

Apple Xcode, the Apple platform SDKs, Metal, GameController, AVFoundation, UIKit/AppKit and CoreMotion are Apple platform dependencies. They do not have corresponding public GitHub source repositories to cite here; see [Xcode](https://developer.apple.com/xcode/) and [Apple documentation](https://developer.apple.com/documentation/). Apple SDK terms apply. They are not bundled open-source packages in this backup.

### .NET package references used by the vendored translator

The following references appear in the vendored Ryujinx.Common project. The versions are declarations from [Directory.Packages.props](nxnative/dm/third_party/ryujinx/Directory.Packages.props), not a complete resolved transitive dependency lock. The file includes declarations for upstream components not built here; those are not all dependencies of this port.

| Package / GitHub source | Declared version | Purpose / license |
|---|---|---|
| [Microsoft.IO.RecyclableMemoryStream — microsoft/Microsoft.IO.RecyclableMemoryStream](https://github.com/microsoft/Microsoft.IO.RecyclableMemoryStream) | 3.0.1 | Pooled streams; MIT |
| [MsgPack.Cli — msgpack/msgpack-cli](https://github.com/msgpack/msgpack-cli) | 1.0.1 | MessagePack serialization; Apache-2.0 |
| [Humanizer — Humanizr/Humanizer](https://github.com/Humanizr/Humanizer) | 3.0.10 | Formatting utilities; MIT |
| [Gommon — GreemDev/Gommon](https://github.com/GreemDev/Gommon) | 2.8.1.2 | Utility dependency; local NuGet metadata records commit 222084874ac473e02f27faeb10e540f926702976. License was not established from the retained notice; consult the [package metadata](https://www.nuget.org/packages/Gommon/2.8.1.2) |

### Reference projects and workflow guidance

- [Atmosphere-NX/Atmosphere](https://github.com/Atmosphere-NX/Atmosphere): Horizon synchronization semantics reference. Reference use does not mean the Atmosphere kernel is linked into this app.
- yuzu: credited by nxnative for Maxwell encodings/kernel cross-checks. A reliable current original GitHub URL is not established here; no unrelated mirror is substituted.
- [SciresM/hactool](https://github.com/SciresM/hactool): historical extraction-tool credit in nxnative, not the current LibHac extraction executable.
- [realskyrin/ns-game-apple-arm-port](https://github.com/realskyrin/ns-game-apple-arm-port): explicitly consulted as a reference for this port, including the native-port workflow, diagnostics and platform-validation approach. This reference is acknowledged separately from incorporated code; the skill itself is not copied into this repository.

For retained notices and detailed upstream modifications, see the [third-party inventory](nxnative/dm/third_party/README.md). No blanket MIT statement overrides a component's own license. Unrecorded revisions and unavailable source URLs are explicitly marked rather than guessed.

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
