# Low Tide 3D: first isometric POC

## Scope

This is an **honest engine integration spike**, not yet a playable crawler. The first scene is intended to show the supplied Astra cutaway crawler on an empty plane from an orthographic, three-quarter view. The untouched kit lives in `Low_Tide_Kit/`.

## Current Sindri blocker

As of the Sindri version inspected on 2026-10-08, `sindri.mesh` supports `cube` and `surface` primitives only. `surface` geometry is inlined into the scene (`vertices`, `uvs`, and **u16 indices**), and the component has no imported mesh/GLB source field. See:

- https://github.com/vardirhq/sindri-engine/blob/main/crates/sindri-scene/src/components/mesh.rs
- https://github.com/vardirhq/sindri-engine/blob/main/examples/cube/assets/demo.scene
- https://github.com/vardirhq/sindri-engine/blob/main/docs/project-format.md

This means writing `"model": "Low_Tide_Kit/starter_crawler_cutaway.glb"` into the scene would *not* work. Do **not** fake the result with a static screenshot or a handcrafted cube that is claimed to be the crawler.

### Minimum general engine capability to unblock this POC

1. Implement an asset-backed glTF 2.0 / GLB mesh resource and stable scene component reference (not game-specific code). Load it through the normal async asset pipeline on native and WebGPU.
2. Preserve node hierarchy and local transforms, glTF materials/base colors, indices and normals. Correctly interpret Y-up GLB coordinates. Handle unsupported glTF features with visible diagnostics.
3. Render the exact committed `Low_Tide_Kit/starter_crawler_cutaway.glb` with a depth-tested ortho world camera, rather than rendering a generated approximation.
4. Test native and browser export, including resource packaging from the external project root. Add a real engine integration test for GLB loading and a headless/game smoke test.
5. Follow Sindri's `AGENTS.md`, `CLAUDE.md`, dependency, parity/capability, and preflight policies. Fix missing capabilities generally in `vardirhq/sindri-engine`, not inside Low Tide.
6. Only mark visual POC complete once an actual in-engine render capture exists and has been inspected.

## POC scene

`poc.scene` contains a genuinely supported **orthographic three-quarter camera**, background/environment, flat cube-ground surface, and a placeholder marker to verify framing. It does **not** claim the crawler GLB renders yet.

The main target asset is `Low_Tide_Kit/starter_crawler_cutaway.glb`, not `preview_cutaway.png`. Start with cutaway, then allow swapping to `starter_crawler_full.glb` to test hiding upper walls and roofs.

Kit coordinates: source manifest uses Z-up; exported GLB already uses Y-up (X right, Y up, -Z forward). Do not convert twice.

## After rendering works

Character marker with WASD, then a physical crew controller; moving/rotating crawler root with persistent throttle; ramp hinge and boarding; modular floor and wall assets. Every added behavior must be authored in Decay, not a custom Rust game loop. Do not rewrite the original `games/low-tide` while this experiment is unproven.
