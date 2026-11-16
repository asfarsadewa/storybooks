# Production pipeline: book one

This spec describes how we make the first interactive storybook. It uses the techniques in `code-first-techniques.md`. It adds only the pieces that turn those techniques into a repeatable process.

**Principle:** a book is data. The engine is code. People and Claude write documents. Fixed generators turn the documents into pictures and sound. The second book needs new documents. It does not need new engine code, except for new props.

This is the musikmodel pattern: brief → document → checker → renderer. Every checker error names its place in the document.

---

## 1. Decisions

| Topic | Decision |
|---|---|
| Repository | A new repo for the game. This repo stays research. |
| Build | Vite with ES modules. The static build is an offline PWA. |
| Puppets | Each character is one SVG file written to the puppet contract (§5.4). A checker validates it. A parametric character generator waits until after book one. |
| Narration | Babble voices (§6 of the findings) and text with word highlighting. Read-aloud TTS waits until after book one. |
| Profile walker | Not in book one. It needs a third drawing for each character. |
| Story | Ink, run by inkjs. The Node checker compiles Ink with the inkjs compiler. |
| Music | musikmodel score documents. The `shared/` modules are vendored with their source commit noted. |
| Editor | Claude Code edits the documents. The person reviews in the previewer. There is no authoring app for book one. |
| Target devices | iPhone 14 Pro (measured). One low-cost tablet (not chosen yet). |
| Kids | No accounts, no analytics, no network during play, no timers, no fail states, autosave. |

## 2. Scope of book one

Book one is *The Adventure of Kai the Brave*. Its design is in `book-one-kai.md`.

- 3 scenes: the meadow, the crash site and Valda.
- 3 characters. Kai is the player character. The Skylark is a fourth figure for flight.
- 7 puzzles on 4 puzzle engines (§5.7).
- About 20 minutes of play. Reading age 10 to 12.
- Explore mode (the diorama), stage mode (the puppet card), puzzle mode and flight mode (the meadow only). Tapping a character or a hotspot changes the mode.

## 3. Stages

1. **Brief.** The person writes one page: the story, the characters, the places, the length and the reading age.
2. **Documents.** Claude writes the book documents (§5). The person reviews them in the previewer.
3. **Check.** `npm run check` runs every checker (§7). A document that fails does not reach the build.
4. **Preview.** The previewer loads any scene or Ink knot directly (§9).
5. **Device gate.** Each scene passes the bench on every target device (§10).
6. **Ship.** `npm run build` makes the offline PWA.

## 4. Game repo layout

```
book/                     one folder per book
  book.json               manifest
  story.ink               all text and choices
  cast/<id>.json          character spec
  cast/<id>.svg           stage puppet
  scenes/<id>.json        diorama layout
  puzzles/<id>.json       puzzle (generator, params, seed)
  music/<mood>.json       musikmodel score
  ui.json                 interface strings (ASD-STE100)
engine/                   runtime modules (§6)
tools/
  check.js                all checkers
  bench-server.py         device bench results
preview/                  previewer page
test/                     checker tests and headless screenshot tests
```

## 5. Documents

### 5.1 `book.json`

```json
{
  "id": "kai",
  "title": "The Adventure of Kai the Brave",
  "readingAge": [10, 12],
  "start": "start",
  "player": "kai",
  "cast": ["kai", "tako", "zarbor", "skylark"],
  "scenes": ["meadow", "crash", "valda"],
  "music": { "meadow": "music/meadow.json", "ship": "music/ship.json", "valda": "music/valda.json", "heartsong": "music/heartsong.json" },
  "seed": 1
}
```

`start` is the first Ink knot. `player` is the cast member that the child walks with.

### 5.2 `story.ink` and the tag vocabulary

All words in the book live in Ink. A line with no `by` tag is narration. Tags cue the staging. The vocabulary is fixed. The checker rejects any other tag. To add a tag, change the engine and this spec in the same change.

| Tag | Arguments | What it does |
|---|---|---|
| `scene` | scene id | Loads the scene in explore mode. |
| `stage` | 1 or 2 cast ids | Opens the stage card with these puppets. The first one stands on the left. |
| `by` | cast id | The line is spoken by this character, in its voice. |
| `mood` | cast id, expression | Sets the expression of a puppet (§5.4). |
| `walk` | cast id, marker id | The character walks to a marker in the current scene. |
| `time` | `morning`, `midday`, `golden`, `night` | Sets the time of day. |
| `music` | mood id | Changes the music to this mood. |
| `sfx` | sound id | Plays a sound from the engine's sound list. |
| `puzzle` | puzzle id | Opens the puzzle. The story continues when the child solves it. |

A knot that ends with `-> DONE` closes the stage card. The child is then back in explore mode. Hotspots (§5.5) start knots.

```ink
=== meet_pip ===
# stage: mira pip
# mood: pip worried
Oh! Hello there. #by: pip
The lantern by the bridge went out last night. #by: pip
* [Of course I will help!] -> yes
* [Why can you not do it, Pip?] -> why
```

Story text is the voice of the fiction. ASD-STE100 does not apply to it. The kid rules in §7 do apply.

### 5.3 `cast/<id>.json`

```json
{
  "id": "pip",
  "name": "Pip",
  "voice": { "style": "babble", "f0": 520, "fs": 1.55, "rate": 0.042, "vib": [0.4, 7], "breath": 0.08 },
  "map": { "figure": "quadruped-small", "height": 5, "colors": { "body": "#7a5236", "belly": "#e9cfae", "eye": "#2f2226" } },
  "puppet": {
    "svg": "pip.svg",
    "bones": {
      "root":  { "pivot": [150, 240], "parts": ["body"], "motion": ["breathe"] },
      "head":  { "parent": "root", "pivot": [150, 150], "parts": ["head", "eyesOpen", "eyesClosed", "mouth", "mouthOpen"], "motion": ["sway", "tapWobble"] },
      "ears":  { "parent": "head", "pivot": [150, 110], "parts": ["ears"], "motion": [{ "spring": { "k": 60, "c": 6, "drive": "head" } }] }
    },
    "hotspots": [{ "id": "face", "circle": [150, 150, 60] }]
  }
}
```

- `voice` uses the babble parameters from prototype 08.
- `map.figure` picks a voxel figure generator from the engine. Book one has `child`, `quadruped-small` and `bird-small` (for flight). The colours come from the spec. Nobody draws the map figure.
- `bones` is the rig. A bone has a pivot in drawing units, an optional parent, the parts it moves and its motion presets.
- **Draw order is the SVG document order. The hierarchy is the bones.** These are two separate things. The hair can draw behind the torso and still move with the head (§5 of the findings).

Motion presets in book one: `breathe`, `sway`, `tapWobble`, `blink`, `lookAt`, `mouthFlap`, `spring`. Each preset is engine code taken from prototype 06.

### 5.4 Puppet contract (`cast/<id>.svg`)

- Every part that moves on its own is a top-level `<g data-part="name">`.
- Part names are unique in the file. Every bone in the cast JSON names only parts that exist.
- **Required states:** `eyesOpen`, `eyesClosed`, `mouth`, `mouthOpen`. The baker needs all four to make blinks, talking and expressions.
- **Optional states** for expressions: `browsUp`, `browsDown`, `blush`, `tears`.
- Filters, patterns and gradients live in `<defs>` and use user-space units. Then a baked part keeps the same noise as the full drawing.
- The `viewBox` is the drawing unit for pivots and hotspots.

**Expressions** are fixed in the engine: `neutral`, `happy`, `laugh`, `surprised`, `sad`, `sleepy`, `worried`. Each expression maps to part states and motion values. If a puppet has no optional part for an expression, the engine uses the required parts only.

### 5.5 `scenes/<id>.json`

```json
{
  "id": "meadow",
  "seed": 77,
  "slab": { "radius": 62, "height": 7, "ground": "meadow" },
  "time": "golden",
  "props": [
    { "kind": "cottage", "at": [-2, -24], "yaw": 90 },
    { "kind": "pine", "at": [-42, -24], "variant": 0 },
    { "kind": "lantern", "id": "lamp", "at": [26, 40] }
  ],
  "scatter": [
    { "kind": "grass", "circle": [-22, -6, 13], "spacing": 2.4 },
    { "kind": "grass", "lone": 40 }
  ],
  "water": [{ "kind": "pond", "circle": [-27, 20, 12] }],
  "path": { "points": [[-2, -14], [10, 10], [30, 50]], "width": 5 },
  "lights": [{ "kind": "lamp", "prop": "lamp", "reach": 30, "shadows": true }],
  "flight": { "figure": "bird-small", "altitude": 26, "zoom": 1.8 },
  "markers": { "door": [-2, -12], "lamp": [32, 42] },
  "cast": [{ "id": "mira", "at": [16, 6] }, { "id": "pip", "at": [28, 13] }],
  "hotspots": [{ "id": "pip", "target": "cast:pip", "knot": "meet_pip" }]
}
```

- Units are world units, as in prototype 05.
- `kind` names a prop generator in the engine library. Book one has the props from prototype 05: `cottage`, `pine`, `roundTree`, `mushroom`, `lantern`, `post`, `reed`, `grass`. A new prop is an engine change.
- `scatter` places grass by rule. The rules keep grass away from the path, the water and other props, as prototype 05 does.
- The `seed` makes every placement and every model deterministic.
- `flight` is optional. If it is present, the scene shows the **Fly** button. The player becomes a small bird with a chase camera (§4.7 of the findings). Flight is free play: the bird starts no knots and has no goal. The `altitude` must be higher than the tallest prop.

### 5.6 `ui.json`

Every interface string: buttons, hints, menus, save messages and errors. It follows ASD-STE100. The checker scans it (§7).

### 5.7 `puzzles/<id>.json`

A puzzle is data for one of the puzzle engines. The generator makes the board from `params` and `seed`. The author can also give a fixed `board`.

```json
{
  "id": "power_path",
  "engine": "tiles",
  "generator": "pipes",
  "params": { "cols": 5, "rows": 5, "variant": "power", "minMoves": 8 },
  "seed": 314,
  "hints": ["The hatch needs power from the left.", "Corner tiles turn the flow."]
}
```

Puzzle engines in book one:

| Engine | What the child does | Book one uses it for |
|---|---|---|
| `dials` | Turns dials to match sounds or symbols | The translator |
| `tiles` | Turns tiles to connect a flow. Variants: power, stars, light | The power path, the star map, the crystal caves |
| `deduce` | Chooses items or answers that fit every clue | The workbench, the three trials |
| `sequence` | Repeats or orders a sequence of sounds | The Heartsong |

Kid rules for puzzles:
- There is no fail state and no timer. A wrong move is undone with a funny reaction.
- After about 60 s without progress, the puzzle offers a hint. The child can ask for a hint at any time.
- The child can leave a puzzle and come back. The board keeps its state.

## 6. Engine modules

| Module | Source | New work |
|---|---|---|
| `stack` | 05: voxel builder, atlases, impostors, pixel budget | Split from the prototype |
| `props` | 05: prop generators | Read parameters from the scene document |
| `figures` | 05: `girl`, `hedgehog` | Generate `child` and `quadruped-small` from cast colours and height |
| `scene` | 05: object list, scatter, pond, path | **New:** load a scene document |
| `light` | 05: time of day, sun shadows, night layer, lamp-shadow cache | Lights from the scene document |
| `walk` | 05: tap to walk, obstacles, wading | Walk to markers for the `walk` tag |
| `flight` | 05: Fly mode, chase camera, pan and zoom, `bird-small` figure | Read the `flight` block of the scene document |
| `puppet` | 06: part baker, springs, expressions | **New:** a rig player driven by `bones` |
| `voice` | 08: babble, prosody, text sync | None |
| `puzzle` | — | **New:** 4 puzzle engines, a generator for each, and the `puzzle` tag |
| `music` | musikmodel `shared/` | Vendored copy |
| `story` | — | **New:** inkjs runner and tag dispatcher |
| `cache` | — | **New:** bakes in IndexedDB, keyed by `hash(generatorVersion, params, seed)` |
| `save` | — | **New:** autosave of the Ink state, the scene and positions |
| `perf` | 05: HUD, `?bench` | None |

The performance rules in §7 of the findings apply to every module.

## 7. Checkers

`npm run check` runs every checker in Node. Each error gives the file, the place and the fault. Example: `scenes/meadow.json props[3]: the kind "pinee" is not a prop.`

**Book**
- `book.json` names cast, scenes and music files that exist.
- `start` is a knot in `story.ink`.

**Story**
- The Ink compiles.
- Every tag is in the vocabulary (§5.2). Its arguments name cast, scenes, markers, expressions and moods that exist.
- A `walk` tag names a marker in the scene that is loaded at that point.
- Every knot can be reached from `start` or from a hotspot.
- Every knot ends with a choice, a divert or `-> DONE`. No knot is a dead end.

**Kid rules** (provisional limits)
- A story line has 30 words or fewer (reading age 10 to 12).
- A choice has 8 words or fewer.
- A choice point has 3 choices or fewer.
- No choice ends the story badly. Every path reaches an ending.

**Cast**
- The SVG has every required part (§5.4).
- Every bone names parts that exist. Each part has exactly one bone.
- Parent bones exist. The bones form a tree.
- Pivots and hotspots are inside the `viewBox`.
- Voice parameters are inside the ranges of prototype 08.

**Puzzles**
- Every puzzle that a `puzzle` tag names exists.
- **The solver solves every puzzle.** It reports the fewest moves. That number must be at least `minMoves`, so the puzzle is not trivial.
- A `dials` puzzle has exactly one solution. A `deduce` puzzle has exactly one answer that fits every clue.
- Every puzzle has at least 2 hints.

**Scene**
- Every `kind` is in the prop library.
- Props, cast and markers stand on the slab. They do not stand in the water.
- Every hotspot target exists. Every hotspot knot exists.
- Each marker can be reached on foot from where the player starts.
- If the scene has `flight`, its altitude is higher than every prop.
- **Performance budget** (§8).

**Interface copy**
Every string in `ui.json` follows ASD-STE100. The checker flags:
- a sentence of more than 20 words
- a contraction
- the word "unless"
- a contrast tail: "instead of", "rather than" or "X, not Y"

## 8. Performance budget

The budget comes from measurements. **Reference scene:** the prototype 05 meadow. On iPhone 14 Pro it holds 60 fps in every scenario after the lamp-shadow cache (§7 of the findings).

Until a low-cost tablet is measured, a scene may not exceed the reference scene on any of these:

| Measure | How the checker counts it |
|---|---|
| Stack objects | Props, plus scattered grass, plus cast |
| Grass tufts | The scatter result with the scene seed |
| Total slices | Sum of slice counts of all models |
| Point lights with shadows | At most 1 |
| Glow sources | Lamps, windows and fireflies |

The checker prints each measure as a percentage of the reference. After the tablet bench, the limits change to the numbers that hold 60 fps there.

## 9. Previewer

- The previewer opens with `?scene=<id>`, `?knot=<name>` or `?cast=<id>`.
- `?cast=<id>` shows the puppet with the rig overlay, every expression and the voice.
- The previewer reloads when a document changes.
- The previewer shows the frame-time HUD. It keeps `?bench` from prototype 05.
- Headless screenshot tests use the previewer. The tests compare images with a tolerance (§7 of the findings).

## 10. Definition of done for a scene

- `npm run check` passes.
- The bench passes on every target device. Each scenario holds 55 fps or more, with 5% or fewer slow frames.
- The first visit bakes in under 2 s on the low-cost tablet. Later visits load from the cache.
- A person has played it on a phone.

## 11. Build order

| Step | Result | Proves |
|---|---|---|
| M0 | Game repo. The 05 meadow loads from `scenes/meadow.json`. | A scene document costs no performance. The bench matches prototype 05 on iPhone. |
| M1 | Tako's puppet plays from `cast/tako.json` and `tako.svg`. | The data rig works. **Safari bakes SVG filters.** |
| M2 | One Ink knot plays end to end: hotspot → stage → babble → choice → explore. | The tag dispatcher works. |
| M3 | The `tiles` engine with its generator and solver. The power path plays from `puzzles/power_path.json`. | A puzzle document plays, and the checker proves it can be solved. |
| M4 | Every checker in §7, and the other 3 puzzle engines. | Claude can write documents that the build accepts. |
| M5 | Book one: every scene, character, puzzle and ending. Offline PWA. | The pipeline makes a book. |

Test M1 on the iPhone in its first week. Safari SVG baking is the biggest risk that has not been tested.

## 12. Open questions

1. Which low-cost tablet is the second target device?
2. The tag vocabulary will want to grow. Each new tag is an engine change. Keep the list short.
3. After book one: a parametric character generator, so one spec makes the puppet, the map figure and the profile walker.
4. After book one: read-aloud TTS (tiny-voca).
