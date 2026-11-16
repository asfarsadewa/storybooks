# Code-first techniques: findings

Research for a code-first narrative storybook game for children (up to about 10–11 years old). Touch or click. Turn-based when there is any confrontation. No image, model or sprite files. Everything is generated from code.

Each section names its prototype in `prototypes/`. Every prototype is one self-contained HTML file. Open it in a browser. There is no build step.

---

## 1. Sprite stacking

**Prototype:** `01-sprite-stack-flight.html` (a plane flies over a procedural island).

**Idea:** a 3D object is a pile of horizontal 2D slices (floor plans). Draw them bottom to top at the same x,y. Rotate every slice by the same angle. Offset each one a little up the screen. The result reads as 3D and rotates freely with no meshes.

**Core maths (canvas 2D):**

```js
// rot = camera yaw + object yaw; k = screen px per voxel; step = px between slices
const c = Math.cos(rot) * k, s = Math.sin(rot) * k;
for (let z = 0; z < layers.length; z++) {
  ctx.setTransform(c, s, -s, c, sx, sy - z * step);
  ctx.drawImage(layers[z], -w / 2, -d / 2);
}
```

**Findings:**
- **Gaps between slices.** When `step` is above about 1.4 px, the stack looks striped. Fix: draw each slice `rep = ceil(step / 1.4)` times at sub-steps. That multiplies the draw count, so cap it at 4–6.
- **Thin things don't need filling.** Grass blades, poles and reeds look fine with `rep = 1`.
- **Sorting.** Painter's order by screen y after rotation. Tall objects that overlap while rotating can still sort wrongly. That is acceptable for a diorama.
- **Pitch is fixed.** Stacking gives yaw rotation only. Changing the slice gap fakes a change of pitch. At steep angles the gaps show.
- **Where it fits:** a top-down or 3/4 world with a rotating camera. It is wrong for a low behind-the-character view. See §2.
- **Opinion:** if the camera never rotates, pre-render the voxel model at N angles into a sprite sheet instead.

## 2. Mode 7 + perspective stacking (chase camera)

**Prototypes:** `02-mode7-stack-racer.html` and `03-mode7-stack-racer-refined.html`.

**Ground:** classic per-scanline Mode 7. The track is a 1024² texture with mipmaps. For each screen row below the horizon, `z = camH * f / (y - horizon)`. March a texture coordinate across the row. Blend toward a haze colour by distance. Write into an `ImageData` at a low internal resolution and scale it up with `image-rendering: pixelated`.

**Stacks in perspective:** each object is projected with `scale = f / z`. Its floor plans are squashed vertically by `q = camH / z` (ground foreshortening). Heights are not squashed.

```js
// α = objectYaw - cameraYaw; model x = forward, model y = right
a = sinα * sc;  b = -cosα * sc * q;  c = cosα * sc;  d = sinα * sc * q;
ctx.setTransform(a, b, c, d, sx, sy - z * sc);
```

**Findings:**
- **LOD by slice stride.** When `step < 0.9 px`, draw every Nth slice. Far objects lose nothing visible, and the draw count drops a lot.
- **Camera presets** (high / mid / low) are worth exposing. The **mid** camera is the sweet spot. At the **low** (Road Rash) camera, boxy voxel cars hold up better than expected. Thin features and slice counts suffer.
- **Refined voxels:** use `R` voxels per model unit. Define shapes as continuous functions (superellipses, cylinders, tapered cabins) and sample them at `(i + .5) / R`. Then raise `R` per model: cars ×3, trees ×2. Draw with `scale / R`.
- **Baked per-voxel lighting:** lit tops, darker walls, height AO. This makes shapes readable even when tiny.
- **Cost:** about 2.6k slice draws per frame in portrait and about 6.5k in landscape at refined resolution.

## 3. Gouache illustration in SVG

**Prototype:** `04-gouache-svg-illustration.html` ("The Night Reader": an original character with a hedgehog, books and a mug).

Plain vector shapes. The painted look comes entirely from SVG filters:

| Filter | Recipe | Effect |
|---|---|---|
| `rough` | `feTurbulence` (0.035) → `feDisplacementMap` scale 4 | hand-cut wobbly edges |
| `paint` | wobble + stretched noise `baseFrequency="0.012 0.07"`, desaturated, remapped to 0.74–1.16, `multiply`, clipped to the shape (`feComposite in`) | pigment mottling with a brush direction |
| `dry` | wobble + high-frequency noise used as an alpha mask | speckled dry-brush edges |
| `fuzz` | `type="turbulence"` 0.2, displacement 14 | yarn / pom-pom |
| `blush` | Gaussian blur, then eaten by grain | powdery cheeks |
| `paper` | full-frame fractal noise at 0.85, `multiply` at about 0.22 | paper grain that ties it all together |

**Findings:**
- The palette does most of the work: cream paper, mustard `#e8b04a`, teal `#2b9a8c`, coral `#e5664a`, mint, lavender and peach.
- "Repaint" means re-rolling the turbulence `seed` attributes. You get a new brushing of the same drawing.
- **The gap to a real illustrator:** texture follows one global noise, not the form. The next step is per-shape brush direction (rotated or stretched noise per fill) and varied line weight.
- **Performance:** SVG filters are expensive to animate on tablets. **Bake static layers to bitmaps once**, and animate only the puppet parts.

## 4. Painted diorama (the game's world-map prototype)

**Prototype:** `05-painted-diorama.html`. This is the most complete prototype.

A pop-up-book diorama: a grass-and-soil slab, a cottage, trees, a pond, a meadow and a lantern. A walkable kid. Pip the hedgehog opens a gouache SVG puppet dialogue card with a branching chat.

### 4.1 Painted voxels (style unification)

One voxel grid is baked into two finishes (toggle "Painted / Crisp"):
- **Crisp:** flat colour, lit tops, darker walls.
- **Painted:** coherent 3D value noise as pigment mottling, a stretched second octave as brush streaks, warm light mixed into top faces, cool violet mixed into walls, pigment pooled at slice rims, dry-brush flecks, bilinear smoothing instead of nearest-neighbour, and a paper-grain overlay.

**Verdict:** painted voxels sit comfortably next to gouache SVG puppets. The shared palette and the paper grain are what unify them. The weak spots are texture that does not follow the form, and map characters that are small blobs. Expressive faces belong on the puppet stage.

### 4.2 Atlas packing (important for Safari)

The first version made 2 canvases per slice (about 900 in total) and rendered blank on a phone. **Pack all slices of a model into one atlas canvas** with a 1 px transparent gutter around each slice, and draw with a source rect:

```js
ctx.drawImage(atlas, 1, z * (Y + 2) + 1, X, Y, -X / 2, -Y / 2, X, Y);
```

Also: memoise identical models, defer the heavy build behind a "Painting…" message, re-check the canvas size every frame (an iframe can report 0 at load), and show an on-screen error banner.

### 4.3 Movement and environment interaction

- **Tap to walk:** inverse-project the screen point onto the slab plane (undo the y-squash `q`, then the rotation). Round obstacles slide the walker around. **TODO:** a walkable grid with A* pathfinding.
- **Wading:** sinking is almost free with stacking. Skip the bottom `minZ` slices and lower the stack by `minZ * step`, so the cut sits at the waterline. Add a foam collar ellipse.
- **Ripples:** world-space rings drawn as projected ellipses (`ry = r * q`). Each is a bright crest plus a darker trough 1 px below, with an ease-out radius, and clipped to the pond ellipse. One ring per step, a splash on entry and exit, and fidget rings while standing still.

### 4.4 Grass, wind and trample (ported from `ascii-hero`)

- `Trample` is ported as is. It is a grid of `(last push time, bend vector away from the mover)` that recovers over 3.5 s with **no per-frame decay pass**. The walker stamps where they stand and ahead of where they walk.
- `gust()` is ported as is: noise fronts rolling toward +x (world units converted to metres).
- **Bending a stack is a shear.** Slide each slice along a world-space bend vector by `(z / Z) ^ 1.7`, so blades curve rather than tilt. Trample also squashes height (step × `1 - 0.45 * m`). Trample overrides wind in proportion to its strength.
- **Gust sheen:** bake 6 atlases per grass model, brightening toward the tips. Each frame, pick the level from the gust (a per-tuft dither avoids banding). Trampled grass goes dull. It costs no extra draws.
- Reeds sway strongly. Trees sway only at the top.

### 4.5 Light and shadow

- **Time of day** from 0 to 1: the sun's azimuth and elevation, a scene tint (white by day, warm at golden hour, moonlit blue at night) and a night factor.
- **Sun shadows, slice by slice:** draw every slice again on the ground, offset by `height / tan(elevation)` away from the sun. They go into a **half-resolution** buffer with `rep` filling. Tint it once (`source-in` with a violet shadow colour), clip it to the slab with `destination-in`, then composite at about 0.4 alpha. That gives true shapes: gables, cones, canopies and bent blades.
- **Movers in shade:** a CPU test against cylinder casters (trees, cottage). Draw a darkened copy of the mover **into an offscreen layer first**, then composite once at alpha, so overlapping slices don't build up to solid black.
- **Point light (lantern):** a slice at height `h` lands on the ground scaled by `Hl / (Hl - h)` away from the light: `P' = L + (P - L) * s`. These shadows are drawn into the night layer, so they re-darken inside the light pool.
- **Night layer:** fill with the tint, cut light pools with `destination-out` radial gradients (ground pools squashed by `q`), add the lamp shadows, `multiply` over the scene, then add glows with `lighter` (lamp, windows, fireflies). Stars appear in the background.
- **Gaps:** lamp shadows read weakly at phone size. Object lighting is still baked top-lit; directional sun warmth on the sunward sides would need about 4 baked side-lit atlases per model, picked by sun azimuth relative to the object's yaw.

### 4.6 Costs (headless Chromium, no GPU, 390×760 @2×)

| State | fps |
|---|---|
| Diorama, before grass | ~10 |
| + about 120 grass tufts | ~7.5 |
| + sun / lamp shadows | ~6.5–7.5 |

Real devices with GPU canvas should be much faster. These numbers are only for comparing versions. If needed: cache shadows of static objects (they only change with rotation or time), and only re-shadow movers and swaying grass.

### 4.7 Flight mode (chase camera over the diorama)

The **Fly** button turns the player into a small voxel bird. The chase camera from prototype 01 follows it. The button changes to **Land**.

- **Camera:** the heading points up the screen (`rot = −π/2 − heading`). The camera follows with a lag (gain 3.5 per second), so a hard turn shows about 20° of trail.
- **Pan:** `proj()` subtracts a camera point `(camX, camY)`. Every use of the slab centre now goes through `proj(0, 0)`. The cache keys of the static layer, the night layer and the lamp layer include the pan.
- **Zoom ×1.8 in flight:** `S = S0 · zoom`. Impostors are cached at zoom 1 only. So any zoom other than 1 counts as interacting, and stacks draw live at the current scale. The zoom costs no extra draws.
- **Camera aim:** the altitude lifts the bird up the screen. The camera aims ahead of the bird's ground point by `4 + 0.8 · alt · 0.92 / q` units. That keeps the bird near the middle of the screen. The first version aimed at the ground point, and the bird sat at the top edge.
- **Landing:** the pan and zoom ease back. They snap to exactly 0 and 1, so the caches hit again. Headless, this takes 2.0 s, and then the draws return to the idle count.
- **Drawing:** the bird flies above every prop (26 units, the trees reach 22). So it draws after all stacks, and it needs no sorting. Its shadow is a soft blob on the slab that shrinks with altitude.
- **Model:** 3 baked wing frames (up, spread, down). It flaps for 1.4 s, then glides for 1 s. It is built ×1.6 with chunkier voxels (R = 2), because at R = 3 and real size it was too small on a phone.
- **Steering:** the left or right half of the screen turns the bird. With no input, the bird glides in a slow circle. Within 10 units of the rim, the steering blends into a turn back toward the middle.
- **Edge cases:** sun shadows and lamp shadows switch off while flying, as during a drag. Taps steer, so they cannot walk the kid or start hotspots. Autosave should restore the kid on foot.

**Measured** (iPhone 14 Pro, Safari, pixel ratio 1.5, `?bench`):

| Scenario | fps | Frame p95 | Slow frames | JS CPU | Draws |
|---|---|---|---|---|---|
| Day flying | 60 | 17 ms | 0% | 4.1 ms | 1,461 |
| Night flying | 60 | 17 ms | 0% | 3.8 ms | 1,477 |
| Day dragging (for comparison) | 60 | 17 ms | 0% | 3.7 ms | 1,385 |

Flight costs the same as dragging. A low-cost tablet is not measured yet.

---

## 5. Baked SVG puppet rig (animating the gouache drawing)

**Prototype:** `06-baked-svg-puppet.html` ("The Night Reader" from §3, animated).

**Why bake:** moving the live SVG would re-run every filter (displacement, turbulence, blur) on every frame, and phones can't keep up. Instead, each part goes through its filters **once**, and the animation moves the resulting bitmaps on a canvas rig. Measured: **43 parts baked in about 0.3 s, then 60 fps** (headless Chromium, no GPU).

**Baking one part:**
1. In the source SVG, every part is a top-level `<g data-part="name">`. The source SVG stays in the DOM, hidden with `visibility: hidden` (not `display: none`, because `getBBox()` needs layout).
2. `getBBox()` the part and add a margin for filter overspill (14 units; 30 for the fuzz and blur filters).
3. Clone the whole SVG. Remove every other `[data-part]`. Set `viewBox` to the part's box and `width`/`height` to box × bake scale. Defs, patterns, clip paths and filters come along, and filter noise stays identical because it lives in user space.
4. Serialise it to a `data:image/svg+xml` URL, call `Image.decode()`, then draw it into a canvas sized to the box. Store `{ canvas, x, y, w, h }` in drawing units.
5. Bake 6 parts at a time.

The bake scale is about the display scale (`min(2.4, fit.k × 1.05)`), so bitmaps match screen pixels.

**Authoring rules the drawing must follow:**
- **Split by motion, not by look.** Anything that moves on its own is its own part: earrings, pom-pom, each steam wisp, each motif, the hedgehog's body, and the hedgehog's eye in each state.
- **States are sibling parts.** `eyesClosed` / `eyesOpen`, `mouth` / `mouthOpen`, `hhEyeClosed` / `hhEyeOpen`. Draw the extra states up front, even though the still image never shows them.
- **Draw order ≠ hierarchy.** The hair sits behind the torso but moves with the head. Draw it first, inside the head transform, then draw the torso, then the rest of the head.
- **Pivots in drawing units:** body (400, 1000) at the bottom edge; head (400, 505) at the neck; pom-pom at its base; earrings at the lobe; hedgehog at its feet.

**Motion:**
- **Breathing:** scale the body about its bottom edge, `1 + b` vertically and `1 − 0.35 b` horizontally, so volume is roughly kept.
- **Head:** slow sway plus a tap wobble spring.
- **Secondary motion:** damped springs (`a = −k·x − c·v + drive`) for the pom-pom, earrings and hair, driven by the head's angular acceleration. They lag and overshoot like real hanging things.
- **Expression state machine:** eyes are content (closed) by default. Every 4–8 s she opens them, glances toward the hedgehog and blinks, and the hedgehog wakes and peeks back about 0.35 s later. A tap gives surprise (0.35 s) → giggle (open mouth with jaw flutter, blush boost, head wobble, hearts).
- **Steam:** each wisp rises, sways and fades along a loop. Two copies half a cycle apart keep it continuous.
- **Hit testing:** invert the page fit into drawing units, then use circles and rectangles per hotspot.

**Pitfalls:**
- Put `addEventListener('error')` in its own `<script>` before the main one. A syntax error in the main script stops that same script from registering its own error handler, and the page just sits on "loading".
- Not yet tested on Safari. Rendering an SVG data URL with filters into `Image` should work there, but confirm it.

**Opinion:** this is the stage-mode puppet technique. It's the `twilight-bugle` rig (pivots, attach points, hierarchy) with parts generated from code instead of painted by an image model.

### 5.1 Procedural gaits (side-view walker)

**Prototype:** `07-gait-walker.html`. The same character redrawn in profile with full body (striped tights, boots, a backpack with the hedgehog peeking out), split into jointed parts and baked the same way. Walk, run, skip and sneak, with stop, card-flip turns, footprints, a parallax painted landscape and a live footfall chart.

**A gait is data:** stance windows per foot in cycle phase, plus body parameters.

| Gait | Stance windows (near / far) | Duty | Flight | Notes |
|---|---|---|---|---|
| walk | `[0, .62)` / `[.5, 1.12)` | 62% | none | pendulum hip rise mid-stance, heel strike then toe-off |
| run | `[0, .36)` / `[.5, .86)` | 36% | 2 per cycle | hip dips under load, flight arc, forefoot strike, lean 0.2, elbows bent |
| skip | `[0, .17)`, `[.25, .40)` / `[.5, .67)`, `[.75, .90)` | 32% | 4 per cycle | step-hop: two contacts per foot, big arm swing |
| sneak | `[0, .74)` / `[.5, 1.24)` | 74% | none | crouched hip (0.86), tiptoe stance, high steps, hands up |

Airborne windows are computed from the pattern (sampled at 400 steps), not written by hand.

**Feet never slide.** Measured: **0.000 units** of planted-foot drift across all four gaits.
- A foot lifts on the stance → swing **edge** of its pattern. At lift-off it aims for where the hip will be at the middle of its next stance: `hipX + dir · v · (tToMidStance) + 4`.
- A swing is a **timer** (duration = phase to next stance ÷ cadence). The timer decides landing, not the pattern, so a gait change mid-swing never pops a foot into the ground.
- Short swings (skip hops) lift less: × 0.45 when less than 0.12 of the cycle away.
- Gait windows switch only at the cycle boundary, while numeric parameters blend continuously (about 0.2 s).

**Body:**
- **Hip height** = standing height × gait crouch, − a pendulum rise over each stance, + a dip under load, − a flight arc. It is then clamped so no planted leg is asked to reach beyond `L1 + L2`.
- **Legs:** two-bone IK in local space (facing +x), knee forward: `thigh = −(base + A)`, `shin = π − B`, with `base = atan2(tx, ty)`. The boot's world pitch ψ follows a heel-strike → flat → toe-roll curve in stance and toe-off → strike in swing, and the ankle rises with ψ.
- **Arms copy the opposite thigh's swing** (× gain + bias), so they work for any pattern, skip included. Elbow bend grows on the forward swing.
- **Follow-through springs** driven by the hip's vertical acceleration and the horizontal speed change: pom-pom, earring, scarf tail (also streams back with speed), backpack, hedgehog, skirt and a head nod.
- **Expressions per gait:** eyes open while moving, a grin for run and skip, an "o" for sneak, contented closed eyes when standing.

**Stopping and turning:**
- **Stop:** the hip coasts (`v *= e^(−7 dt)`), then each foot steps to a neutral spot under the hip, one at a time, before going idle.
- **Turn:** settle, then a card flip where `scaleX = |cos(π t)|` over 0.4 s. Facing switches while edge-on, and the feet are re-placed at their mirrored neutral spots.
- **Camera:** it leads in the facing direction, plus a `v / rate` term that cancels the lerp lag, so the run stays on screen.

**Footfall chart:** the last 3 s of stance per foot plus an airborne row (a Hildebrand-style gait diagram), recorded every frame from the real foot state, not from the pattern. So it shows transitions honestly.

**Speed slider → automatic gait (Froude number):**
- `Fr = v² / (g · legLength)`. With a child's 164-unit leg ≈ 0.6 m, `g ≈ 2680 units/s²`.
- **Hysteresis:** run above Fr 0.42, back to walk below 0.32, so the gait never flickers at the boundary.
- In auto mode, cadence scales with `√(v / v₀)` and stride = `v / cadence`.
- Measured: walk at 120, 200 and 300 u/s (Fr 0.03–0.20), run at 520 u/s (Fr 0.62). **0.000** planted-foot drift at every speed.
- Speed below 12 stops her (settle → idle). A tap restarts at 160 u/s.

**Card edge on turning:** while `|scaleX| < 0.35`, draw a paper strip (corrugated edge) the height of the puppet at the hip, fading in as she goes edge-on.

**Pip, the quadruped:** it hops out of the backpack (parabola with a spin), follows 95 units behind her, and hops back in on request. Same machinery as hers (stance windows, edge-triggered timed swings, plants aimed at mid-stance), with four legs:

| Gait | Footfall offsets (nh, nf, fh, ff) | Duty | Used when |
|---|---|---|---|
| walk (lateral sequence) | 0, .25, .5, .75 | 72% | speed < 90 |
| trot (diagonal pairs) | nf + fh at 0, ff + nh at .5 | 42% | < 240 |
| gallop | fronts 0 / .08, hinds .48 / .56 | 26% | above |

- Legs are drawn as short curved strokes from the shoulder or hip attachment to the planted paw. At this size they need no IK.
- Standing still: any paw more than 6 units from home shuffles back.
- Measured: **0.000** paw drift in trot and gallop.
- Pip's four feet join the footfall chart, so you can see the diagonal pairing of the trot directly.

**Next steps:** an uneven ground height in both IK targets; Pip walking (not trotting) at slow speeds (raise its thresholds or shorten its stride); sounds per footfall from the musikmodel synth (the chart already knows every contact).

## 6. Synthesized dialogue voices ("babble")

**Prototype:** `08-babble-voices.html`. Pip, Mira and Hoot the owl have a short conversation. Every sound is synthesized live in Web Audio, with no recordings. The text types out in time with the voice, and the mouths move with the actual loudness.

**Three styles** (switchable live):

| Style | How | Feels like |
|---|---|---|
| Blip | one oscillator tone per letter (square, triangle or sawtooth by speaker), 45 ms, low-passed | Undertale |
| Chatter | square-wave ticks on every other letter, each falling slightly in pitch, band-passed, plus a 12 ms high-passed noise click | Golden Sun |
| Babble | a "glottal" buzz (all harmonics at `1/n^1.5`) through 3 parallel band-pass formants (F1/F2/F3) per vowel, with noise-burst consonant onsets | Animal Crossing |

**Babble details:**
- **Vowel formants:** adult values (e.g. `a` 800/1250/2600 Hz, `i` 320/2300/3000), scaled per speaker by `fs` (Pip 1.55, Mira 1.18, Hoot 0.84). A smaller creature means higher formants, independent of pitch.
- **Every letter is a syllable.** A vowel letter sounds itself. A consonant gets an onset (plosive: a 14 ms band-passed burst; `s`/`z`: 45 ms high-passed hiss; `f`/`v`/`h`: 35 ms band-passed noise; `m`/`n`/`l`/`r`/`w`: no burst, a softer vowel), then borrows the next vowel in its word.
- Breath noise through F2 per speaker (Hoot is breathiest) and vibrato through an LFO on the source frequency.

**Voices** (`f0`, `fs`, seconds per letter): Mira 290 Hz / 1.18 / 0.058; Pip 520 Hz / 1.55 / 0.042; Hoot 125 Hz / 0.84 / 0.082 (+35% gain).

**Prosody:**
- **Declination:** pitch × `1.08 − 0.16 · p` across the sentence.
- **Questions:** rise over the last 30%.
- **Exclamations:** ×1.12 pitch, ×0.88 letter time, ×1.15 loudness.
- **Word stress:** the first syllable of each word gets ×1.07 pitch and ×1.2 loudness.
- **Rests:** space = 0.55 letters; comma = 4; `. ! ?` = 7; `…` = 10.

**Determinism:** per-letter jitter is `hash(strHash(line), index)`, so the same line always sounds identical, the same `(generator, params, seed)` rule as the visuals.

**Engineering:**
- The text reveal reads `AudioContext.currentTime` against the planned event times, so text and sound can't drift apart.
- Each line plays on its own gain bus. Skipping ramps that bus to 0 over 40 ms and disconnects it, so there are no clicks and no orphaned nodes.
- Every node uses an exponential attack and release envelope, which avoids clicks.
- **Mouth flap** comes from an `AnalyserNode` RMS on the output (`× 9`, clamped), smoothed by half each frame.
- A `DynamicsCompressor` (−18 dB, 4:1) sits on the master.
- The audio context is created on the first tap (browser autoplay rules). On iPhone, Web Audio is silent when the ringer switch is on silent, so tell players.

**Verification without ears:** render each style × voice through `OfflineAudioContext` and check peak, RMS and NaNs. Measured on the line "Hi Pip! Why do you look so worried?": peaks 0.22–0.47, RMS 0.03–0.07, no NaNs, no clipping. This makes a good automated test for audio generators, alongside the visual regression idea.

**Fits with:** tiny-voca (an Apache-2.0, about 18 MB English TTS model that runs in the browser) for real read-aloud narration, with babble for character chatter. Pitch and formant shifting on its two voices could give a whole cast.

## 7. Performance: the code-first "asset pipeline"

**Context (from the design conversation):** the painted diorama (§4) felt laggy on a real phone. That is the core trade of code-first art: assets are expensive to ship and cheap to draw, while generated art is free to ship and costs CPU and GPU every frame you redraw it. So the habits change from "make files smaller" to **"redraw less, at fewer pixels"**. Treat the rules below as the default for every renderer in this project, the way asset compression is the default elsewhere.

**Why the diorama lagged:**
- 3,000–5,900 `drawImage` calls per frame: every slice of every stack, often 2–4 times to fill gaps.
- Every slice drawn again for sun shadows, every frame.
- A full-resolution canvas at 2× pixel ratio, plus a full-screen paper-grain blend and night-tint blend every frame.
- Idle auto-rotation, so nothing was ever still long enough to cache.
- New gradients, `vis` arrays and `filter()` results every frame, which means garbage-collection stutter on phones.

**The rules (all implemented in `05-painted-diorama.html`; the ⚡ button switches to the original renderer for A/B):**
1. **Cache layers, not just parts.** Everything on the ground that doesn't move (table shadow, slab, contact blobs, sun shadows of static things including grass) lives in one screen-sized layer. It is rebuilt only when its key changes: snapped rotation, time of day (1/200 steps), size, painted mode, interacting yes/no.
2. **Impostors for stacks.** A whole stack at a snapped angle (256 steps = 1.4°), quantised screen-space bend (0.5 S; 0.65 S for grass), squash (1/20) and sheen (3 levels) is rendered once into a shared **1024² atlas page** (shelf packer, 8 pages, the oldest page recycled). Then it costs **one draw per object**. Grass yaw is snapped to 16 directions so tufts share impostors. Few large canvases instead of thousands of small ones also keeps iOS memory safe (§4.2).
3. **A build budget.** At most 24 new impostors per frame. Misses beyond the budget draw live at reduced quality (one draw per slice, no gap filling) until they're cached.
4. **Interaction quality.** While dragging, during a fling, while scrubbing the time of day, or while cycling the day, every cache key would miss anyway. So draw stacks live, one draw per slice, grass at every other slice, and skip sun shadows. Full quality returns about 1.5 s after release, as the caches refill under the budget.
5. **A pixel budget.** Pixel ratio capped at 1.5 (painterly art hides it), plus **dynamic resolution**: every 2.5 s, drop the render scale by 0.125 (down to 0.75) if below 45 fps, and raise it again if above 57 fps with under 8 ms of CPU per frame. Any resize clears the caches.
6. **No full-screen effects per frame.** Paper grain is a static CSS layer (`mix-blend-mode: multiply`) that the browser composites for free. The night or golden tint layer is rebuilt at most 15×/s. Glows are cached radial-gradient sprites drawn with `drawImage`, not new gradients per frame.
7. **Shadows of movers only, only in their box.** In optimised mode, only the kid and Pip get per-frame sun shadows. Clear, tint and composite only the half-resolution rectangle their shadows can reach. (Note: `source-in` / `destination-in` clear the whole canvas outside the source, so clip to the rectangle first.)
8. **No allocation in the hot loop.** Reuse the `vis` objects and sort in place, compact arrays in place instead of `filter()`, and cache gradients by key.
9. **No idle auto-rotation.** A camera that never stops means nothing can be cached. Rotate on input only.
10. **Measure.** Every prototype shows a frame-time HUD: fps, CPU ms (average and p95), draws per frame, pixel ratio, impostor count, layer rebuilds per second. Test on the cheapest real phone or tablet available.

**Measured** (headless Chromium, **no GPU**, 390×760 at 3× device scale; CPU = JS time per frame; fps capped at 60):

| Scenario | Original: fps / CPU / draws | Optimised: fps / CPU / draws |
|---|---|---|
| Day, idle | 6.7 / 18.8 ms / 4,029 | **60 / 3.0 ms / 198** |
| Golden hour, idle | 5.5 / 42.4 ms / 5,895 | **60 / 6.8 ms / 266** |
| Night, idle | 6.7 / 13.3 ms / 3,145 | **60 / 3.2 ms / 205** |
| Walking through the meadow | 6.0 / 32.0 ms / 5,427 | **60 / 3.8 ms / 239** |
| Windy | 6.7 / 19.0 ms / 4,029 | **60 / 3.1 ms / 176** |
| Dragging the view | 5.5 / 34.8 ms / 5,493 | **22.5 / 9.1 ms / 1,417** |

After a drag, caches refill in about 1.5 s, with one 0.5 s window averaging 65 ms per frame. The original also renders at pixel ratio 2.0 against 1.5, which accounts for part of the difference.

**Pitfalls found on the way:**
- Fling decay must be **time-based** (`rotV *= 0.92^(60·dt)`). Per-frame decay at low fps kept the scene in "interacting" mode for seconds.
- Shared impostor keys only work if the inputs are snapped: rotation, grass yaw, bend and sheen. Continuous values give a cache miss on every frame.
- With many cache keys (6 sheen levels × fine bend bins), windy weather caused about 180 impostor builds per 0.5 s and 40 ms frames. Coarser bins and 3 sheen levels brought that down to about 18 builds.

**Measured on a real phone** (iPhone 14 Pro, iOS 18.7, Safari, 393×695 CSS px, `?bench` mode, pixel ratio fixed at 1.5):

| Scenario | fps | Frame p95 | Frames over 20 ms | JS CPU | Draws |
|---|---|---|---|---|---|
| Optimised, day idle | 60 | 17 ms | 0% | 1.6 ms | 192 |
| Optimised, golden hour idle | 60 | 17 ms | 0% | 2.4 ms | 228 |
| Optimised, night idle | **46** | **45 ms** | **29%** | 2.1 ms | 280 |
| Optimised, night, no lamp shadows | 59 | 17 ms | 0% | 2.9 ms | 198 |
| Optimised, night idle, pixel ratio 1.0 | **46** | **45 ms** | **29%** | 2.1 ms | 283 |
| Optimised, walking through the meadow | 60 | 18 ms | 3% | 1.1 ms | 211 |
| Optimised, windy | 60 | 17 ms | 1% | 1.6 ms | 196 |
| Optimised, day dragging | 60 | 17 ms | 0% | 3.7 ms | 1,385 |
| Optimised, night dragging | **26** | **47 ms** | **82%** | 4.7 ms | 1,624 |
| Original, day idle (pixel ratio 2) | 5 | 203 ms | 100% | 9.3 ms | 4,029 |
| Original, night idle (pixel ratio 2) | 13 | 81 ms | 100% | 8.1 ms | 3,145 |

**Findings:**
- **Lamp shadows cause the night slowdown.** The night layer rebuilds 15 times per second. Each rebuild with lamp shadows takes about 45 ms. That gives 29% slow frames, which is about 15 of every 60. If you switch off lamp shadows, the scene runs at 60 fps.
- **While dragging at night, the rotation changes on every frame.** So the night layer rebuilds on every frame, and the scene drops to 26 fps.
- **The cost is not fill rate.** At pixel ratio 1.0 the numbers do not change.
- **The cost is not draw count.** Day dragging draws 1,385 images per frame at 60 fps.
- **JavaScript does not see the cost.** The lamp-shadow phase uses 0.2 ms of JS time. The 45 ms is inside Safari's canvas pipeline. On Safari, only ablation runs (one feature off at a time) show where the time goes. JS phase timers do not.
- The original renderer is much slower on Safari than headless Chromium suggested: 5 fps against 152 fps. Its per-frame sun shadows use the same offscreen-canvas chain as the lamp shadows.
- **Suspect:** many scaled `drawImage` calls into an offscreen canvas, then `destination-in` and `source-in` passes on it, then that canvas drawn into another canvas in the same frame. We did not isolate the exact step. Caching made the question less urgent.

**The fix: cache lamp shadows like sun shadows** (rules 1 and 4):
- The static objects' lamp shadows (rest pose, grass included) are drawn once into one half-resolution layer. The layer is already tinted and clipped to the lamp pool. Its key is the snapped rotation, the size and the tint.
- Each night rebuild draws that layer once. Then it redraws the kid's and Pip's lamp shadows. It does this only inside the lamp pool's box, and only if one of them stands in the pool.
- The tint (`source-in`) and the clip (`destination-in`) touch only that box.
- Lamp shadows are skipped while the player interacts (drag, fling, time scrubbing).
- Trade-off: grass sway no longer moves the lamp shadows of grass. At phone size nobody sees this.

**Before → after** (same iPhone 14 Pro, Safari, pixel ratio 1.5):

| Scenario | Before: fps / p95 / slow frames | After: fps / p95 / slow frames |
|---|---|---|
| Night idle | 46 / 45 ms / 29% | **60 / 17 ms / 0%** |
| Night, the kid in the lamp pool | not measured | 59 / 22 ms / 7% |
| Night dragging | 26 / 47 ms / 82% | **60 / 17 ms / 0%** |
| Day dragging | 60 / 17 ms / 0% | 60 / 17 ms / 0% |

- With a mover in the pool, the box chain still costs a few slow frames (7%). If this shows in play, the next lever is to lower the mover rebuild rate. Another lever is to draw movers without the offscreen chain.
- **Rule for Safari:** keep offscreen-canvas chains (draw, `source-in`, `destination-in`, then draw that canvas into another) out of the per-frame path. Cache their results, or limit them to a small box.
- **Effect on the WebGL plan:** on this phone, optimised Canvas 2D now holds 60 fps in every scenario, dragging included. So WebGL is not needed for speed on a high-end phone. Test a cheap tablet before you decide.

**Bench mode:** open `05-painted-diorama.html?bench` from `tools/bench-server.py`. The page runs every scenario by itself (1.5 s warm-up and 4 s of measurement each). Then it POSTs the results to the PC. The server saves them in `bench-results/` (git ignores this folder). Turn off Low Power Mode on iPhones first, because it caps Safari at 30 fps.

**Still slow, and the next lever: WebGL for explore mode.** Dragging is the one case caching can't fix in Canvas 2D: every stack must be redrawn at a new angle. Sprite stacking is the ideal GPU workload: all slices of all models in one texture atlas, every slice an **instanced quad in a single draw call**, the bend and squash in the vertex shader, and shadows as a second instanced pass with a projection matrix. That should make dragging as cheap as idle. Keep Canvas 2D or SVG for the puppet stage and UI.

## 8. Decisions so far

- **Two modes, one world:** an explore mode (painted sprite-stack diorama) plus a stage mode (gouache SVG paper puppets for dialogue, choices and turn-based moments). Tapping a character transitions between them.
- **Everything is `(generator, params, seed)` → a baked bitmap or atlas, cached.** Generate once, play many times.
- **Performance rules (§7) are the default for every renderer:** cache layers and impostors, snap continuous inputs so caches hit, a draw budget, a pixel budget with dynamic resolution, an interaction-quality mode, no full-screen effects or allocation per frame, and a frame-time HUD. **Plan WebGL instanced stacking for explore mode** in the game.
- **Content as data, authored by Claude, with checkers:** the musikmodel pattern. Scene documents, character specs and prop lists. The game itself stays offline.
- **Story:** Ink (inkjs). Don't write a custom format.
- **Music:** musikmodel's `shared/` modules (no DOM, importable in Node) with adaptive sections per mood. Improve the oscillator trumpet and strings with physical modelling.
- **Sound effects:** an sfxr-style synth built from the same tricks (noise, sweeps, filters).
- **Dialogue voices:** babble (§6) for character chatter, and a small TTS model (tiny-voca) for read-aloud narration. Voice acting stays optional.
- **Puppets:** the rig model from `twilight-bugle` (pivot, attach, rest, z, mirror, string ties) maps onto SVG groups. Add blinks, eye direction toward the tap, mouth shapes, and a mouth flap driven by read-aloud word boundary events.
- **Kids:** read-aloud with word highlighting, big tap targets, autosave, no timers, no fail states (wrong choices get a funny reaction), no accounts, no analytics, no network during play.
- **The only asset that is not code-first:** voice acting.

## 9. Open questions

1. Should the dialogue card stay a 2D overlay, or should puppets pop out of the diorama as Twilight Bugle-style cardboard (Three.js `ExtrudeGeometry` from the SVG paths, with SVG rendered to a texture)?
2. Should map characters get a thin ink outline for readability?
3. Should painted texture follow the form (per-object brush direction)?
4. Pathfinding: a walkable grid with A*.
5. Pond reflections: redraw nearby stacks inverted and tinted inside the pond clip.
6. Directional object lighting: 4 side-lit atlases.

## Related repos

- `asfarsadewa/musikmodel`: code-first music (brief → score JSON → synthesised instruments, deterministic humanised takes).
- `asfarsadewa/twilight-bugle`: cardboard puppet theatre in Three.js (puppet rig, deterministic cue timeline, changeover planner).
- `asfarsadewa/ascii-hero`: source of `Trample` and `gust()`.
