# Clean crawler base handoff

The existing `starter_crawler_cutaway.glb` already includes both exterior
tank instances and the roof antenna. The playable scene adds independent
copies of `tank__123` and `antenna__125`, which causes overlapping geometry.

`Low_Tide_Kit/build_kit.py` now defines a new export:
`starter_crawler_clean_base.glb`. It uses the same cutaway assembly as the
current crawler, **except** the `tank__123` and `antenna__125` instances.
The other tank (`tank__124`) stays part of the fixed base for now.
No mesh is manually edited and all other assembly placements are unchanged.

## Generate and integrate

1. In a checkout with Python, NumPy and SciPy installed, run
   `python3 Low_Tide_Kit/build_kit.py`.
2. Inspect `Low_Tide_Kit/starter_crawler_clean_base.glb` alongside the
   existing cutaway and verify the two removed instances.
3. Commit the generated GLB. The generator also rewrites other assets and
   `kit_manifest.json`; review diffs and avoid unrelated changes.
4. Only **after the clean GLB is committed**, change the `crawler`
   entity's `sindri.model.asset` in `poc.scene` to
   `Low_Tide_Kit/starter_crawler_clean_base.glb`.
5. Confirm the attached tank and antenna render once, remain attached while
   driving and turning, and reset with the crawler in native and browser.
   Check the cargo module's clearance separately.

The source-only change deliberately does not switch the playable scene to a
nonexistent GLB. The renderer's batching/instancing work in Sindri PR #507
is a separate dependency for larger modular assemblies.
