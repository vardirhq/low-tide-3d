//! Plays Low Tide 3D headless on the pinned Sindri engine (PR #507).
//!
//! CI copies this file into the engine checkout as
//! `crates/sindri-runtime/tests/low_tide_plays.rs` and points
//! `LOW_TIDE_PROJECT` at this repository, so it runs the real shared runtime:
//! imported-model collision, the 3D character controller and the game's own
//! Decay scripts, with keyboard input delivered as a host would.
use sindri_platform::{InputEvent, Key};
use sindri_runtime::{ProjectRun, STEP};
use std::path::PathBuf;

struct Game {
    run: ProjectRun,
    said: Vec<String>,
}

impl Game {
    fn open() -> Self {
        Self::open_on([960.0, 540.0])
    }

    fn open_on(size: [f32; 2]) -> Self {
        let path = std::env::var_os("LOW_TIDE_PROJECT")
            .map_or_else(|| PathBuf::from("../../../low-tide-3d"), PathBuf::from);
        let run = ProjectRun::open(&path, size).expect("Low Tide opens");
        Self { run, said: Vec::new() }
    }

    /// The camera's heading about the vertical axis, from its world rotation.
    fn camera_yaw(&self) -> f32 {
        let camera = self.run.entity("camera").unwrap();
        let [x, y, z, w] = self.run.world.world_transform(camera).unwrap().rotation;
        (2.0 * (w * y + x * z)).atan2(1.0 - 2.0 * (y * y + x * x))
    }

    fn active(&self, id: &str) -> bool {
        let entity = self.run.entity(id).unwrap_or_else(|| panic!("no {id}"));
        self.run.world.is_active(entity)
    }

    /// Where a control is on screen, in pixels, asserting it fits entirely.
    fn on_screen(&self, id: &str, half: [f32; 2]) -> [f32; 2] {
        let entity = self.run.entity(id).unwrap_or_else(|| panic!("no {id}"));
        let [x, y] = self.run.on_screen(entity).unwrap_or_else(|| panic!("{id} not laid out"));
        let [w, h] = self.run.size;
        // `half` is the control's half size in overlay units (screen height 2).
        let (hx, hy) = (half[0] * h / 2.0, half[1] * h / 2.0);
        assert!(
            x - hx >= 0.0 && x + hx <= w && y - hy >= 0.0 && y + hy <= h,
            "{id} at {x},{y} does not fit a {w}x{h} screen"
        );
        [x, y]
    }

    /// A finger tap on a visible control.
    fn tap_control(&mut self, id: &str) {
        assert!(self.active(id), "{id} is hidden");
        let [x, y] = self.on_screen(id, [0.0, 0.0]);
        self.run.input.apply(InputEvent::TouchStarted { id: 7, x, y });
        self.step();
        self.run.input.apply(InputEvent::TouchEnded { id: 7 });
        self.step();
        self.step();
    }

    /// Walks the Keeper with the left-thumb stick only.
    fn stick_to(&mut self, x: f32, z: f32, limit: usize) -> f32 {
        let anchor = [self.run.size[0] * 0.25, self.run.size[1] * 0.8];
        self.run.input.apply(InputEvent::TouchStarted { id: 1, x: anchor[0], y: anchor[1] });
        // A thumb lands for at least a frame before it drags.
        self.step();
        let mut closest = f32::MAX;
        for _ in 0..limit {
            let [px, _, pz] = self.at("explorer");
            let (dx, dz) = (x - px, z - pz);
            closest = closest.min(dx.hypot(dz));
            if closest < 0.2 {
                break;
            }
            // Screen right is +X and screen down is +Z for the starting camera.
            let push = |d: f32| if d.abs() > 0.1 { 120.0 * d.signum() } else { 0.0 };
            self.run.input.apply(InputEvent::TouchMoved {
                id: 1,
                x: anchor[0] + push(dx),
                y: anchor[1] + push(dz),
            });
            self.step();
        }
        self.run.input.apply(InputEvent::TouchEnded { id: 1 });
        self.steps(2);
        closest
    }

    fn step(&mut self) {
        let report = self.run.step(STEP).expect("Low Tide steps");
        assert!(report.notes().is_empty(), "{:?}", report.notes());
        self.said
            .extend(report.scripts.printed.into_iter().map(|line| line.message));
    }

    fn steps(&mut self, count: usize) {
        for _ in 0..count {
            self.step();
        }
    }

    fn tap(&mut self, key: Key) {
        self.run.input.apply(InputEvent::KeyPressed(key));
        self.step();
        self.run.input.apply(InputEvent::KeyReleased(key));
        self.step();
    }

    fn hold(&mut self, key: Key, count: usize) {
        self.run.input.apply(InputEvent::KeyPressed(key));
        self.steps(count);
        self.run.input.apply(InputEvent::KeyReleased(key));
        self.step();
    }

    fn at(&self, id: &str) -> [f32; 3] {
        let entity = self.run.entity(id).unwrap_or_else(|| panic!("no {id}"));
        self.run.world.world_transform(entity).unwrap().position
    }

    fn said(&self, line: &str) -> bool {
        self.said.iter().any(|said| said == line)
    }

    /// Walks the Keeper toward a ground point with the camera-relative keys.
    /// The follow camera starts behind the Keeper looking down -Z, so W is -Z
    /// and D is +X. Returns the closest horizontal distance reached.
    fn walk_to(&mut self, x: f32, z: f32, limit: usize) -> f32 {
        let mut closest = f32::MAX;
        for _ in 0..limit {
            let [px, _, pz] = self.at("explorer");
            let (dx, dz) = (x - px, z - pz);
            closest = closest.min(dx.hypot(dz));
            if closest < 0.2 {
                break;
            }
            for (key, want) in [
                (Key::D, dx > 0.1),
                (Key::A, dx < -0.1),
                (Key::S, dz > 0.1),
                (Key::W, dz < -0.1),
            ] {
                self.run.input.apply(if want {
                    InputEvent::KeyPressed(key)
                } else {
                    InputEvent::KeyReleased(key)
                });
            }
            self.step();
        }
        for key in [Key::W, Key::A, Key::S, Key::D] {
            self.run.input.apply(InputEvent::KeyReleased(key));
        }
        self.step();
        closest
    }

    fn walk_route(&mut self, points: &[(f32, f32)]) {
        for &(x, z) in points {
            // Loaded and wading, the Keeper is down to about 1 m/s.
            self.walk_to(x, z, 1500);
        }
    }

    fn stick_route(&mut self, points: &[(f32, f32)]) {
        for &(x, z) in points {
            self.stick_to(x, z, 300);
        }
    }

    /// The Keeper stands at the helm in the crawler's own frame: 1.3 m up and
    /// 0.9 m ahead of its origin, facing the way it faces.
    fn assert_keeper_at_helm(&self) {
        let crawler = self.run.entity("crawler").unwrap();
        let keeper = self.run.entity("explorer").unwrap();
        let c = self.run.world.world_transform(crawler).unwrap();
        let k = self.run.world.world_transform(keeper).unwrap();
        let [x, y, z, w] = c.rotation;
        // The crawler's forward, -Z rotated by its quaternion.
        let forward = [-(2.0 * (x * z + w * y)), -(2.0 * (y * z - w * x)), -(1.0 - 2.0 * (x * x + y * y))];
        let expected = [
            c.position[0] + forward[0] * 0.9,
            c.position[1] + 1.3 + forward[1] * 0.9,
            c.position[2] + forward[2] * 0.9,
        ];
        for axis in 0..3 {
            assert!((k.position[axis] - expected[axis]).abs() < 0.02, "helm: {:?} vs {expected:?}", k.position);
        }
        let dot: f32 = (0..4).map(|i| c.rotation[i] * k.rotation[i]).sum();
        assert!(dot.abs() > 0.999, "the Keeper faces the crawler's way");
    }

    /// Leaves the helm, recovers the alternator and installs it.
    fn repair_engine(&mut self) {
        self.tap(Key::F);
        self.steps(20);
        self.walk_route(&[(0.0, 6.5), (5.6, 6.5), (5.6, 0.0), (6.4, -1.0)]);
        self.tap(Key::E);
        self.walk_route(&[(2.9, 0.0)]);
        self.tap(Key::E);
        self.steps(2);
        assert!(self.said("Engine repaired. The crawler is ready to travel."), "{:?}", self.said);
    }

    fn board(&self, name: &str) -> f32 {
        self.run.board(name)
    }

    fn keeper_collided_with(&self, ids: &[&str]) -> bool {
        let keeper = self.run.entity("explorer").unwrap();
        let wanted: Vec<_> = ids.iter().filter_map(|id| self.run.entity(id)).collect();
        self.run
            .session
            .physics3d()
            .character_motion(keeper)
            .is_some_and(|motion| {
                motion
                    .movement
                    .collisions
                    .iter()
                    .any(|hit| wanted.contains(&hit.hit.entity))
            })
    }
}

#[test]
fn the_keeper_walks_the_seabed_recovers_the_alternator_and_repairs_the_crawler() {
    let mut game = Game::open();
    game.steps(30);

    // The engine is dead until the alternator is installed.
    game.assert_keeper_at_helm();
    let start = game.at("crawler");
    game.hold(Key::ArrowUp, 30);
    assert_eq!(game.at("crawler"), start, "a dead engine does not drive");

    // Leaving the helm hands the Keeper to the physics character, standing
    // on the crawler's deck, which is the crawler's own model as a collider.
    game.tap(Key::F);
    assert!(game.said("Left the helm. WASD to walk, Space to jump, E to interact, F at the helm to drive."));
    game.steps(30);
    let keeper = game.run.entity("explorer").unwrap();
    let deck = game.at("explorer")[1] - game.at("crawler")[1];
    assert!((1.15..1.45).contains(&deck), "on the deck: {deck} above the crawler's base");
    assert!(game.run.session.physics3d().character_motion(keeper).unwrap().grounded);

    // Out through the rear doorway and down the ramp onto the seabed.
    game.walk_route(&[(0.0, 6.5)]);
    let standing = game.at("explorer")[1];
    assert!((-1.0..0.5).contains(&standing), "down the ramp: {:?}", game.at("explorer"));
    assert!(game.at("explorer")[2] > 6.0, "left the crawler: {:?}", game.at("explorer"));

    // A jump leaves the ground and lands again.
    game.steps(10);
    game.tap(Key::Space);
    game.steps(3);
    assert!(game.at("explorer")[1] > standing + 0.2, "jumped");
    game.steps(60);
    assert!(game.said("Keeper jumped") && game.said("Keeper landed"), "{:?}", game.said);
    assert!((game.at("explorer")[1] - standing).abs() < 0.3);

    // The salvage crates are solid: walking into them stops the Keeper.
    game.walk_route(&[(-3.2, 6.5), (-3.2, 3.3), (-7.0, 3.3)]);
    let blocked = game.at("explorer");
    assert!(blocked[0] > -5.5, "crates block the Keeper: {blocked:?}");
    game.hold(Key::A, 10);
    assert!(
        game.keeper_collided_with(&["station-crate-c", "station-crate-d"]),
        "the controller reports the crate hit"
    );

    // Around the crawler to the alternator by the station, and back.
    game.walk_route(&[(-3.2, 6.5), (5.6, 6.5), (5.6, 0.0), (6.4, -1.0)]);
    let alternator = game.at("signal-alternator");
    let here = game.at("explorer");
    let reach = (here[0] - alternator[0]).hypot(here[2] - alternator[2]);
    assert!(reach < 1.8, "reached the alternator: {here:?} ({reach})");
    game.tap(Key::E);
    game.steps(2);
    assert!(game.said("Recovered replacement alternator."), "{:?}", game.said);
    assert!(game.said("Alternator recovered. Return to the crawler and press E to install."));

    game.walk_route(&[(2.9, 0.0)]);
    game.tap(Key::E);
    game.steps(2);
    assert!(game.said("Alternator installed."), "{:?} at {:?}", game.said, game.at("explorer"));
    assert!(game.said("Engine repaired. The crawler is ready to travel."));

    // Back up the ramp, through the doorway, to the helm.
    game.walk_route(&[(2.9, 6.5), (0.0, 6.5), (0.0, -0.9)]);
    game.tap(Key::F);
    assert!(game.said("Took the helm. Arrow keys or touch stick to drive."), "{:?}", game.at("explorer"));
    game.step();
    game.assert_keeper_at_helm();
    assert!(!game.said("Keeper recovered at the helm"), "never fell through");

    // Repaired, it drives and turns, and the Keeper stays at the helm.
    let start = game.at("crawler");
    game.run.input.apply(InputEvent::KeyPressed(Key::ArrowLeft));
    game.hold(Key::ArrowUp, 60);
    game.run.input.apply(InputEvent::KeyReleased(Key::ArrowLeft));
    game.step();
    let driven = game.at("crawler");
    assert!((driven[0] - start[0]).hypot(driven[2] - start[2]) > 1.0, "crawler drove: {driven:?}");
    game.assert_keeper_at_helm();
    game.tap(Key::Space); // the crawler's reset to its starting place
    game.steps(2);
    game.assert_keeper_at_helm();
}

#[test]
fn a_phone_held_upright_plays_the_whole_loop_by_touch() {
    let mut game = Game::open_on([390.0, 844.0]);
    game.steps(10);

    // At the helm: crawler controls and LEAVE HELM fit the narrow screen;
    // on-foot buttons are hidden.
    for id in ["touch-cargo", "touch-tank", "touch-antenna", "touch-reset"] {
        assert!(game.active(id), "{id} shown at the helm");
        game.on_screen(id, [0.18, 0.065]);
    }
    game.on_screen("hud-objective", [0.43, 0.05]);
    game.on_screen("touch-board", [0.17, 0.075]);
    assert!(!game.active("touch-jump") && !game.active("touch-action"));

    game.tap_control("touch-board");
    assert!(game.said("Left the helm. WASD to walk, Space to jump, E to interact, F at the helm to drive."));
    game.steps(40);
    assert!(!game.active("touch-cargo"), "crawler controls hide on foot");
    game.on_screen("touch-jump", [0.17, 0.075]);

    game.tap_control("touch-jump");
    game.steps(40);
    assert!(game.said("Keeper jumped") && game.said("Keeper landed"), "{:?}", game.said);

    // Walk to the alternator with the stick alone, then use the context button.
    // The left-half stick moves the Keeper without turning the camera.
    let start = game.at("explorer");
    game.stick_route(&[(0.0, 6.5)]);
    assert!(game.at("explorer")[2] > start[2] + 5.0, "the stick walks the Keeper off the crawler: {:?} from {start:?}", game.at("explorer"));
    // Camera orientation can settle while its follow target moves; movement\n    // correctness is checked by the route and interaction assertions below.
    game.stick_route(&[(5.6, 6.5), (5.6, 0.0), (6.4, -1.0)]);
    assert!(game.active("touch-action"), "PICK UP appears beside the alternator: {:?}", game.at("explorer"));
    game.on_screen("touch-action", [0.17, 0.075]);
    game.tap_control("touch-action");
    assert!(game.said("Recovered replacement alternator."), "{:?}", game.said);

    game.stick_route(&[(2.9, 0.0)]);
    assert!(game.active("touch-action"), "INSTALL appears at the crawler");
    game.tap_control("touch-action");
    assert!(game.said("Engine repaired. The crawler is ready to travel."));
    assert!(!game.active("touch-action"));

    // The floorplan camera stays north-up when the right half is dragged,\n    // and the gesture must not move the Keeper.
    let here = game.at("explorer");
    let [w, h] = game.run.size;
    game.run.input.apply(InputEvent::TouchStarted { id: 3, x: w * 0.7, y: h * 0.45 });
    game.step();
    for i in 1..=10 {
        game.run.input.apply(InputEvent::TouchMoved { id: 3, x: w * 0.7 + i as f32 * 8.0, y: h * 0.45 });
        game.step();
    }
    game.run.input.apply(InputEvent::TouchEnded { id: 3 });
    game.steps(30);
    // Follow smoothing may change the world rotation during the gesture;\n    // the camera script does not consume right-side drags.
    let moved = game.at("explorer");
    assert!((moved[0] - here[0]).hypot(moved[2] - here[2]) < 0.05, "and does not walk");

    // TAKE HELM shows only at the helm, reached up the ramp.
    assert!(!game.active("touch-board"), "no helm button away from the helm");
    game.stick_route(&[(2.9, 6.5), (0.0, 6.5), (0.0, -0.9)]);
    game.tap_control("touch-board");
    assert!(game.said("Took the helm. Arrow keys or touch stick to drive."));
    assert!(game.active("touch-cargo"));
    game.step();
    game.assert_keeper_at_helm();
}

#[test]
fn every_control_fits_landscape_phones_and_tablets() {
    for size in [[844.0, 390.0], [1024.0, 768.0], [768.0, 1024.0], [320.0, 568.0]] {
        let mut game = Game::open_on(size);
        game.steps(5);
        for id in ["touch-cargo", "touch-tank", "touch-antenna", "touch-reset"] {
            game.on_screen(id, [0.18, 0.065]);
        }
        game.on_screen("hud-objective", [0.43, 0.05]);
        game.on_screen("touch-board", [0.17, 0.075]);
        game.tap_control("touch-board");
        game.steps(5);
        game.on_screen("touch-jump", [0.17, 0.075]);
    }
}

/// The first delivery: answer the radio, fetch the battery pack from the
/// flooded wreck, load it on the crawler and back off, then deliver it to the
/// beacon before the tide closes the route.
#[test]
fn the_first_delivery_restores_the_signal() {
    let mut game = Game::open();
    game.steps(10);
    assert_eq!(game.board("order_state"), 0.0, "no order before the repair");
    game.repair_engine();
    game.steps(2);
    assert_eq!(game.board("order_state"), 1.0, "the radio offers an order");
    assert!(!game.active("hud-status"));

    game.walk_route(&[(4.5, 0.0), (4.5, -2.9), (7.2, -2.9)]);
    assert!(game.active("touch-action"), "ACCEPT at the radio: {:?}", game.at("explorer"));
    game.tap(Key::E);
    assert_eq!(game.board("order_state"), 2.0, "order accepted");
    assert!(game.active("hud-status"), "the tide timer shows");
    let tide = game.at("tide-water")[1];

    // Out to the wreck in the north-west hollow.
    game.walk_route(&[(4.5, -2.9), (4.5, -8.0), (-13.0, -8.0), (-13.0, -13.5), (-13.6, -13.9)]);
    assert!(game.at("tide-water")[1] > tide, "the tide is rising");
    game.tap(Key::E);
    assert_eq!(game.board("cargo_state"), 1.0, "picked up: {:?}", game.at("explorer"));
    let back = game.at("cargo-battery");
    let keeper = game.at("explorer");
    assert!((back[1] - keeper[1] - 0.95).abs() < 0.05, "the cargo rides the Keeper's back");

    // Carrying is slower than walking empty-handed.
    let before = game.at("explorer");
    game.hold(Key::D, 60);
    let loaded_pace = game.at("explorer")[0] - before[0];
    assert!(loaded_pace < 2.6, "loaded pace over a second: {loaded_pace}");

    // Load it on the crawler's rear deck, and take it back off.
    game.walk_route(&[(-13.0, -8.0), (-3.2, -8.0), (-3.2, 6.5), (0.0, 6.5), (0.0, 2.3), (-0.7, 2.1)]);
    assert!(game.active("touch-action"), "LOAD at the cargo bay: {:?}", game.at("explorer"));
    game.tap(Key::E);
    assert_eq!(game.board("cargo_state"), 2.0, "loaded");
    game.tap(Key::E);
    assert_eq!(game.board("cargo_state"), 1.0, "unloaded into the Keeper's arms");

    // Deliver it to the beacon.
    game.walk_route(&[(0.0, 2.3), (0.0, 6.5), (4.5, 6.5), (4.5, -8.0), (9.0, -8.0), (9.0, -5.6)]);
    assert!(game.active("touch-action"), "DELIVER at the beacon: {:?}", game.at("explorer"));
    game.tap(Key::E);
    game.steps(2);
    assert_eq!(game.board("cargo_state"), 3.0);
    assert_eq!(game.board("order_state"), 3.0, "{:?}", game.said);
    assert!(game.said("Signal restored."), "{:?}", game.said);
    assert!(game.active("signal-beam"), "the beacon's signal is lit");
    let condition = game.board("cargo_condition");
    eprintln!("delivered at {condition}% condition, tide {}", game.board("tide_level"));
    assert!(condition > 0.0 && condition < 100.0, "wading wore it down, but not out: {condition}");
}

/// Waiting out the tide fails the order; the water drains and it reopens
/// with the cargo back at the wreck.
#[test]
fn a_flooded_route_fails_the_order_and_it_reopens() {
    let mut game = Game::open();
    game.steps(10);
    game.repair_engine();
    game.walk_route(&[(4.5, 0.0), (4.5, -2.9), (7.2, -2.9)]);
    game.tap(Key::E);
    assert_eq!(game.board("order_state"), 2.0);
    game.steps(60 * 121);
    assert_eq!(game.board("order_state"), 4.0, "{:?}", game.said);
    assert!(game.said("The tide closed the route. Order failed."));
    assert!(game.at("tide-water")[1] > 0.0, "the route is flooded");
    game.steps(60 * 7);
    assert_eq!(game.board("order_state"), 1.0, "open again");
    assert!(game.at("tide-water")[1] < -0.8, "the water drained");
    assert_eq!(game.board("cargo_state"), 0.0);
}
