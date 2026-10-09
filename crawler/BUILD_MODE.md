# Floorplan build mode (first slice)

Tap **BUILD** on mobile (or press B on desktop) to switch from the
three-quarter gameplay camera to a second orthographic camera mounted above
the crawler. This camera is parented to the crawler root so the deck remains
centered and its orientation follows the vehicle. The camera uses
`fit: shorter` so the crawler remains framed in portrait and landscape.

While build mode is active, the crawler's driving update returns early.
Tap BUILD again to return to the gameplay camera and resume driving.

This slice implements camera switching and movement pause only. The crawler
roof is already absent in the cutaway base. A placement grid, object selection,
drag/drop, snapping, rotation, collision checks, Weave build tray and save data
are **not** implemented yet. The BUILD control currently uses the same
legacy fixed-position UI as the existing touch buttons and should be migrated
to responsive Weave with the full build HUD.

The camera's 90-degree pitch is authored as a quaternion in the scene; Decay
does not need to mutate camera rotation at runtime.

## Contextual controls

BUILD remains visible in both modes. Normal driving shows RESET and the
floating stick; build mode hides RESET and the stick, shows CARGO/TANK/ANTENNA,
and keeps equipment toggles responsive while movement is paused. Weave styles
the controls for portrait and compact landscape viewports. This is still a
prototype equipment toolbar, not inventory or free placement.
