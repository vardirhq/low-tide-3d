# AGENTS.md

Guidance for coding agents (ChatGPT, Claude, Codex and others) working in
this repository. Read it before making changes.

## What this is

Low Tide 3D: an external game project for the Sindri engine. CI pins engine
PR #507 (`.github/workflows/pages.yml`), checks the Decay scripts against it
and plays the game headless before exporting it to GitHub Pages. Read
`docs/GAME_VISION.md` for the direction (a courier and survival game around a
crawler that is your home) and `docs/POC.md` for what actually works.

## Making 3D assets

Assets are written as code, never modelled by hand or by tool. **Follow
`art/STYLE.md`**: the vocabulary, the palette, the three-pass method and the
build, check and preview loop.

- Draft in `art/drafts/<name>.py` and run `python3 scripts/asset.py art/drafts/<name>.py`.
- Fix every error and warning in the report before calling an asset done.
- Look at the preview image (or ask the person to share it) and revise.
- Reuse existing assets as references; match their scale and detail density.
- Use only palette materials. Do not invent colours or edit the palette.

## Gameplay scripts (Decay)

- Scripts live in `scripts/*.decay`. Check them against the pinned engine
  before pushing. From a Sindri checkout:
  `cargo run --quiet -p decay-lsp -- --check ../low-tide-3d`.
- The preflight can pass code that fails at runtime. `Input.Pointer.overlay.x`
  is an example; use `Input.Pointer.overlay_x`. The headless test is the real
  proof: `tests/headless/low_tide_plays.rs` (see the CI workflow for how it
  runs inside the engine checkout).
- Gameplay state shared between scripts goes through signals
  (`World.send_signal`) and the board (`Game.set` / `Game.get`). See
  `scripts/courier.decay` for the board values in use.

## Conventions

- Scenes and art keep their paths from the project root. Do not add a
  top-level `assets/` folder: Sindri would treat it as the asset root.
- `Low_Tide_Kit/starter_crawler_clean_base.glb` is generated in CI by
  `scripts/make_clean_crawler.py` and is not committed.
- Run the Python tests before pushing: `python3 -m unittest discover -s tests`.
