# Crawler equipment prototype controls

While playing the scene, use **1** to install/remove the rear cargo,
**2** for the auxiliary tank, and **3** for the roof antenna.

The controls use Sindri's documented physical key names `Digit1`,
`Digit2` and `Digit3`. The current implementation toggles the active
state of each attached model. It does **not** transfer equipment into an
inventory, change gameplay statistics, swap asset types or save installed
states. The models remain parented to the crawler, preserving their local
mounts while hidden.

This is a keyboard-only prototype. Touch controls, an equipment UI,
slot compatibility, persistence and a true swap workflow are subsequent work.
