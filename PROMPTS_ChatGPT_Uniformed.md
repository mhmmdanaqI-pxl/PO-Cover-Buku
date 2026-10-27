# ChatGPT prompts: PDRM + Malaysian Army (v3, uniform-accurate)

These prompts regenerate the four uniformed figures on the covers so they pass as real photographs and their uniforms are correct:

| ID | Cover | Who | Replaces |
|---|---|---|---|
| UNI-C2-PDRM | C2 Keselamatan Dokumen | PDRM officer | police from `C2-C_v3` |
| UNI-C2-ARMY | C2 Keselamatan Dokumen | 10 Para soldier | soldier from `C2-C_v1` |
| UNI-C3-PDRM | C3 Ekonomi | PDRM officer | `C3-D_v2` |
| UNI-C1-ARMY | C1 Alam Sekitar | 10 Para soldier | `C1-C_v2` |

> **v3.1 (27 Oct, 19:45): use the two PDRM prompts in the "v3.1" section below, not the original v3 ones.** Zharief: *"cuba check google commercial baju utk PDRM."* The v3 police copied a 2013 parade photo: long-sleeved tunic and a leather cross strap. The uniform PDRM actually wears today (official PDRM infographic, 2024) has short sleeves and **no cross strap**. The two Army prompts are unchanged.

**Why the badges are left blank on purpose:** image generators always garble insignia, and that's what the client spotted ("logo mcm bukan PDRM"). So every cap and beret badge is generated as a **plain silver placeholder**, sized, angled and lit correctly. I then place the **real PDRM crest and the real 10 Para badge** on it, as I did on the current covers. Rank pips, medal ribbons and name text are left off for the same reason; they can be added later from CGSO's official reference.

These are still AI-generated people. For the final print run, official PDRM / Army photos remain the recommendation.

---

## What to attach (all in `assets/_reference/prompt_refs/`)

| File | What it is | Attach to |
|---|---|---|
| `REF_PDRM_uniform_officer.jpg` | Real PDRM officer: uniform, cap, cross strap, buttons | both PDRM prompts |
| `REF_Army_uniform_beret_camo.jpg` | Real 10 Para soldier: maroon beret and digital camouflage | both Army prompts |
| `../Army_pattern.jpg` | Close-up of the real Malaysian Army digital camouflage | both Army prompts |
| `POSE_C2_police.jpg` | Pose, angle and framing for C2's officer (face masked) | UNI-C2-PDRM |
| `POSE_C2_soldier.jpg` | Pose for C2's soldier (face masked) | UNI-C2-ARMY |
| `POSE_C3_police.jpg` | Pose for C3's officer (face masked) | UNI-C3-PDRM |
| `POSE_C1_soldier.jpg` | Pose for C1's soldier (face masked) | UNI-C1-ARMY |

The pose files are the current figures with their faces pixelated. They lock the body angle and framing to the cover layout, so the new person drops straight into place. The masked face makes sure ChatGPT invents a new person instead of copying the old one.

## How to use
1. Open **one new ChatGPT chat** (GPT-6 Astra, image quality **High**). Paste the **Primer** first and wait for "Ready".
2. Send the prompts one at a time with their attachments. Aspect ratio is **portrait 2:3** for all four.
3. Make **3–4 variations** of each. Choose the one that looks most like an ordinary press photo, not the most heroic one.
4. Fix small faults with **select-and-edit** using the fix prompts at the end. Don't regenerate the whole image for a badge; I replace badges anyway.
5. Download the **original PNG** and save it as `assets/uniformed/UNI-C2-PDRM_v1.png` (and `_v2`, `_v3` for alternates).
6. Check each pick against the **reject list** at 100% zoom.

**Never add:** cinematic, epic, hyperrealistic, ultra-detailed, 8K, masterpiece, dramatic, heroic. They push the model toward the AI look.

---

## Primer (paste first)
```text
I'm a designer compositing an A5 book cover for the Malaysian Government's security office (CGSO, Prime Minister's Department). In this chat I need separate photographs of Malaysian uniformed personnel: officers of the Royal Malaysia Police (PDRM) and soldiers of the Malaysian Army's 10th Parachute Brigade. I will cut each person out and composite them myself.

REALISM RULES (most important):
1. Each image must be indistinguishable from an unretouched photograph by a professional Malaysian press photographer. Shot on a Canon EOS R5 with an 85mm f/1.4 lens at f/2.8, ISO 400, 1/250s. Faint natural sensor grain. Focus on the eyes.
2. Real, ordinary Malaysian men, not models and not idealised. Natural skin with visible pores, fine lines, slight unevenness, a few small blemishes and natural asymmetry; real teeth if visible; short hair with natural texture. Calm, serious, professional expressions caught mid-moment. Never aggressive, never posed stock-photo smiles. Every image in this chat is a DIFFERENT person; never reuse a face.
3. Neutral processing like a straight RAW file: true-to-life colour, neutral white balance, normal contrast. No HDR, no glow or bloom, no colour grade, no airbrushing, no over-sharpening, no glowing rim outline around the person.
4. Physically correct light from the direction I give in each prompt, with natural falloff and soft shadows. One light setup per image.
5. Correct anatomy: five fingers per hand, relaxed natural hands, both eyes looking at the same point, both ears matching.
6. Uniform accuracy matters more than anything else. Copy the uniform from the reference photo I attach: colour, cut, pockets, flaps, buttons, straps and how the headwear sits. Fabric is real cotton-poly with real creases, seams, stitching and slight wear, and it follows the body's folds. Pressed, clean, regulation-neat.
7. Insignia rule: every badge is a PLAIN PLACEHOLDER with no emblem, no lettering and no fine detail. I will add the official insignia myself. No rank pips, no medal ribbons, no shoulder patches, no name text, no numbers anywhere. Never invent a crest.
8. Pose reference rule: when I attach a grey-background pose image, match its body angle, head turn, arm position, framing and crop exactly. Its face is pixelated on purpose: create a completely new person, never the pixelated face.
9. Ignore everything in the uniform references that isn't the uniform: crowds, marching, parade gloves, face paint, sunglasses, headsets, weapons, vests and webbing. Nobody holds or carries a weapon.
10. Photograph each person on location with the background softly out of focus (f/2.8 bokeh), clearly separated from the person in tone so I can cut them out cleanly. No other people in frame.

Don't generate anything yet. Reply "Ready".
```

---

## v3.1: PDRM in the current working uniform (use these)

**What PDRM wears today** (official PDRM infographic *"Seragam Sang Saka Biru"* and the 2024 *tuck in / tuck out* explainer):

| | **Tuck in** (working uniform, rank and file) | **Tuck out** (No. 5 bush jacket, *Pegawai Kanan*) |
|---|---|---|
| Shirt | Very dark navy ("biru hitam"), **short sleeves**, tucked in | Very dark navy, **short sleeves**, worn **untucked** |
| Pockets | 2 chest pockets with buttoned flaps | 4 pockets (2 chest, 2 lower) with buttoned flaps |
| Buttons | Silver | **6 large silver buttons** down the front |
| Belt | Black belt with a **large round silver buckle** (PDRM crest) | No belt |
| Shoulders | Navy epaulettes with rank | **Black** epaulettes with rank |
| Also | Collar crests, round crest badge and name tag on the chest, whistle chain | Collar crests, ribbon bar, round crest badge, name tag, whistle chain |
| Cap | Navy peaked cap, black peak (officers: silver braid on the peak) | Same |
| **Never** | Cross strap, long sleeves, white gloves | Same |

**Recommended:** C3 (port duty) gets the **tuck-in** working uniform, the one most people see on the street. C2 (palace) gets the **tuck-out** senior-officer jacket. Both are current, and between them the two covers show the PDRM's range.

**Attach:** only the pose reference. **Don't** attach `REF_PDRM_uniform_officer.jpg`; that's the 2013 parade photo that caused the cross strap. If you have the PDRM infographic or the tuck in / tuck out photo on your screen, you may attach a screenshot as an extra reference (for generation only, never used on the cover).

Paste this first in the same chat (or after the Primer in a new chat):
```text
Correction for the Royal Malaysia Police (PDRM) images: ignore the earlier PDRM reference photo; it shows an old parade uniform. Use the current PDRM working uniform exactly as I describe it in each prompt. Short sleeves only. Absolutely no cross strap, no Sam Browne belt, no shoulder strap across the chest, no long sleeves, no white gloves. All badges stay plain blank silver placeholders as before. Reply "Ready".
```

### UNI-C3-PDRM v3.1 🔴 PDRM officer, tuck-in working uniform, C3 (sunrise) · 2:3
**Attach:** `POSE_C3_police.jpg`
```text
Real photograph of a Royal Malaysia Police (PDRM) officer on duty at a Malaysian container port at sunrise.

Person: an ordinary Malay man in his early 30s, clean-shaven, slightly rounded face, short neat black hair, medium-brown skin with natural texture. Calm, watchful, professional expression.

Uniform, the current PDRM working uniform worn tucked in: very dark navy-blue ("biru hitam", almost black) SHORT-SLEEVED shirt of smooth uniform fabric, tucked into matching very dark navy trousers with a sharp crease. Two chest pockets with buttoned flaps and polished silver buttons; silver buttons down the front; navy shoulder epaulettes each with a silver button and NO rank insignia; collar open at the neck with a plain white crew-neck undershirt just visible. On the chest: a small plain round polished-silver badge above the left pocket and a plain blank silver name plate above the right pocket. A thin silver whistle chain from the left pocket button. A black leather belt with a LARGE ROUND polished-silver buckle plate, completely blank. Collar badges: two small plain silver pins. Peaked cap: very dark navy crown, glossy black peak with silver braid along the peak, sitting level; cap badge a PLAIN smooth polished-silver oval plate, no emblem. NO cross strap, no shoulder strap, no long sleeves, no medal ribbons, no ID lanyard, no text anywhere.

Pose and framing: match the attached pose reference exactly: body facing the camera with a slight turn, head turned with his gaze into the distance as in the reference, arms relaxed at his sides. Framed from just above the cap to mid-thigh, camera at chest height, slightly low.

Light: early sunrise with the low sun BEHIND-RIGHT, giving a natural warm edge light on the right side of his cap, cheek, shoulder and arm; soft cool skylight fill from the front-left. Face properly exposed, not a silhouette. Background: port cranes and stacked containers in warm morning haze, softly out of focus and clearly lighter than the dark uniform.

Canon EOS R5, 85mm, f/2.8, ISO 400. Neutral, unretouched processing. Portrait 2:3, highest resolution.
```

### UNI-C2-PDRM v3.1 🔴 PDRM senior officer, tuck-out bush jacket, C2 (blue hour) · 2:3
**Attach:** `POSE_C2_police.jpg`
```text
Real photograph of a Royal Malaysia Police (PDRM) senior officer on guard duty in the forecourt of a Malaysian government building at blue hour, just after sunset.

Person: an ordinary Malay man of about 40, square jaw, short neat black hair with a little grey at the temples, a neatly trimmed moustache, medium-brown skin with natural texture. Calm, alert, dignified expression.

Uniform, the current PDRM senior officer's working jacket worn untucked ("tuck out", Pakaian Seragam Kerja No. 5): a very dark navy-blue ("biru hitam", almost black) SHORT-SLEEVED bush jacket worn outside the trousers, hem at the hip. Four pockets with buttoned flaps (two chest pockets, two lower hip pockets), six large polished-silver buttons down the front, short sleeves with a neat hem. BLACK shoulder epaulettes, plain, NO rank insignia. Collar open at the neck with a plain white crew-neck undershirt just visible. On the chest: a small plain round polished-silver badge on the left pocket and a plain blank silver name plate above the right pocket. A thin silver whistle chain from the left pocket button. No belt visible over the jacket. Matching very dark navy trousers with a sharp crease. Collar badges: two small plain silver pins. Peaked cap: very dark navy crown, glossy black peak with silver braid along the peak, sitting level; cap badge a PLAIN smooth polished-silver oval plate, no emblem. NO cross strap, no shoulder strap, no long sleeves, no medal ribbons, no ID lanyard, no text anywhere.

Pose and framing: match the attached pose reference exactly: standing at attention, body turned 3/4 as in the reference, arms straight at his sides, hands relaxed. Framed from just above the cap to just below the knees, camera at chest height, slightly low.

Light: soft cool blue-hour ambient light from above and in front, plus a gentle warm floodlight from BEHIND-LEFT that gives a subtle warm edge on his left shoulder, cap and cheek. Face properly exposed and readable, not a silhouette. Background: the building's warm-lit cream façade and columns, softly out of focus and clearly lighter than the dark uniform.

Canon EOS R5, 85mm, f/2.8, ISO 400. Neutral, unretouched processing. Portrait 2:3, highest resolution.
```

**Save as** `assets/uniformed/UNI-C3-PDRM_v2.png` and `assets/uniformed/UNI-C2-PDRM_v3.png`.
**Reject if:** any strap across the chest; long sleeves; the C3 shirt untucked or the C2 jacket tucked in; buckle or badges with a design or text; a uniform that reads bright blue instead of near-black navy.

---

## (v3, superseded) UNI-C2-PDRM 🔴 PDRM officer, C2 (blue hour) · 2:3
**Attach:** `REF_PDRM_uniform_officer.jpg` + `POSE_C2_police.jpg`
```text
Real photograph of a Royal Malaysia Police (PDRM) officer on guard duty in the forecourt of a Malaysian government building at blue hour, just after sunset.

Person: an ordinary Malay man of about 40, square jaw, short neat black hair with a little grey at the temples, a neatly trimmed moustache, medium-brown skin with natural texture. Calm, alert, dignified expression.

Uniform, copied from the attached PDRM reference: dark navy-blue (almost black-navy) long-sleeved uniform shirt and matching trousers with a sharp crease; two chest pockets with buttoned flaps and polished silver buttons; plain shoulder epaulettes with a silver button and NO rank insignia; open collar showing a white crew-neck undershirt; the black leather cross strap over the chest with a short silver whistle chain to the breast pocket, as in the reference; black leather belt with a plain silver buckle. Peaked cap exactly as in the reference: dark navy crown, glossy black peak with the silver braid along it, sitting level and straight. Cap badge: a PLAIN, smooth, polished-silver oval plate about the size of a thumb, centred on the front of the cap, no emblem and no text. Collar badges: two small plain silver pins. Name plate: a plain silver bar with nothing on it. No medal ribbons.

Pose and framing: match the attached pose reference exactly. Standing at attention, body turned 3/4 toward the RIGHT of frame, arms straight at his sides, hands relaxed. Framed from just above the cap to just below the knees, camera at chest height, slightly low.

Light: soft cool blue-hour ambient light from above and in front, plus a gentle warm floodlight from BEHIND-LEFT that gives a subtle warm edge on his left shoulder, cap and cheek. Face properly exposed and readable, not a silhouette. Background: the building's warm-lit cream façade and columns, softly out of focus and clearly lighter than the dark uniform.

Canon EOS R5, 85mm, f/2.8, ISO 400. Neutral, unretouched processing. Portrait 2:3, highest resolution.
```

## UNI-C2-ARMY 🔴 10 Para soldier, C2 (blue hour) · 2:3
**Attach:** `REF_Army_uniform_beret_camo.jpg` + `Army_pattern.jpg` + `POSE_C2_soldier.jpg`
```text
Real photograph of a Malaysian Army soldier of the 10th Parachute Brigade standing guard in the forecourt of a Malaysian government building at blue hour.

Person: an ordinary Malay man in his early 30s, broad face, thick straight eyebrows, a faint shadow of stubble, short military haircut, medium-brown skin with natural texture. A different person from any officer generated earlier in this chat. Calm, steady, serious expression.

Uniform, copied from the attached references: the current Malaysian Army digital camouflage combat uniform, the pixel pattern matching the attached camouflage close-up exactly (small square pixels in dark green, mid green, khaki-tan, brown and black), identical on shirt and trousers and following every fold without smearing. Shirt with two chest pockets with buttoned flaps, shoulder straps, sleeves down and buttoned, open collar showing an olive-green T-shirt; black belt with a plain buckle. Name tape above the right pocket: a blank camouflage tape with no letters. Plain sleeves, no shoulder patches.

Maroon beret, as in the reference: deep maroon wool felt with a black leather headband sitting level about two fingers above the eyebrows, the crown shaped down over his RIGHT ear. Above his LEFT eye, on the headband: a small black inverted-triangle felt backing (point down) with a plain flat silver shape on it, no wings, no emblem, no detail.

No weapon, no sunglasses, no face paint, no headset, no vest, no gloves.

Pose and framing: match the attached pose reference exactly. Standing upright, body turned 3/4 toward the LEFT of frame, head turned slightly further left, arms at his sides. Framed from just above the beret to upper thigh, camera at chest height.

Light: soft cool blue-hour ambient light from above and in front, plus a gentle warm floodlight from BEHIND-LEFT giving a subtle warm edge on the beret and left shoulder. Face properly exposed. Background: the warm-lit cream façade of the building, softly out of focus, clearly lighter than the uniform.

Canon EOS R5, 85mm, f/2.8, ISO 400. Neutral, unretouched processing. Portrait 2:3, highest resolution.
```

## (v3, superseded) UNI-C3-PDRM 🔴 PDRM officer, C3 (sunrise) · 2:3
**Attach:** `REF_PDRM_uniform_officer.jpg` + `POSE_C3_police.jpg`
```text
Real photograph of a Royal Malaysia Police (PDRM) officer on duty at a Malaysian container port at sunrise.

Person: an ordinary Malay man in his early 30s, clean-shaven, slightly rounded face, short neat black hair, medium-brown skin with natural texture. A different person from any officer generated earlier in this chat. Calm, watchful, professional expression.

Uniform, copied from the attached PDRM reference: dark navy-blue (almost black-navy) uniform shirt and matching trousers; two chest pockets with buttoned flaps and polished silver buttons; plain shoulder epaulettes with a silver button and NO rank insignia; open collar showing a white crew-neck undershirt; the black leather cross strap and short silver whistle chain as in the reference; black leather duty belt with a plain silver buckle. Peaked cap exactly as in the reference: dark navy crown, glossy black peak with the silver braid along it, sitting level. Cap badge: a PLAIN, smooth, polished-silver oval plate, centred on the front of the cap, no emblem and no text. Collar badges: two small plain silver pins. Name plate: a plain silver bar with nothing on it. No medal ribbons.

Pose and framing: match the attached pose reference exactly. Standing in a calm, alert stance, body facing the camera with a slight turn, head turned toward the RIGHT of frame, gazing into the distance. Framed from just above the cap to mid-thigh, camera at chest height, slightly low.

Light: early sunrise with the low sun BEHIND-RIGHT, giving a natural warm edge light on the right side of his cap, cheek and shoulder; soft cool skylight fill from the front-left. Face properly exposed, not a silhouette. Background: port cranes and stacked containers in warm morning haze, softly out of focus and clearly lighter than the dark uniform.

Canon EOS R5, 85mm, f/2.8, ISO 400. Neutral, unretouched processing. Portrait 2:3, highest resolution.
```

## UNI-C1-ARMY 🔴 10 Para soldier, C1 (late morning) · 2:3
**Attach:** `REF_Army_uniform_beret_camo.jpg` + `Army_pattern.jpg` + `POSE_C1_soldier.jpg`
```text
Real photograph of a Malaysian Army soldier of the 10th Parachute Brigade standing on a green parade field on a clear late morning.

Person: an ordinary Malay man in his mid-20s, lean face with high cheekbones, clean-shaven, short military haircut, medium-brown skin with natural texture. A different person from any soldier generated earlier in this chat. Quiet, determined, warm expression.

Uniform, copied from the attached references: the current Malaysian Army digital camouflage combat uniform, the pixel pattern matching the attached camouflage close-up exactly (small square pixels in dark green, mid green, khaki-tan, brown and black), identical on shirt and trousers and following every fold without smearing. Shirt with two chest pockets with buttoned flaps, shoulder straps, sleeves down and buttoned, open collar showing an olive-green T-shirt. Name tape above the right pocket: a blank camouflage tape with no letters. Plain sleeves, no shoulder patches.

Maroon beret, as in the reference: deep maroon wool felt with a black leather headband sitting level about two fingers above the eyebrows, the crown shaped down over his RIGHT ear. Above his LEFT eye, on the headband: a small black inverted-triangle felt backing (point down) with a plain flat silver shape on it, no wings, no emblem, no detail.

No weapon, no sunglasses, no face paint, no headset, no vest, no gloves.

Pose and framing: match the attached pose reference exactly. Standing tall and relaxed, body turned 3/4 toward the RIGHT of frame, eyes lifted slightly toward the light. Framed from just above the beret to mid-thigh, camera at chest height, slightly low.

Light: bright late-morning tropical sun from the UPPER RIGHT (about 2 o'clock, 45° high) with crisp but soft-edged natural shadows; soft natural fill from the left. Background: trees at the edge of the field, softly out of focus, lighter and greener than the uniform.

Canon EOS R5, 85mm, f/2.8, ISO 200. Neutral, unretouched processing. Portrait 2:3, highest resolution.
```

---

## Fix prompts (select the area first, then send)
- **Badge has a design or text:** `Replace the selected badge with a plain, smooth, polished-silver oval plate of the same size, position, angle and lighting. No emblem, no text, no detail.`
- **10 Para backing wrong:** `Replace the selected beret badge with a small black inverted-triangle felt patch, point down, with a plain flat silver shape on it. Same size, position and lighting. No emblem, no detail.`
- **Rank pips or ribbons appeared:** `Remove the selected rank insignia / ribbons. Plain navy fabric with the same creases and lighting.`
- **Writing on a name tag:** `Make the selected name tag completely blank, same material and lighting.`
- **Camouflage smeared or blotchy:** `Redo the selected camouflage so it is the crisp Malaysian Army digital pixel pattern from the reference, following the fabric folds. Change nothing else.`
- **Hand wrong:** `Fix the selected hand: five fingers, natural relaxed pose, matching skin and lighting.`
- **Skin too smooth:** `Make the selected skin look like an unretouched photo: visible pores, fine lines, slight unevenness. Same person, same lighting.`

## Reject list (check at 100% zoom)
**Any image**
- [ ] Waxy or poreless skin, a model-like face, or the same face as another figure on the covers
- [ ] Mismatched eyes or catchlights, odd teeth, extra or melted fingers
- [ ] Glowing outline around the person, HDR halos, a built-in colour grade
- [ ] Any text, letters or numbers anywhere
- [ ] Light coming from the wrong side for that cover

**PDRM**
- [ ] Uniform reads as black or bright blue instead of the reference navy
- [ ] Cap crown floppy or tilted; peak not glossy black; braid missing or invented
- [ ] Buttons or pocket flaps that don't match left to right; the cross strap breaks or vanishes
- [ ] White gloves, parade lanyards or a weapon (they came from the reference crowd)

**Army**
- [ ] Camouflage that isn't the pixel pattern of `Army_pattern.jpg`, or smears, repeats, or changes between shirt and trousers
- [ ] Beret worn like a cap, pulled to the wrong side, or not maroon
- [ ] Badge on the wrong side, or a crest / wings drawn on it
- [ ] Shoulder patches, flags or tapes with writing
- [ ] Face paint, sunglasses, headset, vest or weapon (they came from the reference photo)

---

## After you save them
Tell me which files you picked. I will:
1. Cut each person out (BiRefNet plus edge clean-up) and check the face, hands and uniform at 200%.
2. Put the **real PDRM crest** on the cap and collar and the **real 10 Para badge** on the beret, warped to the surface and matched to the photo's light (`_scripts/insignia.py`).
3. Drop each one into its exact place on the cover using the pose match, then grade to the cover's light, shade the lower body into the base, and add contact shadows and grain.
4. Re-export the covers, layered PSDs, CMYK press PDFs, mockups and deck, then repackage the Drive folder.
