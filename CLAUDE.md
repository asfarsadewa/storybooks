# Code-first research

This repo is research for a code-first narrative storybook game for children. It is not the game.

- Read `code-first-techniques.md` before you design or build anything for the game. It records the techniques, their maths, their pitfalls, their costs and the decisions made so far.
- `production-pipeline.md` is the spec for making book one: documents, tag vocabulary, puppet contract, checkers, performance budget and build order. The game itself lives in a separate repo.
- `book-one-kai.md` is the design of book one, *The Adventure of Kai the Brave*: story, story state, scenes, cast, puzzles and the engine work it needs.
- `prototypes/` holds the working demos. Each is one self-contained HTML file with no build step. Treat them as reference implementations: copy the techniques, not the file structure.
- `prototypes/05-painted-diorama.html` is the most complete. It exposes `window.__test` (`walkTo(x, y)`, `setTod(0..1)`, `tufts()`, `pond()`, `lamp()`, `perf()`, `opt(bool)`, `fly(bool)`, `steer(-1..1)`, `flight()`) for headless browser tests. The ⚡ button switches between the optimised and original renderers. For real-device numbers, run `python tools/bench-server.py`, then open `05-painted-diorama.html?bench` on the device. The results arrive in `bench-results/`.
- `prototypes/06-baked-svg-puppet.html` is the stage-mode puppet reference. It exposes `window.__test` (`parts()`, `tap(x, y)` in drawing units).
- `prototypes/07-gait-walker.html` is the procedural gait reference. It exposes `window.__test` (`state()`, `gait(name)`, `stop()`, `go(±1)`, `speed(v)`, `pipBtn()`, `pip()`). Planted feet (hers and Pip's) must drift 0 units; check that after any change.
- `prototypes/08-babble-voices.html` is the dialogue-voice reference. It exposes `window.__test` (`plan(text, who, style)`, `state()`). Check audio generators by rendering through `OfflineAudioContext` (peak, RMS, NaNs).
- **Performance is part of done.** Follow the rules in `code-first-techniques.md` §7. Every interactive prototype shows a frame-time HUD (fps, CPU ms, draws per frame, pixel ratio). Report before/after numbers for any rendering change, and say what hardware they came from (headless numbers are for comparison only; real phones are the target).
- No asset files. Everything visual or audible is generated from `(generator, params, seed)` and baked once.
- Before a change in technique, discuss it first and list its edge cases.
- Add new findings to `code-first-techniques.md`, in the matching section, with measured numbers where you have them.
