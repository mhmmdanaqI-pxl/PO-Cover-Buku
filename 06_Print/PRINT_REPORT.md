# CGSO 2026 covers: print report

**Send these to the printer:** `CGSO2026_C1/C2/C3_PRINT_CMYK_FOGRA39.pdf` (this folder).
The RGB `*_SCREEN_RGB.pdf` files in `04_Final/` are for screen review only.

## File spec
| Item | Value |
|---|---|
| Size | 154 × 216 mm page = A5 148 × 210 mm + 3 mm bleed; TrimBox and BleedBox set |
| Colour | CMYK only. Output intent: **FOGRA39** (offset, coated paper), profile `Coated_Fogra39L_VIGC_300.icc` embedded. Artwork and vectors are untagged DeviceCMYK, so the output intent alone governs them (no other ICC profile in the file) |
| Artwork | One flattened image per cover at 300 ppi, CMYK, lossless (Flate) |
| Vectors on top | Jata Negara, office block, headline, roundel. All text is converted to outlines (no fonts needed) |
| Conversion | sRGB → FOGRA39, relative colorimetric + black point compensation |

## Checks
| Cover | Max total ink (limit 300%) | Colour shift screen → print (ΔE2000) | Pixels shifting > 6 ΔE | RGB left in file |
|---|---|---|---|---|
| C1 Alam Sekitar | **285%** | mean 0.70, 95th pct 3.14 | 0.03% | none |
| C2 Keselamatan Dokumen | **285%** | mean 0.76, 95th pct 1.81 | 0.00% | none |
| C3 Ekonomi | **285%** | mean 0.62, 95th pct 2.53 | 0.00% | none |

A ΔE under ~2 can't be seen. The only noticeable shift is C1's brightest sky blue and the cyan headline accent, which print slightly less saturated. You can see it in `C1_screen_vs_print.jpg`, and the magenta areas in `C*_gamut_warning.jpg` mark where it happens.

## Vector colour builds
| Element | CMYK |
|---|---|
| White text, Jata white | 0 / 0 / 0 / 0 (paper) |
| Jata black linework | 0 / 0 / 0 / **100 K**, so the fine lines can't fringe from plate misregistration |
| Jata yellow | 0 / 0 / 89 / 0 |
| Jata red | 0 / 86 / 82 / 0 |
| Jata green | 79 / 0 / 87 / 0 |
| Jata blue | 78 / 38 / 0 / 0 |
| C2 headline gold | 8 / 22 / 76 / 7 |
| Roundel red | **0 / 90.5 / 96.1 / 0**, the designer's original CMYK values, kept exactly |

Solids are cleaned: any ink under 5% inside a strong colour is set to zero, so there's no faint dot pattern in flat areas.

**Overprint and layers:** all white text knocks out (0/0/0/0, no overprint). The only overprint in the files is the Jata's 100% K linework, as set in the supplied Jata artwork, which prevents white gaps if the plates shift. The files contain no optional-content layers.

**Smallest type:** the office block is Roboto Regular, white, knocked out of four colours. The stem is 0.27 mm at 8.5 pt and 0.24 mm at 7.5 pt (www.cgso.gov.my). That's above the usual 0.2 mm minimum for coated offset, but check registration on the proof.

## Effective resolution: is upscaling needed? **No.**
Every element is rendered into a single 300 ppi image. This is each element's own source resolution as placed:

| Element | Effective ppi |
|---|---|
| People (all covers) | 380–530 |
| Aircraft | 610–890 |
| Istana Negara (real photo) | 457–486 |
| Jalur Gemilang (exact vector on fabric, 2x) | ~410 |
| Guilloche, microtext, growth line, arc | vector-sourced (300+) |
| C2 dossier | 244 |
| C3 solar base | 241 |
| C1 rainforest base | 214 |
| C1 / C3 sky plates | 169 |
| C3 port silhouette (blurred, darkened) | 171 |

The only sources below 300 ppi are smooth skies, a deliberately blurred silhouette, and dark foreground under the headline. None has fine detail that printing would reveal, and the cover-wide film grain is rendered at 300 ppi on top. An AI upscaler would add no real detail; it would only invent texture in clouds and leaves, which is exactly the "AI look" we've been avoiding. The printer's preflight sees one 300 ppi image, so there are no low-resolution warnings.

## Soft proofs in this folder
- `C*_softproof_FOGRA39.jpg`: the full cover as it should look on coated paper, with paper white simulated.
- `C*_screen_vs_print.jpg`: screen version (left) next to the print simulation (right).
- `C*_gamut_warning.jpg`: magenta marks where the print differs from screen by more than ΔE 6.

## Still to confirm with the printer
1. **Press condition:** is their coated offset press FOGRA39? If they use Japan Color 2001 or another condition, the files can be rebuilt for it in about a minute.
2. **Corner radius:** about 6 mm is assumed, and everything important is 10 mm inside the trim.
3. **Hard proof:** ask for a contract proof or a press proof before the full run.
4. **Small white text:** the office block is 7.5–8.5 pt white, knocked out of a four-colour background. That's standard, but ask them to check registration.

The files aren't certified PDF/X. They're built to PDF/X-4 requirements (CMYK only, output intent, Trim/BleedBox, no fonts), but no preflight tool has validated them here.
