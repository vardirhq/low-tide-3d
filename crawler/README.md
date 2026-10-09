# Modular crawler prototype

This is a **static assembly preview**, not yet a playable construction system.
It uses the existing 1 m grid, 131-item assembly and individual GLBs in
`Low_Tide_Kit/kit_manifest.json`. No new assets or engine changes are required.

## Generate a scene

```bash
python3 scripts/build_modular_crawler.py
```

This writes `crawler-modular.scene` (not committed). To experiment, change
`crawler/layout.json` and rerun. An override key is an **existing instance
name** from the manifest. Its value is a module asset ID, or `null` to remove
it. The sample replaces one crate with a workbench and removes one tank.
All other assembly items are unchanged, except upper walls and roofs hidden
for cutaway viewing.

The generator retains the seabed, camera, lighting, scenery and UI entities
from `poc.scene` but replaces the combined crawler GLB with separate model
entities. It intentionally removes the driving script: separate scene entities
are not guaranteed to follow a moving crawler without validated runtime
parenting support. **Do not replace `poc.scene` with this preview.**

The manifest stores Z-up source coordinates; output uses Y-up GLB coordinates.
Rotation is converted from source yaw to Y-axis quaternion. The generated
entities use the same `sindri.model` component already used by the POC.

## Next engineering gates

1. Validate the generated scene in native and browser runtimes, including
   appearance, module orientation, export of all GLB assets and draw-call cost.
2. Check PR #507's exact Decay API for runtime model entity creation,
   parenting and persistence. Do not assume APIs from engine `main` exist.
3. Once supported, attach modules under the moving crawler root, implement
   occupied-slot checks and allow in-game swaps.
4. Persist selected modules through a documented save mechanism, then add
   resource costs and construction UI.
5. Structural extensions need floor/wall clearance and track placement rules.
   Swapping a module with a different footprint is **not yet validated**.

This intentionally provides a concrete, reproducible foundation without
pretending the game already has dynamic construction.
