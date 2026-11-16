# Book one: The Adventure of Kai the Brave

This is the design for the first book. It follows `production-pipeline.md`. Story text in the book is the voice of the fiction, so ASD-STE100 does not apply to it. This design document follows ASD-STE100.

## 1. Brief (from the author)

- **Story:** Kai meets a little alien who cries alone. Kai helps the alien against a tyrant who exiled the alien's family. Kai chooses to help rebuild the alien's planet.
- **Reader:** 10 to 12 years old.
- **Characters:** Kai, a quick genius inventor. Tako, a little alien with a high, quick voice. Zarbor, a tyrant and keeper of an ancient secret, with a low, menacing voice.
- **Places:** a meadow with grass, flowers, groups of trees and a puddle. A fallen spaceship with puzzles. Valda, Tako's planet.
- **Music:** uplifting, heroic and danceable. The ending is heroic and grand, catchy and hummable.
- **Must have:** great puzzles and great punchlines. A meadow flight as a small bird.
- **Must not have:** death, for anyone, enemies included.

## 2. Decisions

| Topic | Decision |
|---|---|
| The bird | The child flies a small bird in the meadow. Later the story reveals that the bird is the Skylark, Kai's scout drone. |
| Act 3 routes | One route in book one: the crystal caves (prism lamp). The echo horn and gravity boots routes come later. |
| Camera in flight | Chase camera (findings §4.7). It holds 60 fps on iPhone 14 Pro. |
| Length | About 20 minutes. |

## 3. Story

### Act 1: the meadow

- Kai arrives with a pocket translator, a new invention that does not work yet.
- A small bird circles the meadow. The child can tap **Fly** at any time and fly as the bird. Flight is free play.
- From the air, the child can see smoke over the woods. This is an optional hint about the fallen ship.
- Kai finds Tako crying beside the puddle. Tako speaks only babble.
- **Puzzle 1, the translator** (dial matching): Kai tunes the translator. The child matches Tako's real babble syllables to glyphs.
- **Choice A, trust:** offer a snack (kind), show a gadget (clever), or sit and wait (patient). The choice sets `trust`.
- Tako explains: Zarbor exiled Tako's family to Valda's moon. Tako's ship came down in the woods.

### Act 2: the fallen ship

- **Puzzle 2, the power path** (tile rotation): Kai routes power to the hatch.
- Inside are 3 ship logs the child can collect. Each one adds to `logs`.
- **First twist:** Tako's family are Song Keepers. Their voices keep Valda's Heartstone glowing. Zarbor banished every Song Keeper.
- **Puzzle 3, the workbench** (deduction): Kai builds the prism lamp from salvaged parts. The clues decide the part list.
- **The Skylark reveal:** the ship's navigation is dead. The little bird lands on the console, opens a panel in its chest and projects a star map. It is Kai's scout drone, the Skylark. Kai built it last summer. Every flight over the meadow was Kai at the controls. Tako asks why a bird has a charging port.
- **Puzzle 4, the star map** (tile rotation, star variant): the child turns star segments. They draw the course to Valda. They launch.

### Act 3: Valda

- The Heartstone is dimming. Singing has been forbidden for years.
- **Puzzle 5, the crystal caves** (tile rotation, light variant): the prism lamp bends a beam through crystals. The beam opens the way to the citadel.
- **Puzzle 6, the three trials:** Zarbor sets three riddles of logic (deduction). The child answers with clues from the story. `trust` decides which hint Tako gives. Nobody fights.
- **Main twist:** Zarbor is not cruel. He is afraid. As a child he was a Song Keeper. He sang alone, and the Heartstone cracked. He believes that singing breaks the stone. In fact, the stone needs many voices together.
- **The mask punchline:** Kai sees that Zarbor's menacing voice comes from an amplifier mask. Without it his voice is small and squeaky.
- **Choice C, the mask:** switch the mask back on for him, ask why he needs it, or tell everyone. Every option leads to understanding. None of them humiliates him. The choice sets `mask`.
- **Puzzle 7, the Heartsong** (sequence memory): the child builds the song from 4 phrases. One phrase comes from each Song Keeper family, and one comes from Zarbor. The phrases make the hummable heroic theme. If `logs` is 3, Zarbor also sings a lost last verse.

### Ending

**Choice D:** how does Kai help rebuild Valda?

| Ending | What happens |
|---|---|
| The Song Engine | Kai builds a machine that carries the song to every city. (Inventor ending) |
| The Skylark gift | Kai gives the Skylark to Tako, so the two friends can always find each other. (Friendship ending) |
| The Choir of Valda | Kai teaches Zarbor to sing with everyone. (Harmony ending) |

`mask` decides Zarbor's part in the epilogue. All endings are heroic. Nobody dies.

## 4. Story state

| Variable | Values | Set by | Used by |
|---|---|---|---|
| `trust` | kind, clever, patient | Choice A | Tako's lines, Tako's hint in the trials |
| `logs` | 0 to 3 | Ship logs found | The secret verse in the Heartsong |
| `mask` | kind, curious, honest | Choice C | Zarbor's part in the epilogue |
| `ending` | engine, gift, choir | Choice D | The ending scene |

Every path goes through the same puzzles and reaches the Heartsong. The checker proves that every path reaches an ending (`production-pipeline.md` §7).

## 5. Scenes

| Scene | Diorama | Time of day | Flight |
|---|---|---|---|
| `meadow` | Grass, flowers, groups of trees, a puddle, smoke over the woods | Morning to golden hour | Yes |
| `crash` | The woods. The ship's hull is open like a pop-up book. | Golden hour to night | No |
| `valda` | Crystal trees, glowing fungi, the cave mouth, the citadel and the Heartstone | Valda dusk | No |

## 6. Cast

| Id | Map figure | Puppet | Voice |
|---|---|---|---|
| `kai` | `child` | Hand-drawn SVG | Babble, middle pitch, quick |
| `tako` | `alien-small` (new) | Hand-drawn SVG | Babble, high, quick |
| `zarbor` | `robed-tall` (new) | Hand-drawn SVG, with a mask part and a no-mask state | Babble, low and slow with the mask. High and small without it |
| `skylark` | `bird-small` | None | Short chirps |

## 7. Puzzles

Book one uses 4 puzzle engines for 7 puzzles. Each puzzle is a document generated from `(generator, params, seed)`. The checker solves each one (`production-pipeline.md` §7).

| # | Puzzle | Engine |
|---|---|---|
| 1 | Translator | Dial matching |
| 2 | Power path | Tile rotation |
| 3 | Workbench | Deduction |
| 4 | Star map | Tile rotation |
| 5 | Crystal caves | Tile rotation |
| 6 | Three trials | Deduction |
| 7 | Heartsong | Sequence memory |

## 8. Engine work for this book

| Work | Size |
|---|---|
| Puzzle module: 4 engines, puzzle documents, the solver in the checker | Large |
| Prop kit: flowers, puddle (pond variant), smoke column | Small |
| Prop kit: ship hull, fins, hatch, panels, cables, console | Medium |
| Biome kit: Valda palette, crystal trees, glowing fungi, cave mouth, citadel, Heartstone | Medium |
| Figures: `alien-small`, `robed-tall` | Medium |
| Puppets: Kai, Tako, Zarbor (SVG, by hand) | Medium |
| Music: 4 moods and the Heartsong theme in musikmodel | Medium |

## 9. Later

- Act 3 routes: the echo horn (whisper market, sequence memory) and the gravity boots (sky spires, grid path). When they arrive, the workbench becomes a choice, and the gadget picks the route.
- Flight in Valda.
