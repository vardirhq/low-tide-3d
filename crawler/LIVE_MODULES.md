# Live crawler equipment: validation and limitations

The current playable scene uses a **combined cutaway crawler GLB**. The
additional cargo, tank and antenna GLBs are attached in `CrawlerDrive.start`
using `World.set_parent` and local positions. Their source positions come from
`Low_Tide_Kit/kit_manifest.json` (source X/right, Y/forward, Z/up), converted
to Sindri X/right, Y/up, -Z/forward.

The tank and antenna already exist inside the combined GLB. Adding separate
copies at the same mount **overlaps geometry**. This is intentional only as an
attachment proof, not a production-quality modular crawler. The cargo likewise
needs visual clearance validation. Do not add more copies on top of the combined
mesh as a substitute for modular construction.

Run the deterministic checks:

```bash
python3 -m unittest discover -s tests -p 'test_crawler_modules.py'
```

The checks cover GLB asset existence, coordinate conversion, live mount
positions, parent/local-transform use, the steering-sign regression and static
assembly output. They **do not** verify actual native or browser rendering,
model overlaps, scene parenting behavior or draw-call performance.

## Required next step

Generate a *clean* base crawler mesh that omits independently controlled
equipment, or validate a performant assembly/instancing path for separate
structural GLBs. Only then remove the overlapping objects from the combined
crawler. Confirm parenting, rendering and steering in both native and browser
before replacing the existing playable model.
