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
        let mut closest = f32::MAX;
        for _ in 0..limit {
            let [px, _, pz] = self.at("explorer");
            let (dx, dz) = (x - px, z - pz);
            closest = closest.min(dx.hypot(dz));
            if closest < 0.2 {
                break;
            }
            // Screen right is +X and screen down is +Z for the starting camera.
            let push = |d: f32| if d.abs() > 0.1 { 60.0 * d.signum() } else { 0.0 };
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

    // Driving still carries the Keeper, who waits beside the crawler.
    let start = game.at("crawler");
    game.hold(Key::ArrowUp, 45);
    let driven = game.at("crawler");
    assert!(driven[2] < start[2] - 1.0, "crawler drove forward: {driven:?}");
    let keeper = game.at("explorer");
    assert!((keeper[0] - driven[0] - 2.0).abs() < 0.01, "Keeper rides along");
    game.tap(Key::Space); // the crawler's reset to its starting place
    game.steps(2);

    // Stepping off hands the Keeper to the physics character, which settles
    // onto the imported seabed instead of hovering or sinking.
    game.tap(Key::F);
    assert!(game.said("Left crawler. WASD to walk, Space to jump, E to interact, F to board."));
    game.steps(60);
    let standing = game.at("explorer")[1];
    assert!((-1.0..0.5).contains(&standing), "on the seabed: {standing}");
    let keeper = game.run.entity("explorer").unwrap();
    assert!(game.run.session.physics3d().character_motion(keeper).unwrap().grounded);

    // A jump leaves the ground and lands again.
    game.tap(Key::Space);
    game.steps(3);
    assert!(game.at("explorer")[1] > standing + 0.2, "jumped");
    game.steps(60);
    assert!(game.said("Keeper jumped") && game.said("Keeper landed"), "{:?}", game.said);
    assert!((game.at("explorer")[1] - standing).abs() < 0.3);

    // The salvage crates are solid: walking into them stops the Keeper.
    game.walk_to(2.0, 3.3, 180);
    game.walk_to(-7.0, 3.3, 240);
    let blocked = game.at("explorer");
    assert!(blocked[0] > -5.5, "crates block the Keeper: {blocked:?}");
    game.hold(Key::A, 10);
    assert!(
        game.keeper_collided_with(&["station-crate-c", "station-crate-d"]),
        "the controller reports the crate hit"
    );

    // Walk to the alternator by the station, recover it, bring it back.
    game.walk_to(2.0, 1.0, 240);
    game.walk_to(5.6, 0.0, 240);
    game.walk_to(6.4, -1.0, 120);
    let alternator = game.at("signal-alternator");
    let here = game.at("explorer");
    let reach = (here[0] - alternator[0]).hypot(here[2] - alternator[2]);
    assert!(reach < 1.8, "reached the alternator: {here:?} ({reach})");
    game.tap(Key::E);
    game.steps(2);
    assert!(game.said("Recovered replacement alternator."), "{:?}", game.said);
    assert!(game.said("Alternator recovered. Return to the crawler and press E to install."));

    game.walk_to(2.0, 0.5, 300);
    game.tap(Key::E);
    game.steps(2);
    assert!(game.said("Alternator installed."), "{:?}", game.said);
    assert!(game.said("Engine repaired. The crawler is ready to travel."));

    // Boarding returns control to the crawler.
    game.tap(Key::F);
    assert!(game.said("Boarded crawler. Arrow keys or touch stick to drive."));
    assert!(!game.said("Keeper recovered beside the crawler"), "never fell through");
}

#[test]
fn a_phone_held_upright_plays_the_whole_loop_by_touch() {
    let mut game = Game::open_on([390.0, 844.0]);
    game.steps(10);

    // At the helm: crawler controls and STEP OFF fit the narrow screen;
    // on-foot buttons are hidden.
    for id in ["touch-cargo", "touch-tank", "touch-antenna", "touch-reset"] {
        assert!(game.active(id), "{id} shown at the helm");
        game.on_screen(id, [0.18, 0.065]);
    }
    game.on_screen("hud-objective", [0.43, 0.05]);
    game.on_screen("touch-board", [0.17, 0.075]);
    assert!(!game.active("touch-jump") && !game.active("touch-action"));

    game.tap_control("touch-board");
    assert!(game.said("Left crawler. WASD to walk, Space to jump, E to interact, F to board."));
    game.steps(40);
    assert!(!game.active("touch-cargo"), "crawler controls hide on foot");
    game.on_screen("touch-jump", [0.17, 0.075]);

    game.tap_control("touch-jump");
    game.steps(40);
    assert!(game.said("Keeper jumped") && game.said("Keeper landed"), "{:?}", game.said);

    // Walk to the alternator with the stick alone, then use the context button.
    // The left-half stick moves the Keeper without turning the camera.
    let start = game.at("explorer");
    let view = game.camera_yaw();
    game.stick_to(2.0, 1.0, 120);
    assert!(game.at("explorer")[2] > start[2] + 1.0, "the stick walks the Keeper");
    assert!((game.camera_yaw() - view).abs() < 0.01, "the stick does not turn the camera");
    game.stick_to(5.6, 0.0, 240);
    game.stick_to(6.4, -1.0, 120);
    assert!(game.active("touch-action"), "PICK UP appears beside the alternator");
    game.on_screen("touch-action", [0.17, 0.075]);
    game.tap_control("touch-action");
    assert!(game.said("Recovered replacement alternator."), "{:?}", game.said);

    game.stick_to(2.0, 0.5, 300);
    assert!(game.active("touch-action"), "INSTALL appears at the crawler");
    game.tap_control("touch-action");
    assert!(game.said("Engine repaired. The crawler is ready to travel."));
    assert!(!game.active("touch-action"));

    // A drag on the right half turns the camera and leaves the Keeper put.
    let here = game.at("explorer");
    let view = game.camera_yaw();
    let [w, h] = game.run.size;
    game.run.input.apply(InputEvent::TouchStarted { id: 3, x: w * 0.7, y: h * 0.45 });
    game.step();
    for i in 1..=10 {
        game.run.input.apply(InputEvent::TouchMoved { id: 3, x: w * 0.7 + i as f32 * 8.0, y: h * 0.45 });
        game.step();
    }
    game.run.input.apply(InputEvent::TouchEnded { id: 3 });
    game.steps(30);
    assert!((game.camera_yaw() - view).abs() > 0.1, "a right-half drag orbits the camera");
    let moved = game.at("explorer");
    assert!((moved[0] - here[0]).hypot(moved[2] - here[2]) < 0.05, "and does not walk");

    game.tap_control("touch-board");
    assert!(game.said("Boarded crawler. Arrow keys or touch stick to drive."));
    assert!(game.active("touch-cargo"));
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
