# Crawler equipment prototype controls

On phones, tap the **CARGO**, **TANK**, or **ANTENNA** buttons along the top
of the screen to install/remove each piece. On keyboards, **1**, **2**, and
**3** do the same thing.

The controls use Sindri's documented physical key names `Digit1`,
`Digit2` and `Digit3`. The current implementation toggles the active
state of each attached model. It does **not** transfer equipment into an
inventory, change gameplay statistics, swap asset types or save installed
states. The models remain parented to the crawler, preserving their local
mounts while hidden.

This is a basic touch prototype. A polished equipment panel, slot compatibility,
persistence and a true swap workflow are subsequent work.
