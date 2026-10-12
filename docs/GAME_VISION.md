# Low Tide — Game Vision and Design Bible (Draft)

Status: **Proposed direction, not established canon or implemented functionality.** This document captures the October 2026 design exploration. Treat ideas as candidates to validate in playable slices.

## Elevator pitch

**A survival exploration game about making a home in a world that refuses to stay still.**

Pilot a modular tracked crawler across a mysteriously exposed seabed. Salvage tangible machinery, explore stranded ships and settlements, navigate returning tides, and build a warm, lived-in home that travels with you.

**Design pillars**
1. **The crawler is home:** walk inside, customize, repair, and live aboard even while it moves.
2. **The tide matters:** changing water levels create and close routes and exploration opportunities.
3. **Physical salvage:** recognizable objects and machinery become real installed equipment, not just abstract crafting currency.
4. **Discovery over combat:** mysteries, environments, and people motivate expeditions.
5. **Quiet moments matter:** sheltering from storms, cooking, and watching the landscape are meaningful experiences.

## Lore proposal: The Long Ebb

Decades ago, ocean tides began behaving impossibly. Harbors emptied, currents reversed, and coastlines retreated. Ships became stranded far inland from the new shores; fishing towns looked out over immense salt valleys. People called the ongoing event **The Long Ebb**.

The ocean has not vanished. Water returns in irregular pulses. Some basins flood for hours, others for months, and some have been dry for decades. Recently, certain regions have started getting wetter.

The cause remains disputed. Research logs suggest geological explanations, altered tidal forces, or something deep beneath the former ocean. Preserve ambiguity early on; uncover the truth through environmental storytelling, recovered recordings, and exploration rather than exposition dumps.

### Player identity: a Keeper

The player is an independent **Keeper**, someone who maintains a traveling crawler and makes a living transporting goods, salvaging machinery, carrying messages, and helping stranded people. They inherit a small, unreliable crawler from someone important to them. They are not a chosen savior.

A recovered radio recording points toward an abandoned station called **The Last Signal** and ends: *“When the water returns, don't follow it.”* This is a proposed story hook, not a committed plot resolution.

### World and factions

- **The Anchorage:** stable communities in stranded ships and offshore platforms; trade, repairs, and infrastructure.
- **The Drifters:** independent crawler crews and nomadic salvagers; self-reliance and mobility.
- **The Sounders:** researchers studying tides and the ocean's retreat; remote monitoring stations and hazardous expeditions.

No faction is wholly heroic or villainous. Quests should include towing a stranded crawler, recovering instruments, delivering equipment, and rescuing travelers.

### Regions and discovery

- **Shipwrecks:** cramped interiors, mechanical salvage, personal histories.
- **Drowned settlements:** apartments, submerged basements, abandoned services.
- **Industrial ruins:** offshore rigs, cranes, pumps, fuel and heavy machinery.
- **Deep basins:** strange ecosystems, hydrothermal/geological hazards, major mystery clues.

## Core gameplay loop

**Travel → Explore → Salvage → Build → Prepare → Travel**

### Travel and the moving home

The crawler is a physical, persistent vehicle rather than a teleporting base. Steer manually, set persistent throttle, then leave the helm to walk, cook, repair, or organize inventory while it keeps moving. Navigation upgrades can come later. Terrain, traction, fuel, mass, weather, and breakdowns provide decisions. The player must be able to move safely between crawler-local and world frames while boarding, exiting, and riding a turning vehicle.

### Courier work

Inspired by *Death Stranding*: the Keeper is also a courier. Stations of the
Anchorage, Drifters and Sounders post orders such as a pump, a battery or
water. Each order moves physical cargo from one place to another across a
seabed that the tide keeps reshaping.

- **The route is the challenge,** not combat. Distance, terrain, water depth
  and the tide clock decide how a delivery goes.
- **Cargo is physical.** It has weight, takes damage, and is carried on the
  Keeper's back or in the crawler's hold. Condition on arrival matters.
- **Deliveries connect the world.** A served station comes online: its beacon
  lights, it shares forecasts and it posts new orders. This grows a network,
  echoing *The Last Signal*.
- **Survival is logistics.** Fuel, water and parts are cargo too, so every
  trip weighs what to deliver against what to keep.

### Crawler and Keeper: division of labour

The crawler is not a faster Keeper; speed is at most a later upgrade. It does
what one person on foot cannot: heavy, long-range and sustained work. The
Keeper does what it cannot: squeeze into wrecks, climb, handle small things
and dive. Play alternates between the two: park the crawler as a base camp,
work on foot, return to it.

What only the crawler offers:

- **Hauling:** bulk and oversized cargo, several items in a slotted hold,
  sealed storage that keeps cargo dry and intact, special racks for fragile
  or powered cargo, and a winch or crane for salvage no person can lift.
- **A workshop on tracks:** the workbench travels with you to refine
  salvage into parts, repair cargo before handing it over, and maintain the
  Keeper's gear.
- **Home and survival:** a bed to rest, save and wait out the tide; a
  kitchen, purifier and tanks; light and warmth at night. Its deck stands
  above the water, so high tide is waited out inside, not fled.
- **Reach:** crossing deep mud, channels and long distances; carrying and
  deploying relays, bridges, ladders and pumps that open routes; an antenna
  mast that receives distant orders and forecasts; mounted lights and
  deterrents that guard it while the Keeper is away.
- **Job board:** orders arrive by radio on the crawler, so choosing work,
  packing the hold and planning the route all happen at home.

Each module mounted on the deck changes what the crawler can do. The
crawler's growth is the game's progression.

### Exploration and physical salvage

Inspect wrecks, discover paths, operate mechanisms, and recover specific parts. Small items are carried; heavy generators or engines may need a winch, crane, stabilization, or towing. Salvaged objects should retain identity when installed in the crawler. Avoid reducing every discovery to anonymous scrap.

### Modular building

Three layers:
- **Structure:** deck cells, walls, roof, chassis, tracks, room layouts, clearance, stability.
- **Equipment:** engines, batteries, storage, fuel/water tanks, salvage cranes, diving systems, navigation and defenses.
- **Home:** beds, tables, lighting, kitchen, shelving, rugs and personal clutter.

A small starting crawler should expand gradually, with real space, mass and mounting constraints. Personal decoration is a core reward, not necessarily another stat meter.

### Tides and diving

The tide is the signature mechanic, not decorative lore.
- **Low:** exposed routes, accessible wrecks, easier land travel.
- **Rising:** flooding passages, muddy terrain, time pressure, changing exits.
- **High:** some routes close, sheltered areas matter, and diving opportunities emerge.

Avoid making every rise instantly lethal. Sometimes the right response is to wait safely inside the crawler. Diving should occur in actual water, with shallow swimming-based exploration and deeper expeditions enabled by specialized equipment. This avoids inexplicable diving from a dry crawler doorway.

### Survival philosophy

Emphasize fuel, energy, equipment condition, expedition planning, environmental hazards, and situational oxygen. Keep food, water, sleep and temperature relatively lightweight. Avoid relentless hunger timers and constant repair chores. The experience should be dangerous but occasionally cozy.

### Combat: adapt Orbital Last Stand's auto-attack

**Design intention, not an implemented feature or proven reusable module.** Explore extracting engine-agnostic Decay gameplay concepts from Orbital Last Stand rather than copying wave-mode assumptions.

- Auto-acquire the nearest **valid hostile** within weapon range, subject to line of sight and occlusion.
- Respect weapon cooldown, damage, attack cadence, and range; player controls movement, positioning and avoidance.
- Avoid accidental attacks on wildlife, neutrals, or NPCs. Consider defensive/aggressive modes and explicit hostility rules.
- Crawler-mounted defenses independently acquire targets even when the player is away: turrets, electrical deterrents, floodlights, and upgraded sensors.
- Appropriate threats: territorial seabed creatures, displaced wildlife, malfunctioning scavenger drones, and hostile salvagers. Evasion and nonviolent solutions should often be viable.
- Mobile-first: minimize dedicated attack buttons; prioritize understandable targeting feedback.

**Proposed reusable pipeline:** target acquisition → faction/hostility validation → range/line-of-sight validation → cooldown → attack → damage and feedback.

Check the actual Last Stand implementation and current Sindri/Decay APIs before specifying a shared module or refactor. Keep combat a supporting system, not the primary progression treadmill.

## Progression arc (nonlinear)

1. **A House on Tracks:** repair the inherited crawler, power basics, learn nearby wrecks and tide behavior.
2. **Beyond the Salt:** add living space and salvage gear, meet settlements and traders.
3. **The Drowned Roads:** improve terrain handling, unlock diving, traverse unpredictable basins.
4. **The Last Signal:** explore the deep regions, connect recovered evidence, confront the ocean mystery.

These describe expanding capabilities, not mandatory linear missions. Builders, explorers, and story-focused players should all have worthwhile goals.

## Opening playable sequence

Wake in the cramped crawler; the engine fails. Walk to a nearby abandoned signal station, find a replacement component and a strange radio recording, return to repair the engine, and drive away. A rising-tide warning changes the safe route. Reach higher ground, set the throttle, step away from the helm, and shelter inside at night. The radio mystery can wait until morning.

## First vertical slice: The Last Signal

Keep scope intentionally small:
1. One compact seabed region with an abandoned signal station and legible terrain.
2. A controllable crawler with walkable interior, boarding and persistent throttle.
3. A few tangible salvage objects and a simple repair/install interaction.
4. One localized tide event that changes a route and supports safe retreat.
5. One discoverable recording and environmental narrative beat.
6. A small amount of optional hostile activity to test auto-targeting only **after** movement, exploration and salvage work.

**Success criterion:** the player can leave the crawler, discover and recover something useful, install it, drive to safety, and feel that the vehicle is their home. Not merely that a 3D model renders.

## Current repository reality and engineering boundaries (October 2026)

- `Low_Tide_Kit/` contains real modular GLB assets. The starter deck is **3 × 6 m**, with 1 m construction cells, cutaway/full models and mount conventions.
- `docs/POC.md` documents verified native/WebGPU imported-model rendering, with important limitations.
- `scripts/crawler_drive.decay` currently implements direct-transform prototype driving and equipment visibility toggles, **not** terrain physics, persistent helm throttle, walking a *moving* deck, survival or combat.
- `scripts/crawler_camera.decay` is an experimental third-person camera script; its interaction and collision behavior need validation.
- `crawler/BUILD_MODE.md`, `crawler/LIVE_MODULES.md`, and `crawler/README.md` document partial/prototype construction, parenting, and known mesh-overlap constraints.
- Prototyped on Sindri PR #507 and covered by headless tests:
  - the Keeper as a physics character;
  - a walkable crawler deck with helm boarding;
  - one alternator repair;
  - one courier order (`scripts/courier.decay`) with a single carried cargo
    item, a one-slot cargo bay and a uniform rising tide plane.
- This vision is **not a claim** that diving, terrain-aware tides, inventory, persistence, factions, a multi-slot hold, crafting or auto-attack exist in this repository.
- Coordinate conventions, moving-base character behavior, camera collision, runtime model assembly, performance, and save/load are engineering gates, not assumed solved problems.
- Consult Sindri engine's `AGENTS.md`, `CLAUDE.md` and relevant architecture/capability docs before implementation in the engine.

## Scope guardrails and open questions

- Does the tide operate globally, regionally, or as authored local events? Start with local events before simulation at world scale.
- How much of the world is procedural versus handcrafted? Favor a curated first region.
- How large can the crawler become without undermining intimate interior play?
- Should combat be optional or configurable? Preserve noncombat alternatives.
- How should the mystery resolve without turning the game into a scripted corridor?
- How do players save equipment placement, salvage state, and world changes reliably?

**North star:** *When the world you knew disappears, you build a home you can carry into the unknown.*
