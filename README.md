# storybooks

Experiments for a storybook game where every asset (world, characters, light, music) is generated from code.

| Prototype | What it shows |
|---|---|
| `prototypes/01-sprite-stack-flight.html` | Sprite stacking basics: a plane over a procedural island |
| `prototypes/02-mode7-stack-racer.html` | Mode 7 ground plus perspective sprite stacks, LOD, camera presets |
| `prototypes/03-mode7-stack-racer-refined.html` | The same with refined voxels and baked per-voxel lighting |
| `prototypes/04-gouache-svg-illustration.html` | A gouache-style illustration from SVG shapes and filters |
| `prototypes/05-painted-diorama.html` | Painted voxel diorama: walking, wading, ripples, grass and wind, sun and lamp shadows, puppet dialogue. Optimised renderer (cached layers, impostors, pixel budget) with an A/B toggle and a frame-time HUD |
| `prototypes/06-baked-svg-puppet.html` | The gouache drawing as an animated puppet: baked SVG parts on a canvas rig, springs, expressions, taps |
| `prototypes/07-gait-walker.html` | The character in profile with procedural gaits (walk, run, skip, sneak), a Froude-based speed slider, card-flip turns, and Pip's four-legged walk, trot and gallop, with a footfall chart |
| `prototypes/08-babble-voices.html` | Synthesized dialogue voices: blip, chatter and formant babble per character, with intonation, text synced to the audio clock, and mouth flap |
| `prototypes/09-style-lab.html` | The house style for the voxel look (outlines, rounded corners), the per-frame budget for cache rebuilds, and the after-drag freeze fix |

Open any file in a browser. The findings are in `code-first-techniques.md`.

The findings record every phone benchmark: what was slow on an iPhone, why, and the fix. Section 7 holds the performance rules. Book one, *The Adventure of Kai the Brave*, is built from this research. Play it at https://storybooks.asfarlab.fun.

## Licence

MIT. See `LICENSE`.
