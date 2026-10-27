# CGSO 2026 photographic assets — generation review

Date: 27 October 2026

Generated **51 original PNG variations across all 23 asset IDs**: 22 required assets and the optional C3-H port. Every ID has 2–4 versions. All versions are retained in the requested folders.

This completes the generation pass, not final production approval. Four asset IDs fail the strict architecture/skyline preservation gate, and several others require detail review.

## Files and technical verification

| Folder | PNG files |
|---|---:|
| shared | 2 |
| C2 | 15 |
| C1 | 18 |
| C3 | 16 |
| Total | 51 |

All 51 files decoded successfully. There are 28 landscape images at 1536 × 1024 and 23 portrait images at 1024 × 1536, matching the requested 3:2 or 2:3 ratios. SHA-256 checks found no duplicate image files. See [asset-inventory.json](asset-inventory.json).

[Open the visual review gallery](ASSET_GALLERY.html). Click any thumbnail there to open its original PNG.

## Preferred candidates and exceptions

“Candidate” means a preferred option for the designer's review; it does not establish print readiness. “Detail review” records unresolved visible constraints. No generated palace or skyline variant is selected for production.

| ID | Asset | Preferred | Status | Review |
|---|---|---|---|---|
| S-1 | Blank flag fabric | [v2](shared/S-1_v2.png) | Candidate | Broad billowing folds and clean contrast. Map the exact flag vector later. |
| C2-A | Palace at blue hour | None | Replace with real photo | Both variants alter architectural details. Neither passes the exact-reference gate. Use the real palace source; it crops the outer wings, so a wider source is still needed if the whole building must appear. |
| C2-B | Classified dossier | [v2](C2/C2-B_v2.png) | Candidate | Better margins around folder, paper and ribbon. Blank emblem and label areas. |
| C2-C | Two security officers | [v3](C2/C2-C_v3.png) | Detail review | v3 improves straight arms and side clearance. Framing is wider than head-to-knees. Badges, insignia and camouflage remain approximate; verify before use. |
| C2-D | Three Su-30MKM jets | [v2](C2/C2-D_v2.png) | Detail review | v2 has three separated planes in a triangular V. v1 is an echelon rather than the requested V. Verify airframe and small markings against the reference. |
| C2-E | Cybersecurity researcher | [v4](C2/C2-E_v4.png) | Candidate | v4 corrects tablet orientation and restores shoulder/elbow clearance. Earlier variants have awkward screen direction or cropped framing. |
| C2-F | Student using phone | [v1](C2/C2-F_v1.png) | Detail review | v1 has the requested leftward orientation but little margin by the right shoulder. v2 has more space but turns the other way. |
| C1-A1 | Clear sky | [v2](C1/C1-A1_v2.png) | Candidate | v2 has more clear blue space and fewer clouds. |
| C1-A2 | Haze sky | [v2](C1/C1-A2_v2.png) | Candidate | Even haze plate without land or a distinct sun. |
| C1-B | Palace in daylight | None | Replace with real photo | Window, column and other architectural details drift from the reference. Use the real palace photograph and relight in Photoshop. |
| C1-C | Army soldier | [v2](C1/C1-C_v2.png) | Detail review | v2 adds the beret badge and keeps hands within frame. Uniform details and insignia require verification; reference photos do not establish current uniform standards. |
| C1-D | Environmental researcher | [v2](C1/C1-D_v2.png) | Detail review | Better framing and a clear abstract graph. Inspect tiny screen/button marks at final placement size and remove anything that reads as lettering. |
| C1-E | Youths planting a tree | [v4](C1/C1-E_v4.png) | Detail review | v4 shows all six hands separately with whole-figure framing. Soil contact still obscures some finger detail, so the strict 30-finger check is not certified. v1/v2 overlap hands; v3 hides one hand. |
| C1-F | Rainforest foliage | [v2](C1/C1-F_v2.png) | Candidate | Continuous bottom border with an irregular upper edge against dark forest. |
| C1-G | C-130H Hercules | [v1](C1/C1-G_v1.png) | Detail review | v1 shows four engines/propellers more clearly; v2 obscures an engine. Verify livery, geometry and markings before final use. |
| C3-A | Sunrise sky | [v1](C3/C3-A_v1.png) | Candidate | v1 has the cleaner sun shape. Both need restrained grading to match the composite. |
| C3-A2 | KL skyline | None | Replace with real photo | Landmark ordering is broadly retained, but facade and smaller-building details change. Use the real skyline source; its night lighting still needs the planned sunrise treatment. |
| C3-B | Palace at sunrise | None | Replace with real photo | Both alter architecture. Use the real palace photograph with non-generative relighting. |
| C3-C | Solar farm | [v2](C3/C3-C_v2.png) | Candidate | More restrained warmth and clearer rows than v1. |
| C3-D | Police officer at port | [v2](C3/C3-D_v2.png) | Detail review | Less invented adornment than v1 and good framing. Badge/cap details remain approximate and need verification. |
| C3-E | Renewable-energy engineer | [v2](C3/C3-E_v2.png) | Candidate | Both arms are within frame and the single solar cell reads clearly; v1 crops an arm. |
| C3-F | Young professionals | [v2](C3/C3-F_v2.png) | Candidate | Full figures, natural stride and more forward-looking gaze than v1. |
| C3-H | Port at sunrise (optional) | [v1](C3/C3-H_v1.png) | Detail review | Optional asset included. Inspect and retouch small hull markings that may read as invented text. |

## Required real-photo fallbacks

- C2-A, C1-B and C3-B: [Istana Negara source](_reference/Istana_Negara_Jalan_Duta.jpg). Preserve its real architecture and relight in Photoshop. This source cuts off the outer wings; do not extend them with invented architecture if the full-building requirement is enforced.
- C3-A2: [KL skyline source](_reference/KL_skyline.jpg). Preserve the real building shapes; sunrise relighting is still outstanding.
- [Reference credits and licenses](_reference/SOURCES.md) accompany all ten collected reference files. The police and army photographs are visual references, not verification of current uniform regulations.
- The file named `palace_wide.jpg` depicts the palace entrance gate at night, not a wider photograph of the palace. It was not used for generation.

## Execution and handoff

Built-in image generation was used, one image per call. Sequence: Shared → C2 → C1 → C3, followed by targeted corrections. Each call included its concept primer and asset prompt. This replaces the manual “new chat per concept” workflow while retaining each concept's lighting instructions. The built-in tool did not expose a separate High quality control; highest resolution was requested and the actual dimensions are recorded above.

The [source prompt set](PROMPTS_SOURCE_2026-10-27.md) is preserved with the [prompt assembly and refinement notes](GENERATION_NOTES.md). Supplied photographic references were used for architecture, uniforms, aircraft and skyline.

These are photographic source plates with their backgrounds intact. Cutouts, cover compositing, final colour matching, Photoshop/Topaz upscaling and print preparation have not been performed. C3 jets should reuse C2-D, flipped horizontally and regraded warm during compositing as specified; no separate jet generation was made for C3.

No standalone flags, emblems, text, roundels or graphic overlays were generated. The physical security-document decoration in C2-B follows its asset prompt. Existing design/template files were not edited.

