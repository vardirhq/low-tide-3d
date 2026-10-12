# Low Tide asset style and workflow

Low Tide's 3D assets are **written as code**, not modelled. Every asset is a
short list of calls to three building blocks. The style lives in the rules
below and in the existing assets (`Low_Tide_Kit/build_kit.py`,
`scripts/salvage_shapes.py`, `scripts/keeper_shapes.py`). A new asset should
look like it belongs beside the crawler.

## The loop

1. Write a spec in `art/drafts/<name>.py` (see the vocabulary below).
2. Run `python3 scripts/asset.py art/drafts/<name>.py`.
3. Read `art/drafts/out/<name>_report.txt` and fix every **error** and
   **warning**.
4. Look at `art/drafts/out/<name>_preview.png` and compare it with the
   existing assets: proportion, detail density, silhouette. Revise.
5. Repeat until the report is clean and the preview reads well. Change the
   existing calls; don't start over.
6. Promote it: move the calls into the right builder (for example
   `scripts/salvage_shapes.py`), rebuild, and add it to the scene.

Requirements: Python 3 with `numpy`, `scipy` and `Pillow`.

**Without a computer:**

- **On GitHub:** add or edit a spec in `art/drafts/` from the GitHub app or
  website and open a pull request. The *Asset preview* workflow builds it,
  commits the preview to `art/drafts/previews/` and comments with the images
  and reports. Push a fix and it updates.
- **In ChatGPT:** upload `scripts/asset.py` and `Low_Tide_Kit/build_kit.py`
  (plus this guide) to a chat. ChatGPT's own Python sandbox can run
  `python3 asset.py <spec>.py` with the files side by side and show the
  preview inline.

## Vocabulary

```python
asset(name, [width_x, depth_y], 'One-line description: what it is, which side is the front.')
box(name, centre, size, material, bevel=0.015, rot=0)
cyl(name, end_a, end_b, radius, material, segments=12, r2=None)
pipe(name, [point, point, ...], radius, material)
```

- **Units and axes:** metres. X right, Y forward, **Z up**. The exporter
  converts to glTF's Y-up.
- **Origin:** ground centre. The asset stands on z = 0 and fits its footprint,
  centred on x = 0, y = 0.
- **The front faces −Y.** Put labels, dials, doors and controls on the −Y side.
- `box` takes its **centre** and **full size**, so a 0.4 m tall box on the
  ground has centre z = 0.2. `rot` turns it about Z, in radians.
- `cyl` runs from one end point to the other; `r2` makes a cone. `pipe` is a
  bent rod through its points.
- `math` is available. Use loops for repeated details (bolts, ticks, slats).
- Name every part by what it is (`'lid'`, `'hinge'`, `'charge_bar'`), never
  `'part3'`.

## Palette: these names only

| Material | Use |
|---|---|
| `steel` | Frames, bodies, structural metal. Most common. |
| `edge` | Trim, hoops, rails, hinges, worn metal edges |
| `gold` | Small accents: bolts, rivets, knobs, handles, dial rims |
| `rust` | Bases, plinths, old exposed metal, wreckage |
| `dark` | Faceplates, terminals, deep recesses, shadows |
| `teal` | Painted machinery bodies (Low Tide's signature colour) |
| `cream` | Labels, placards, dial faces, painted stripes |
| `wood`, `woodlight` | Planks, furniture, crates |
| `red` | Warnings, positive terminals, hazard marks (sparingly) |
| `rubber` | Tyres, hoses, cables, seals |
| `blue`, `linen`, `paper` | Rare: textiles, documents |
| `lamp`, `screen` | Glowing parts only: lenses, bulbs, displays |

Aim for **one main body colour, one secondary and one accent**. Most of
Astra's assets are `steel`/`teal`/`rust` bodies with `gold` and `cream` details.

## Building an asset in three passes

1. **Silhouette (3–6 parts).** The big shapes that make it recognisable from
   across the seabed: body, base or feet, top. Check the preview's three-quarter
   view before adding anything else.
2. **Structure (5–15 parts).** What it is built from: lids, panels, hoops,
   frames, legs, handles, pipes.
3. **Detail (10–25 parts).** Small parts that tell its story: bolts, ticks,
   knobs, dials, labels, cables, patches. They go mostly on the front (−Y) and
   top. Detail clusters on a few spots; it is not spread evenly.

A finished prop has **10–35 parts and 300–1,500 triangles**. Hard limit: 4,000.

## Proportion and finish

- **Bevels:** the default 0.015 for bodies; 0.025–0.03 for large soft shapes;
  0.002–0.004 for small plates and ticks; 0 for razor-thin marks.
- **Cylinder segments:** 16 for large round bodies (drums, tanks), 12 for
  ordinary parts, 10 for small parts and pipes, 8 or 6 for bolts and rivets.
- **Thickness:** nothing thinner than 5 mm. A label is about 0.018 thick and
  stands about 5 mm proud of its surface.
- **Layering:** details overlap the surface they sit on by a few millimetres,
  so nothing floats and nothing z-fights.
- **Human scale:** the Keeper is 1.87 m. A door is about 2 m, a desk 0.8 m,
  a handle at waist height about 1 m, a carryable item at most about 0.5 m.
- **Chunky:** slightly oversized bolts, knobs and handles read better from the
  game's camera than realistic ones.

## Example

Astra's battery pack: 11 parts, 464 triangles.

```python
asset('battery_pack', [.5, .5], 'Carryable power-cell pack; label and charge bars face -Y.')
# Silhouette
box('case', (0, 0, .18), (.44, .32, .36), 'teal', .025)
box('lid', (0, 0, .37), (.47, .35, .06), 'steel')
# Structure
pipe('handle', [(-.09, .08, .4), (-.09, .08, .49), (.09, .08, .49), (.09, .08, .4)], .018, 'gold')
for x, mat in [(-.15, 'red'), (.15, 'dark')]:
    cyl('terminal', (x, 0, .4), (x, 0, .45), .03, mat, 10)
# Detail, on the front
box('label', (0, -.165, .21), (.27, .018, .17), 'cream')
for x in [-.08, 0, .08]:
    box('charge_bar', (x, -.177, .21), (.035, .008, .07), 'gold', .003)
```

The radio desk (30 parts) in `scripts/salvage_shapes.py` is a good larger
example.

`art/drafts/cargo_rack.py` was made only from this guide, as a test of the
workflow. It took two passes: the first preview showed its slot plates
flickering where they sat flush with the base. That mistake is now an
automatic check.
