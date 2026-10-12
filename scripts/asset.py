#!/usr/bin/env python3
"""Build one Low Tide asset from a short spec, then preview and check it.

    python3 scripts/asset.py art/drafts/water_tank.py

writes, beside the spec in `out/`:

- `<name>.glb`          the model, through the same exporter as the crawler kit
- `<name>_preview.png`  front, side, top and three-quarter views, 1 m scale bar
- `<name>_report.txt`   size, triangle count and every problem found

A spec is plain Python using the kit's vocabulary (see art/STYLE.md):

    asset('water_tank', [0.8, 0.8], 'Riveted 300 l drinking-water tank.')
    box('plinth', (0, 0, 0.06), (0.8, 0.8, 0.12), 'rust')
    cyl('shell', (0, 0, 0.12), (0, 0, 1.1), 0.36, 'teal', 16)
    pipe('outlet', [(0.3, -0.2, 0.3), (0.45, -0.3, 0.3)], 0.03, 'edge')

Requires Python 3 with numpy, scipy and Pillow (`pip install numpy scipy pillow`).
No GPU, Blender or engine needed.
"""
from __future__ import annotations

import math
import runpy
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Low_Tide_Kit"))
import build_kit as kit  # noqa: E402  (the shared vocabulary, palette and exporter)

TRIANGLE_BUDGET = 4000
TOUCH = 0.006      # parts closer than this count as joined
OVERHANG = 0.03    # allowed reach past the stated footprint
GROUNDED = 0.03    # a part this close to z=0 stands on the ground
VIEW = 360         # pixels per view


# --------------------------------------------------------------------------- #
# Building


def build(spec: Path) -> dict:
    """Run a spec and return the kit's record of the one asset it defines."""
    existing = set(kit.K)
    made: list[str] = []

    def asset(name, footprint, description, sockets=None):
        if name in existing:
            raise SystemExit(f"'{name}' is already a kit asset; choose a new name")
        made.append(name)
        kit.begin(name, list(footprint), description,
                  [kit.socket("mount", [0, 0, 0], [0, 0, -1])] + list(sockets or []))

    def need_asset(fn):
        def wrapped(*args, **kwargs):
            if not made:
                raise SystemExit("call asset(name, footprint, description) first")
            return fn(*args, **kwargs)
        return wrapped

    env = {"asset": asset, "box": need_asset(kit.box), "cyl": need_asset(kit.cyl),
           "pipe": need_asset(kit.pipe), "socket": kit.socket, "math": math}
    runpy.run_path(str(spec), init_globals=env)
    if len(made) != 1:
        raise SystemExit(f"a spec defines exactly one asset; this one defined {len(made)}")
    return kit.K[made[0]]


# --------------------------------------------------------------------------- #
# Checks


def check(a: dict) -> tuple[list[str], list[str]]:
    """Problems as (errors, warnings), each worded for the person or model fixing it."""
    errors, warnings = [], []
    parts = a["parts"]
    if not parts:
        return ["the asset has no parts"], []
    lo = np.array([p["v"].min(0) for p in parts])
    hi = np.array([p["v"].max(0) for p in parts])
    names = [p["name"] for p in parts]

    unknown = sorted({p["mat"] for p in parts if p["mat"] not in kit.M})
    if unknown:
        errors.append(f"unknown materials {unknown} would be dropped from the model; "
                      f"use only: {', '.join(kit.M)}")
    if lo[:, 2].min() > GROUNDED:
        errors.append(f"nothing touches the ground: the lowest part starts at z={lo[:, 2].min():.3f} m")
    for i in np.where(lo[:, 2] < -0.005)[0]:
        errors.append(f"'{names[i]}' goes {-lo[i, 2]:.3f} m below the ground (z<0)")

    w, d = a["footprint_m"][0] / 2 + OVERHANG, a["footprint_m"][1] / 2 + OVERHANG
    for i in range(len(parts)):
        if lo[i, 0] < -w or hi[i, 0] > w or lo[i, 1] < -d or hi[i, 1] > d:
            warnings.append(f"'{names[i]}' reaches outside the {a['footprint_m']} m footprint "
                            f"(x {lo[i, 0]:.2f}..{hi[i, 0]:.2f}, y {lo[i, 1]:.2f}..{hi[i, 1]:.2f})")

    # Floating parts: not on the ground and not touching any other part.
    for i in range(len(parts)):
        if lo[i, 2] <= GROUNDED:
            continue
        gap = np.maximum(np.maximum(lo - hi[i], lo[i] - hi), 0).max(axis=1)
        gap[i] = np.inf
        if gap.min() > TOUCH:
            warnings.append(f"'{names[i]}' floats: it touches neither the ground nor another part "
                            f"(nearest gap {gap.min():.3f} m)")

    flicker: dict[tuple[str, str], int] = {}
    for i, j in _coplanar_pairs(parts):
        flicker[(names[i], names[j])] = flicker.get((names[i], names[j]), 0) + 1
    for (a_name, b_name), count in flicker.items():
        times = f" ({count} places)" if count > 1 else ""
        warnings.append(f"'{a_name}' and '{b_name}' have faces in the same plane and will flicker "
                        f"(z-fighting){times}; move the smaller one about 5 mm proud")

    size = hi - lo
    for i in np.where(size.min(axis=1) < 0.004)[0]:
        warnings.append(f"'{names[i]}' is thinner than 4 mm and will hardly be visible")

    tris = sum(len(p["f"]) for p in parts)
    if tris > TRIANGLE_BUDGET:
        warnings.append(f"{tris} triangles is over the {TRIANGLE_BUDGET} budget; "
                        "drop tiny details or lower cylinder segments")
    return errors, warnings


def _faces(part):
    """A part's flat faces as {(normal, offset): (min_xyz, max_xyz)}, rounded to 1 mm."""
    tri = part["v"][part["f"]]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    length = np.linalg.norm(n, axis=1)
    keep = length > 1e-9
    tri, n = tri[keep], n[keep] / length[keep, None]
    faces = {}
    for t, normal in zip(tri, n):
        key = (tuple(np.round(normal, 2)), round(float(normal @ t[0]), 3))
        if key[0] == (0.0, 0.0, -1.0) and abs(key[1]) < 0.002:
            continue  # resting on the ground: never seen
        lo, hi = t.min(0), t.max(0)
        if key in faces:
            faces[key] = (np.minimum(faces[key][0], lo), np.maximum(faces[key][1], hi))
        else:
            faces[key] = (lo, hi)
    return faces


def _coplanar_pairs(parts):
    """Pairs of parts with overlapping faces in one plane, facing the same way."""
    faces = [_faces(p) for p in parts]
    found = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            if parts[i]["mat"] == parts[j]["mat"]:
                continue  # same colour: flicker is invisible
            for key, (lo_a, hi_a) in faces[i].items():
                other = faces[j].get(key)
                if other is None:
                    continue
                overlap = np.minimum(hi_a, other[1]) - np.maximum(lo_a, other[0])
                # Two in-plane axes overlap by more than 2 mm (the third is the plane).
                if (overlap > 0.002).sum() >= 2:
                    found.append((i, j))
                    break
    return found


def report(a: dict, errors: list[str], warnings: list[str]) -> str:
    parts = a["parts"]
    v = np.concatenate([p["v"] for p in parts]) if parts else np.zeros((1, 3))
    lo, hi = v.min(0), v.max(0)
    used = sorted({p["mat"] for p in parts})
    lines = [
        f"asset      {a['id']}",
        f"description {a['description']}",
        f"footprint  {a['footprint_m'][0]} x {a['footprint_m'][1]} m",
        f"size       {hi[0]-lo[0]:.2f} wide (x) x {hi[1]-lo[1]:.2f} deep (y) x {hi[2]-lo[2]:.2f} tall (z) m",
        f"parts      {len(parts)}   triangles {sum(len(p['f']) for p in parts)}",
        f"materials  {', '.join(used)}",
        "",
        f"errors     {len(errors)}",
        *[f"  - {e}" for e in errors],
        f"warnings   {len(warnings)}",
        *[f"  - {w}" for w in warnings],
    ]
    if not errors and not warnings:
        lines.append("\nNo problems found. Judge the preview for proportion and detail.")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- #
# Preview: a small flat-shaded software renderer (no GPU)

LIGHT = np.array([-0.45, -0.6, 0.66])
LIGHT /= np.linalg.norm(LIGHT)


def _rgb(hexcolor: str) -> np.ndarray:
    return np.array([int(hexcolor[i:i + 2], 16) for i in (1, 3, 5)], float)


def _views():
    """Rotation matrices taking source coordinates (X right, Y forward, Z up)
    to camera coordinates (x right, y up, z toward the viewer)."""
    front = np.array([[1, 0, 0], [0, 0, 1], [0, -1, 0]], float)     # looks along +Y
    side = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], float)       # from +X
    top = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], float)        # from above, +Y up
    yaw, pitch = math.radians(-35), math.radians(28)
    rz = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]])
    three_quarter = rx @ front @ rz
    return [("front (-Y)", front), ("side (+X)", side), ("top", top), ("three-quarter", three_quarter)]


def render(a: dict, path: Path) -> None:
    tri = np.concatenate([p["v"][p["f"]] for p in a["parts"]])            # (n, 3, 3)
    col = np.concatenate([np.repeat(_rgb(kit.M.get(p["mat"], ("#ff00ff",))[0])[None], len(p["f"]), 0)
                          for p in a["parts"]])
    normal = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    normal /= np.maximum(np.linalg.norm(normal, axis=1)[:, None], 1e-12)
    views = _views()
    # One scale for every view, so sizes compare between them.
    extent = max(np.ptp((tri.reshape(-1, 3) @ m.T)[:, :2], axis=0).max() for _, m in views)
    scale = (VIEW - 60) / max(extent, 0.2)
    sheet = Image.new("RGB", (VIEW * 2, VIEW * 2 + 26), (232, 228, 214))
    draw = ImageDraw.Draw(sheet)
    for k, (label, m) in enumerate(views):
        image = _draw(tri @ m.T, normal @ m.T, col, scale, ground=m if k < 2 else None)
        ox, oy = (k % 2) * VIEW, (k // 2) * VIEW
        sheet.paste(Image.fromarray(image), (ox, oy))
        draw.text((ox + 8, oy + 6), label, fill=(40, 50, 52))
    bar = scale  # one metre in pixels
    y = VIEW * 2 + 13
    draw.line([(10, y), (10 + bar, y)], fill=(40, 50, 52), width=3)
    draw.text((16 + bar, y - 6), f"1 m   {a['id']}", fill=(40, 50, 52))
    sheet.save(path)


def _draw(tri, normal, col, scale, ground=None):
    img = np.full((VIEW, VIEW, 3), (232, 228, 214), np.uint8)
    zbuf = np.full((VIEW, VIEW), -np.inf)
    pts = tri[:, :, :2].reshape(-1, 2)
    centre = (pts.min(0) + pts.max(0)) / 2
    def to_px(xy):
        return np.stack([VIEW / 2 + (xy[..., 0] - centre[0]) * scale,
                         VIEW / 2 - (xy[..., 1] - centre[1]) * scale + 10], -1)
    if ground is not None:  # the ground line z=0, seen edge-on
        gy = to_px(np.array([0.0, (np.array([0, 0, 0.0]) @ ground.T)[1]]))[1]
        img[int(np.clip(gy, 0, VIEW - 1)):, :] = (214, 206, 186)
    lit = 0.38 + 0.62 * np.clip(normal @ (LIGHT @ np.eye(3)), 0, 1)
    # Faces pointing away still draw (closed meshes), shaded by their front side.
    lit = np.where(normal[:, 2] < 0, 0.38 + 0.62 * np.clip(-normal @ LIGHT, 0, 1), lit)
    shade = np.clip(col * lit[:, None], 0, 255)
    px = to_px(tri[:, :, :2])
    depth = tri[:, :, 2]
    for t in range(len(tri)):
        (x0, y0), (x1, y1), (x2, y2) = px[t]
        xmin, xmax = int(max(min(x0, x1, x2), 0)), int(min(max(x0, x1, x2) + 1, VIEW))
        ymin, ymax = int(max(min(y0, y1, y2), 0)), int(min(max(y0, y1, y2) + 1, VIEW))
        if xmin >= xmax or ymin >= ymax:
            continue
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-9:
            continue
        gx, gy = np.meshgrid(np.arange(xmin, xmax) + 0.5, np.arange(ymin, ymax) + 0.5)
        w0 = ((x1 - gx) * (y2 - gy) - (x2 - gx) * (y1 - gy)) / area
        w1 = ((x2 - gx) * (y0 - gy) - (x0 - gx) * (y2 - gy)) / area
        w2 = 1 - w0 - w1
        inside = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not inside.any():
            continue
        z = w0 * depth[t, 0] + w1 * depth[t, 1] + w2 * depth[t, 2]
        sub = zbuf[ymin:ymax, xmin:xmax]
        win = inside & (z > sub)
        sub[win] = z[win]
        img[ymin:ymax, xmin:xmax][win] = shade[t]
    return img


# --------------------------------------------------------------------------- #


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    spec = Path(argv[0]).resolve()
    a = build(spec)
    out = spec.parent / "out"
    out.mkdir(exist_ok=True)
    errors, warnings = check(a)
    text = report(a, errors, warnings)
    (out / f"{a['id']}_report.txt").write_text(text)
    render(a, out / f"{a['id']}_preview.png")
    if not any("unknown materials" in e for e in errors):
        # The kit's exporter reports paths relative to its own folder.
        kit.P = out
        kit.export(out / f"{a['id']}.glb",
                   [{"name": a["id"], "asset": a["id"], "position": [0, 0, 0],
                     "yaw_degrees": 0, "group": "draft"}])
    print(text)
    print(f"preview  {out / (a['id'] + '_preview.png')}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
