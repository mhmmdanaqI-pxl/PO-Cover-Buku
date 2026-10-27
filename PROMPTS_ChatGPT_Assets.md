# ChatGPT Asset Prompts — CGSO 2026 Covers (v2: real-photo realism)

## The rule: every asset must pass as a real photograph
The client is a government security office. One fake-looking face or melted badge will sink the whole pitch, and Team B's AI-looking children were part of why they lost. So these prompts push hard on realism:

- **Real cameras and lenses.** Each primer names the body, lens, aperture and ISO, which pulls the model toward photographic rendering.
- **Ordinary people, not models.** Skin with pores, natural asymmetry, real fabric creases, candid moments.
- **Neutral processing.** No HDR, glow, "cinematic" grade or airbrushing. Assets come out like unretouched RAW files and we grade all of them together in Photoshop. Mismatched built-in grades are the biggest giveaway of an AI composite.
- **Subtle light.** One physically correct light source per concept. No glowing halo outlines around people.
- **People shot on location, not on grey.** Subjects are photographed in a real setting with a soft, out-of-focus background and the right light, then cut out with Select Subject. They pick up natural light spill, so they don't look pasted in.
- **No clichés.** The glowing fingerprint and light-ribbon prompts are gone. I'll build any graphic overlay as a precise vector.

**Never add** words like *cinematic, epic, hyperrealistic, ultra-detailed, 8K, masterpiece, dramatic*. They push the model toward the AI look.

---

## How to use
1. **One new ChatGPT chat per concept.** Paste that concept's **Primer** first, then the asset prompts one at a time.
2. Set quality to **High** and pick the aspect ratio listed (it's also written in each prompt).
3. Make 2–4 variations. **Choose the one that looks most like an ordinary photo**, not the most dramatic one. Fix small faults with ChatGPT's select-and-edit.
4. Download the **original PNG**, not a screenshot. Save it as `assets/<folder>/<ID>_v1.png`, e.g. `assets/C2/C2-C_v1.png`.
5. Upscale only with Photoshop **Camera Raw → Enhance → Super Resolution**, or Topaz with creativity/recovery set to low. High-creativity "generative" upscalers invent texture and bring the AI look back.
6. **Order:** Shared → C2 → C1 → C3.
7. 🔴 = must have · ⚪ = nice to have · 📎 = attach a reference photo with the prompt.

### References to collect into `assets/_reference/` first
| For | What to find |
|---|---|
| Istana Negara | Sharp, straight-on front photo of **Istana Negara, Jalan Duta** (Wikimedia Commons is a safe source) |
| Police | PDRM officer in the dark-blue uniform with peaked cap, front or 3/4 view |
| Army | Malaysian Army soldier in the current digital camouflage + beret |
| C1 aircraft | RMAF **C-130H Hercules** in flight |
| C2/C3 aircraft | RMAF **Su-30MKM** in flight |
| C3 skyline | Kuala Lumpur skyline photo that shows **Merdeka 118** and the **Petronas Twin Towers** |

### Don't generate these (I'll build them exactly)
Jalur Gemilang vector, guilloche + microtext (C2), rising gold line + protective arc (C3), any scan-line or graphic overlay, all text, Jata Negara, roundel.

### Reject the image if you see any of these AI tells (check at 100% zoom)
- [ ] Waxy, airbrushed or poreless skin; everyone looking like a model; all faces the same age or skin tone
- [ ] Eyes with mismatched catchlights, a drifting gaze or odd irises; teeth too uniform or too many
- [ ] Wrong finger count, rubbery hands, mismatched earrings, a tudung that melts into the neck
- [ ] Camouflage pattern that smears or repeats oddly; buttons, pockets or epaulettes that don't line up; garbled badge or insignia
- [ ] Hair dissolving into the background
- [ ] Shadows that don't match the light, double shadows, or a glowing outline around the subject
- [ ] HDR halos, over-saturated colours, plastic sheen
- [ ] Background objects that morph or make no sense; any gibberish text

---

## Shared

### S-1 🔴 Flag fabric (for an exact Jalur Gemilang) · 3:2
AI almost always gets the flag wrong (stripe count, 14-point star). So generate blank fabric. I'll map the exact vector flag onto it with Photoshop's Displace filter, which gives a real-looking flag that's 100% correct.
```text
Real studio photograph of a large plain white polyester flag billowing in strong wind from a fan, attached along its left edge (no pole visible), flowing to the right with deep, natural folds and ripples across the whole surface and slight fraying at the free edge. Shot on a Canon EOS R5 with a 50mm lens at f/8, ISO 200. One soft light from above, so the folds show clear but natural highlights and shadows. Plain white fabric with no pattern, no colour and no text. Pure black background. Neutral, unretouched processing. Landscape 3:2, highest resolution.
```
**Check:** folds run across the whole sheet; no hard creases at the corners; clean edges against the black.

---

## Concept 2 — Keselamatan Dokumen (build first)

### Primer (paste first in a new chat)
```text
I'm a designer compositing an A5 book cover for the Malaysian Government's security office. Theme: national sovereignty protected through document security. Every image in this chat is a separate photographic asset I will cut out and combine in Photoshop.

REALISM RULES (most important):
1. Each image must be indistinguishable from a real photograph by a professional Malaysian press/commercial photographer. Shot on a Canon EOS R5. People: 85mm lens, f/2.8, ISO 400. Architecture and objects: 24–100mm, f/8. Faint natural sensor grain.
2. Real, ordinary Malaysians, not models and not idealised. Natural skin with pores, fine lines, slight unevenness and natural asymmetry; real teeth; a few flyaway hairs; fabric with real creases, seams and wear. Candid, mid-moment expressions, not posed stock-photo smiles.
3. Neutral, unretouched processing like a straight RAW file: true-to-life colour, neutral white balance, normal contrast. No HDR, no glow or bloom, no teal-orange grade, no airbrushing, no over-sharpening, no "cinematic" look. I will grade everything together later.
4. Physically correct light with natural falloff and soft shadows. Lighting for this whole set: blue hour just after sunset. Soft cool ambient light from above-front, plus gentle warm light from behind-left (like building floodlights) giving a subtle warm edge on hair and shoulders. Subtle, never a glowing outline.
5. Correct anatomy: five fingers per hand, natural hand poses, both eyes looking at the same point, matching earrings, symmetrical uniform details.
6. No text, letters, numbers, logos or watermarks anywhere. Name tags, ID cards and screens stay blank or abstract. If unsure about a badge or patch, keep it small and simple rather than inventing details.
7. Photograph people on location in a plausible real setting with the background softly out of focus. I will cut them out myself.

Don't generate anything yet. Reply "Ready".
```

### C2-A 🔴📎 Istana Negara at blue hour · 3:2
```text
[Attach the Istana Negara reference photo]
Using the attached photo as the exact architectural reference, produce a real architectural photograph of this same building, Istana Negara at Jalan Duta, Kuala Lumpur. Preserve the architecture exactly: the large central golden dome with its chevron pattern, the smaller golden domes, the cream façade, columns, arched windows, proportions and the number of domes. Do not add, remove or redesign anything. Change only the time of day: blue hour just after sunset, a clean deep-blue sky with no clouds, the building lit by its own warm floodlights so the golden domes glow gold and the façade reads warm cream, with realistic light falloff and some areas in shadow. Shot straight-on with a 24mm tilt-shift lens at f/8, so the verticals stay straight; whole building in frame with space around it; empty flagpoles. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** compare dome by dome with the real photo. If anything differs, **use the real photo** and relight it in Photoshop instead. The client will notice a wrong palace.

### C2-B 🔴 Classified dossier (hero object) · 3:2
```text
Commercial product photograph of a Malaysian government confidential dossier, shot from a 3/4 overhead angle with a 100mm macro lens at f/11. A closed deep navy-blue bookcloth hardcover file folder with fine gold-foil edging, real cloth texture and slight wear on the corners, lying at a slight angle on a plain dark navy surface with a soft natural contact shadow. On the folder cover: a blank debossed circular area at top centre (an emblem will be added later) and a blank rectangular label area. Sliding partly out of the folder: two ivory security documents on textured paper with visible fibres, printed with fine-line guilloche engraving in gold and blue like a passport page, a narrow holographic security strip with subtle, realistic iridescence, and a red cotton ribbon tie. Absolutely no text, letters or numbers. Blue-hour lighting per the chat rules. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** no fake text anywhere; the emblem area is truly blank (the real Jata goes there); the paper looks like paper, not plastic.

### C2-C 🔴📎 Two security officers on guard · 2:3
```text
[Attach the PDRM and Malaysian Army uniform references]
Real photograph of two Malaysian security personnel standing side by side on guard in the forecourt of a government building at blue hour, the building's warm lights softly out of focus behind them. Left: a Royal Malaysia Police (PDRM) officer, an ordinary Malay man in his late 30s, in the dark-blue PDRM uniform and peaked cap exactly as in the reference. Right: a Malaysian Army soldier, an ordinary Malay man in his late 20s, in the current Malaysian Army digital-camouflage uniform and beret exactly as in the reference. Both stand at attention, bodies turned 3/4 toward the left of frame, calm, alert and serious, not aggressive. No weapons. Framed from head to knees from a slightly low camera position. Real uniform fabric with creases and stitching; name tags blank; insignia simple and accurate. Lighting per the chat rules. Shot at 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```
**Check:** uniform colours, cap/beret badges and shoulder patches match the references; the camouflage pattern doesn't smear; hands are correct.

### C2-D 🔴📎 Fighter jets in formation · 3:2
```text
[Attach the RMAF Su-30MKM reference]
Air-to-air photograph, taken from a chase plane with a 200mm lens at 1/500s, of three Royal Malaysian Air Force Sukhoi Su-30MKM fighter jets in a tight V formation, climbing toward the upper right, seen from a 3/4 low angle. Grey camouflage as in the reference, with real panel lines and slight weathering, faint heat shimmer behind the engines and no afterburner flames. Small national roundels only, no readable serials or text. Plain deep-blue dusk sky with no clouds. Gentle warm light from behind-left catches the upper fuselages. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** each jet has twin tails, canards and two engines; all three are the same type and in plausible formation spacing.
*Also used for C3:* flip it horizontally and regrade it warm, so there's no second jet generation.

### C2-E 🔴 Cybersecurity researcher · 2:3
```text
Real photograph of an ordinary Malaysian Chinese man in his early 30s, a cybersecurity researcher, in a dim security operations room, the monitors behind him softly out of focus. He wears a plain navy shirt with sleeves folded once and a lanyard with a blank ID card. He holds a tablet at chest height and studies it with quiet focus, mid-thought; the screen shows only abstract shapes and a small padlock symbol, no text. His face is lit softly by the screen from below-front, with the gentle warm edge light from behind-left. Waist-up, body turned 3/4 toward the right. 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```

### C2-F 🔴 Youth with phone ("don't overshare") · 2:3
```text
Real photograph of an ordinary Malaysian Indian young woman, about 20, a university student on a campus walkway at dusk, the background softly out of focus. She wears a cream top and a light denim jacket. She holds a smartphone toward the viewer at chest height; the screen shows one simple padlock icon on a dark-blue screen, no text. A natural, slightly shy smile, eyes to camera, caught mid-moment. Waist-up, body turned 3/4 toward the left. Blue-hour light per the chat rules. 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```
I can replace the phone screen afterwards if it comes out messy.

---

## Concept 1 — Alam Sekitar / Jerebu

### Primer (paste first in a new chat)
```text
I'm a designer compositing an A5 book cover for the Malaysian Government's security office. Theme: the haze (jerebu) clearing, protecting the environment as a national asset. Every image in this chat is a separate photographic asset I will cut out and combine in Photoshop.

REALISM RULES (most important):
1. Each image must be indistinguishable from a real photograph by a professional Malaysian press/commercial photographer. Shot on a Canon EOS R5. People: 85mm lens, f/2.8, ISO 200. Architecture, aircraft and landscapes: 24–200mm, f/8. Faint natural sensor grain.
2. Real, ordinary Malaysians, not models and not idealised. Natural skin with pores, fine lines, slight unevenness and natural asymmetry; real teeth; a few flyaway hairs; fabric with real creases, seams and wear. Candid, mid-moment expressions, not posed stock-photo smiles.
3. Neutral, unretouched processing like a straight RAW file: true-to-life colour, neutral white balance, normal contrast. No HDR, no glow or bloom, no teal-orange grade, no airbrushing, no over-sharpening, no "cinematic" look. I will grade everything together later.
4. Physically correct light with natural falloff and soft shadows. Lighting for this whole set: bright late-morning tropical sun from the UPPER RIGHT (about 2 o'clock, 45° high), soft natural fill from the left. No glowing outlines.
5. Correct anatomy: five fingers per hand, natural hand poses, both eyes looking at the same point, matching earrings, symmetrical uniform details.
6. No text, letters, numbers, logos or watermarks anywhere. Name tags and screens stay blank or abstract. If unsure about a badge or patch, keep it small and simple rather than inventing details.
7. Photograph people on location in a plausible real setting with the background softly out of focus. I will cut them out myself.

Don't generate anything yet. Reply "Ready".
```

### C1-A1 🔴 Clear sky plate · 2:3
```text
Real photograph of a clean tropical sky over Kuala Lumpur on a clear morning after rain: deep, even blue with a few natural white cumulus clouds lit from the upper right, the sun itself out of frame. Shot looking slightly upward with a 24mm lens at f/8, ISO 100. No land, no buildings, no aircraft, no birds. True-to-life colour, no polariser darkening, no HDR. Portrait 2:3, highest resolution.
```

### C1-A2 🔴 Haze sky plate · 2:3
```text
Real photograph of the same Kuala Lumpur sky on a heavy haze day: an even, smoky amber-grey veil of particulate haze, low contrast and low visibility, with the light diffused and slightly yellowish. It's a uniform smoky veil, not fog banks or storm clouds, and there's no visible sun disc. Shot looking slightly upward with a 24mm lens at f/8, ISO 100. No land, no buildings, no aircraft. True-to-life, slightly flat colour. Portrait 2:3, highest resolution.
```
I'll blend A1 and A2 diagonally in Photoshop with a soft gradient mask. That gives a real-looking "haze clearing" and gives us control over where the edge sits.

### C1-B 🔴📎 Istana Negara in clear morning light · 3:2
```text
[Attach the Istana Negara reference photo]
Using the attached photo as the exact architectural reference, produce a real architectural photograph of this same building, Istana Negara at Jalan Duta, Kuala Lumpur. Preserve the architecture exactly: the large central golden dome with its chevron pattern, the smaller golden domes, the cream façade, columns, arched windows, proportions and the number of domes. Do not add, remove or redesign anything. Change only the light: bright, clear late-morning sun from the upper right with crisp natural shadows, a clean simple blue sky behind, a well-kept green lawn. Shot straight-on with a 24mm tilt-shift lens at f/8, so the verticals stay straight; whole building in frame with space around it; empty flagpoles. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** same as C2-A. Use the real photo if anything is off.

### C1-C 🔴📎 Malaysian Army soldier · 2:3
```text
[Attach the Malaysian Army uniform reference]
Real photograph of an ordinary Malaysian Army soldier, a Malay man in his late 20s, standing on a green parade field in late-morning sun, the trees behind him softly out of focus. He wears the current Malaysian Army digital-camouflage uniform and beret exactly as in the reference, sleeves down, real fabric creases, name tag blank. He stands tall and calm, body turned 3/4 toward the right of frame, eyes lifted slightly toward the light, with a quiet, determined and warm expression. No weapon. Framed from head to mid-thigh from a slightly low camera position. Sun from the upper right per the chat rules. 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```

### C1-D 🔴 Environmental researcher · 2:3
```text
Real photograph of an ordinary Malaysian Malay woman in her early 30s, an environmental scientist, working at an outdoor air-quality monitoring station on a rooftop, with greenery and the station's equipment softly out of focus behind her. She wears a soft sage-green tudung and a white lab coat over modest clothing. She holds a handheld air-quality monitor and checks its screen with natural focus, caught mid-task; the screen shows only an abstract graph, no numbers or text. Waist-up, body turned 3/4 toward the right. Sun from the upper right per the chat rules. 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```

### C1-E 🔴 Youths planting a tree · 3:2
```text
Real documentary photograph of three ordinary Malaysian youths aged 18 to 24 at a community tree-planting site in a park: a Malay young woman in a tudung, a Chinese-Malaysian young man and an Indian-Malaysian young woman. They kneel together around a young rainforest sapling, pressing dark soil around it with bare hands, chatting and laughing naturally, caught mid-moment, with some soil on their fingers. Casual clothes in white, sage green and light denim, with real creases. Full figures, seen from a low 3/4 front angle, the group facing slightly toward the left of frame; the background of trees is softly out of focus. Sun from the upper right per the chat rules. 50mm, f/4. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** count fingers (30 in total); hands in the soil look natural; no one is staring at the camera.

### C1-F 🔴 Rainforest foliage border · 3:2
```text
Real photograph of lush Malaysian rainforest undergrowth at ground level, shot with a 50mm lens at f/8: layered ferns, wild ginger and broad tropical leaves, with natural variety in leaf age, a few small holes and imperfections, and scattered dewdrops. The leaves rise from the bottom of the frame with an irregular natural top edge against a deep, dark shaded forest background, so they can be masked. Sun from the upper right catches the top leaves. True-to-life greens, not oversaturated. Landscape 3:2, highest resolution.
```

### C1-G 🔴📎 C-130 Hercules (cloud seeding) · 3:2
```text
[Attach the RMAF C-130H reference]
Air-to-air photograph, taken from a chase plane with a 200mm lens at 1/60s, of a Royal Malaysian Air Force C-130H Hercules transport aircraft in flight, livery as in the reference, with real panel lines and slight weathering. Seen from a 3/4 low front angle, gently banking and flying from left to right. The four propellers show natural motion-blur discs and the fuselage is sharp. Small national roundels only, no readable serials or text. Plain clear blue sky behind. Sun from the upper right. Neutral processing. Landscape 3:2, highest resolution.
```
TUDM flies C-130s on cloud-seeding runs during haze, and the rationale will point that out.

---

## Concept 3 — Ekonomi / Penjimatan

### Primer (paste first in a new chat)
```text
I'm a designer compositing an A5 book cover for the Malaysian Government's security office. Theme: economic resilience, prudent energy-saving steps that keep the nation strong. Positive and hopeful; no conflict or war imagery. Every image in this chat is a separate photographic asset I will cut out and combine in Photoshop.

REALISM RULES (most important):
1. Each image must be indistinguishable from a real photograph by a professional Malaysian press/commercial photographer. Shot on a Canon EOS R5. People: 85mm lens, f/2.8, ISO 400. Architecture and landscapes: 24–70mm, f/8. Faint natural sensor grain.
2. Real, ordinary Malaysians, not models and not idealised. Natural skin with pores, fine lines, slight unevenness and natural asymmetry; real teeth; a few flyaway hairs; fabric with real creases, seams and wear. Candid, mid-moment expressions, not posed stock-photo smiles.
3. Neutral, unretouched processing like a straight RAW file: true-to-life colour, neutral white balance, normal contrast. No HDR, no glow or bloom, no teal-orange grade, no airbrushing, no over-sharpening, no "cinematic" look. I will grade everything together later.
4. Physically correct light with natural falloff and soft shadows. Lighting for this whole set: early sunrise. The low sun is BEHIND-RIGHT, giving a natural warm edge light on hair and shoulders, with soft cool skylight fill from the front-left. Faces are properly exposed, not silhouettes. No glowing outlines.
5. Correct anatomy: five fingers per hand, natural hand poses, both eyes looking at the same point, matching earrings, symmetrical uniform details.
6. No text, letters, numbers, logos or watermarks anywhere. Name tags and screens stay blank or abstract. If unsure about a badge or patch, keep it small and simple rather than inventing details.
7. Photograph people on location in a plausible real setting with the background softly out of focus. I will cut them out myself.

Don't generate anything yet. Reply "Ready".
```

### C3-A 🔴 Sunrise sky plate · 2:3
```text
Real photograph of a tropical sunrise sky over Kuala Lumpur, shot with a 24mm lens at f/8, ISO 100. The sun is just above the horizon at the right edge of the frame; the sky grades naturally from warm amber and soft gold near the horizon to deep blue at the top, with a few thin high clouds catching the light. Sky only: no land, buildings or birds. True-to-life colour with exposure for the sky, no HDR. Portrait 2:3, highest resolution.
```

### C3-A2 🔴📎 KL skyline at sunrise · 3:2
```text
[Attach the KL skyline reference photo]
Using the attached photo as the exact reference for the buildings, produce a real photograph of the Kuala Lumpur skyline at sunrise from a distance, shot with a 200mm lens at f/8, so the city reads as a soft, slightly hazy layer. It must include Merdeka 118 and the Petronas Twin Towers with their real shapes; don't invent or distort buildings. The low sun is behind-right, giving warm rim light on the right edges of the towers and soft blue atmospheric haze in front. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** compare the Merdeka 118 spire and the twin towers with the reference. If they're off, use a real skyline photo.

### C3-B 🔴📎 Istana Negara at sunrise · 3:2
```text
[Attach the Istana Negara reference photo]
Using the attached photo as the exact architectural reference, produce a real architectural photograph of this same building, Istana Negara at Jalan Duta, Kuala Lumpur. Preserve the architecture exactly: the large central golden dome with its chevron pattern, the smaller golden domes, the cream façade, columns, arched windows, proportions and the number of domes. Do not add, remove or redesign anything. Change only the light: early sunrise from behind-right, a natural warm edge of light along the right side of the domes and façade, the front of the building in soft cool shade with gentle warm bounce, a simple warm sky behind. Shot straight-on with a 24mm tilt-shift lens at f/8, so the verticals stay straight; whole building in frame with space around it; empty flagpoles. Neutral processing. Landscape 3:2, highest resolution.
```
**Check:** same as C2-A. Use the real photo if anything is off.

### C3-C 🔴 Solar farm base · 3:2
```text
Real photograph from a low angle across rows of photovoltaic solar panels at a Malaysian large-scale solar farm at sunrise, shot with a 35mm lens at f/11. The panels reflect the warm sky, with real dust and small imperfections on the glass; the low sun is at the right; the rows lead diagonally from the bottom-left into the distance toward green tropical hills. Foreground panels sharp. No people, no text. Neutral processing. Landscape 3:2, highest resolution.
```

### C3-D 🔴📎 Police officer on guard · 2:3
```text
[Attach the PDRM uniform reference]
Real photograph of an ordinary Royal Malaysia Police (PDRM) officer, a Malay man in his 30s, on duty at a container port at sunrise, the cranes behind him softly out of focus. He wears the dark-blue PDRM uniform and peaked cap exactly as in the reference, with real fabric creases; name tag blank. He stands alert in a calm, watchful stance, body turned 3/4 toward the left of frame, looking into the distance. No weapon drawn. Framed from head to mid-thigh from a slightly low camera position. Lighting per the chat rules. 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```

### C3-E 🔴 Renewable-energy researcher · 2:3
```text
Real photograph of an ordinary Malaysian Indian woman in her early 30s, a renewable-energy engineer in a solar research lab at sunrise, warm window light coming from behind-right and the lab equipment softly out of focus. She wears a white lab coat with safety glasses pushed up on her head. She holds up a single photovoltaic solar cell and inspects it closely, caught mid-task with a focused, quietly optimistic expression. Waist-up, body turned 3/4 toward the right. 85mm, f/2.8. Neutral processing. Portrait 2:3, highest resolution.
```

### C3-F 🔴 Young professionals · 3:2
```text
Real street photograph of three ordinary Malaysian young professionals in their mid-20s walking together across a city plaza at sunrise toward the camera, the office towers behind them softly out of focus: a Malay woman in a tudung and a smart blazer carrying a tablet, a Chinese-Malaysian man in an open-collar shirt and chinos, and an Indian-Malaysian man in a smart-casual polo. Mid-stride and mid-conversation, natural expressions, looking ahead and not at the camera. Full figures from a slightly low camera position. Lighting per the chat rules. 50mm, f/4. Neutral processing. Landscape 3:2, highest resolution.
```

### C3-H ⚪ Port at sunrise · 3:2
```text
Real photograph of a Malaysian container port at sunrise in the style of Port Klang: ship-to-shore gantry cranes and stacked containers against a warm sky, the low sun at the right, calm water reflecting the light, slight morning haze. Shot with a 70mm lens at f/8. No readable text or logos on the containers. Neutral processing. Landscape 3:2, highest resolution.
```

**Jets for C3:** reuse C2-D, flipped horizontally and regraded warm.

---

## Tally
| Set | Must 🔴 | Nice ⚪ |
|---|---|---|
| Shared | 1 | 0 |
| C2 | 6 | 0 |
| C1 | 8 | 0 |
| C3 | 7 | 1 |
| **Total** | **22** | **1** |
