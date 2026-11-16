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

**Next steps:**
- A drawn edge-on frame for the flip (a thin card edge).
- An uneven ground height function in the IK target.
- Gait from a speed slider (automatic walk → run transition at a Froude-number threshold).
- The hedgehog walking on its own with a 4-beat quadruped pattern.

## 6. Decisions so far

- **Two modes, one world:** an explore mode (painted sprite-stack diorama) plus a stage mode (gouache SVG paper puppets for dialogue, choices and turn-based moments). Tapping a character transitions between them.
- **Everything is `(generator, params, seed)` → a baked bitmap or atlas, cached.** Generate once, play many times.
- **Content as data, authored by Claude, with checkers:** the musikmodel pattern. Scene documents, character specs and prop lists. The game itself stays offline.
- **Story:** Ink (inkjs). Don't write a custom format.
- **Music:** musikmodel's `shared/` modules (no DOM, importable in Node) with adaptive sections per mood. Improve the oscillator trumpet and strings with physical modelling.
- **Sound effects:** an sfxr-style synth built from the same tricks (noise, sweeps, filters).
- **Puppets:** the rig model from `twilight-bugle` (pivot, attach, rest, z, mirror, string ties) maps onto SVG groups. Add blinks, eye direction toward the tap, mouth shapes, and a mouth flap driven by read-aloud word boundary events.
- **Kids:** read-aloud with word highlighting, big tap targets, autosave, no timers, no fail states (wrong choices get a funny reaction), no accounts, no analytics, no network during play.
- **The only asset that is not code-first:** voice acting.

## 7. Open questions

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
