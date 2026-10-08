# LOW TIDE / starter crawler kit v0.1

Real modular geometry, designed for a small mobile home on a drained seabed.
This is an asset and assembly prototype, not a playable Sindri scene.

## Open first

- `starter_crawler_cutaway.glb`: immediate interior inspection, roof and upper walls absent.
- `starter_crawler_full.glb`: complete assembled crawler; named removable upper-wall/roof nodes.
- `modular_kit_catalog.glb`: every module laid out separately for inspection.
- `modules/`: every module exported at its own reusable origin.
- `preview_cutaway.png` and `preview_exterior.png`: renders of the actual mesh geometry.

In Blender: **File → Import → glTF 2.0 → select a GLB**. All geometry and colors are
embedded; no missing texture paths. Instances share mesh definitions.
To edit one instance without changing siblings, make its mesh single-user first.

Optional `open_in_blender.py` imports the full model, organizes visibility groups,
and saves a `.blend` file. Run from Blender's Scripting workspace, setting `KIT`
to this extracted folder if needed. It does not clear an existing scene.
Blender itself was unavailable during creation: this helper is supplied, but no
prebuilt `.blend` or verified Blender execution is claimed.

## Modular contract

| Property | Convention |
|---|---|
| Units | meters; all instance scales 1 |
| Construction | 1 × 1 m cells, 0.25 m prop snap |
| Source / JSON axes | X right, Y forward, Z up, right-handed |
| GLB axes | X right, Y up, **-Z forward**, right-handed |
| Coordinate conversion | source `(x,y,z)` → GLB `(x,z,-y)` |
| Source yaw | around +Z; converted to GLB +Y |
| Starter deck | 3 m wide × 6 m long, 18 cells |
| Deck elevation | 1.25 m above track-ground reference |
| Floor origin | center of top walking surface; structural thickness below |
| Floor centers | X = -1, 0, 1; Y = -2.5 … 2.5 in 1 m steps |
| Walls | span 1 m in X; local +Y faces exterior; pivot at deck boundary |
| Junctions | wall panel 0.9 m, shared 0.1 m post at each endpoint |
| Low wall | 0.92 m including cap; separate upper sections to 2.2 m |
| Roof | 1 × 1 m; pivot at deck level; underside 2.22 m above it |
| Doorway | 0.82 m clear width, 2.05 m clear height |
| Props | bottom-center pivot, upright; default front faces -Y |
| Tracks | 3 m bogie length, axle along X; ground-center pivot |
| Ramp | hinge pivot at top; extends -Y, 2.75 m run / 1.25 m drop |
| Root | `LT_Crawler_Root`, center of crawler at ground level |

Construction rotations use 90° increments. This does **not** constrain vehicle
rotation: the complete root can translate and rotate freely at runtime.
Positions in `kit_manifest.json` are source Z-up coordinates, not GLB coordinates.
Do not apply the axis conversion twice.

The full assembly is made from precisely the same meshes in the individual
exports, with transforms and shared mesh references, not a separate sculpt.

## Sockets and placement

Floor edges and low-wall equipment mounts expose named `SOCKET_…` empty nodes.
Sockets use standard `LT_mount_025`. The JSON retains source-space positions and
normals. **In exported GLB socket space, +Z points outward, +Y is the up tangent.**
Floor-facing sockets use crawler forward as their up tangent. Socket rotation
quaternions are included, not just positions.

To mate sockets, use `parent_world × parent_socket × rotate_Y(180°) ×
inverse(child_socket)`. This opposes their +Z axes while keeping +Y aligned.
Check occupancy and physical clearance separately; a socket is not a load rating.
Tank mount and bogie chassis sockets are present. Other prototype props use their
documented bottom pivot; extend their socket schemas when gameplay needs it.

The assembly uses explicit transforms from the manifest. It is not an automatic
socket solver. Larger equipment such as cranes and solar panels is **not** modeled.

## Layout and expansion

Front (+Y): helm, stool and windows. Port: bed, workshop and stacked storage.
Starboard: kitchenette and a small engine bay with low vented bulkhead.
Rear: doorway and hinged ramp. A 0.82 m minimum clear route runs through the
center to the helm area. This is a geometric clearance check, not a playtest.

The four tracked bogies are an intentional modular undercarriage: two per side,
each with its own closed tread loop. They are not one continuous belt per side.
Adding a 1 m deck row reuses floors, side panels and roof tiles. Running gear is
a separate constraint: bogies occupy a 3 m attachment length and should be
repositioned/added deliberately rather than stretched. Additional widths require
moving side equipment and checking track clearance, mass and stability.

## Camera and cutaway behavior

Use an orthographic camera around 40–50° elevation. Start by hiding `roof` and
`upper_walls` visibility groups. Keep low walls to preserve room boundaries.
The cutaway GLB removes these groups permanently; use the full GLB for runtime
toggling. Door frames remain intact, so at some yaw angles a frame may obscure
a small part of the view. A later camera-facing wall fade can address this.

Hide render nodes only. Keep physical walls and ceilings active when their
visuals disappear. Avoid fading the whole crawler: it makes depth and interiors
harder to read and can introduce transparent sorting artifacts.

## Materials and geometry

Stylized bevels, low-sided cylinders and reusable PBR color materials. Rust
patches, rivets, seams and plank gaps are geometry. No generated image textures,
external texture dependencies, procedural shader dependencies or alpha sorting.
Windows are open apertures, not glass. Lamps include emissive material and
`KHR_lights_punctual` point lights; engines without that extension still show
the emissive mesh but need their own light components.

This pass is textureless and triangulated, with flat normals per triangle. It
has no authored UV unwrap, baked normal maps, LOD chain or deformation rig.
Bevel geometry softens silhouettes. Parts are closed solids, but the assembled
kit intentionally contains intersecting solids; it is not a single printable
watertight surface. Export groups primitives by material per module for reuse.

Counts and byte sizes are recorded in `kit_manifest.json`; count total triangles
with instances, not just unique geometry. Material primitives can create several
draw calls per module. For production, atlas/batch by material, use engine mesh
instancing, and add LODs; the prototype has not been performance-tested in Sindri.

## Collision and moving-base integration

`collision_recipes.json` contains **source-space** simple box/convex recipes.
It keeps the doorway and window openings open and includes a slope hull for the
ramp. It is data for integration, not an embedded physics extension. Tracks use
coarse boxes; do not drive over individual tread render triangles. Recipes need
validation against Sindri's collider, controller and slope-limit behavior.

Use one vehicle body and child colliders. Store installed-module transforms
relative to `LT_Crawler_Root`. Store an aboard character's local frame/reference
to that same root and account for the base's linear **and angular** motion.
Avoid applying root transform inheritance and platform velocity twice.
At the entrance, explicitly transfer between crawler and world reference frames.

Throttle is persistent vehicle state, independent of the player controlling the
helm. Leaving it should change input ownership while vehicle simulation keeps
running. This behavior, driving physics, local navigation, boarding and camera
logic are design guidance only; none is implemented by these static assets.

The ramp has a usable hinge origin but no animation. Retract it for travel in a
gameplay implementation. Wheels/treads are static and material-batched; animate
the named source parts or split them into movable mesh nodes in a later pass.
Do not rotate the entire bogie to imitate tread motion.

## Rebuild

Python 3 dependencies: `numpy scipy`; verification also uses `trimesh`; renders
use `Pillow`. Install into your preferred virtual environment, then run:

```sh
python build_kit.py
python make_colliders.py
python validate_kit.py
python render_preview.py
```

`build_kit.py` is the editable procedural source for every mesh and placement.
No external assets are used. `validation_report.json` records checks actually
performed and explicitly lists missing application/runtime tests.
