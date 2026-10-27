# Generation notes

Mode: built-in image_gen. Date: 2026-10-27.

## Prompt set
The verbatim source document is [PROMPTS_SOURCE_2026-10-27.md](PROMPTS_SOURCE_2026-10-27.md).
Each concept call combined its primer and individual asset prompt. The primer's instruction to reply “Ready” was replaced with an instruction to generate that single asset. Aspect ratios and lighting directions were retained. Reference attachment placeholders were implemented using local reference-image inputs.

These notes describe prompt assembly and refinements; they are not a verbatim transcript of every generation call.

## Reference roles
- Palace: _reference/Istana_Negara_Jalan_Duta.jpg — exact architecture reference.
- PDRM: _reference/PDRM_uniform.jpg — uniform reference; unrelated parade embellishments were excluded.
- Army: _reference/Army_uniform.jpg and Army_pattern.jpg — uniform/camouflage references; no weapons, face paint, sunglasses or tactical gear.
- Su-30MKM: _reference/Su30MKM_detail.jpg — airframe and livery reference.
- C-130H: _reference/C130H.jpg and C130H_flight.jpg — airframe/livery and in-flight reference.
- Skyline: _reference/KL_skyline.jpg — building shapes/order reference.
- palace_wide.jpg and Su30MKM.jpg were inspected but not used as generation inputs.

## Refinements
Second variants targeted framing, neutral lighting, blank surfaces and source fidelity without adding new scene subjects.
- C2-C v3: straight arms at attention, hands visible and both officers within the frame.
- C2-E v3: tablet horizontal with its screen facing upward toward the researcher. v4 edited v3 to expand framing around shoulders and elbows.
- C1-E v3: full-figure clearance and separated hands. v4 edited v3 to move the hidden hand onto open soil, show all six hands separately and preserve people, clothing, sapling and lighting.

Every variation is retained; preferred candidates and unresolved deviations are recorded in ASSET_REVIEW.md.

