#!/usr/bin/env python3
"""Remove separately controlled equipment nodes from the baked crawler GLB.

Uses only the Python standard library. Retains shared meshes, materials,
buffers and all other nodes without rebuilding the kit.
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Low_Tide_Kit/starter_crawler_cutaway.glb"
OUTPUT = ROOT / "Low_Tide_Kit/starter_crawler_clean_base.glb"
DETACHABLE = {"tank__123"}
# The antenna is in the roof group and absent from the cutaway GLB.


def chunks(blob):
    if len(blob) < 12:
        raise ValueError("GLB too short")
    magic, version, total = struct.unpack_from("<4sII", blob)
    if magic != b"glTF" or version != 2 or total != len(blob):
        raise ValueError("Invalid GLB header")
    result = []
    offset = 12
    while offset < total:
        length, kind = struct.unpack_from("<I4s", blob, offset)
        offset += 8
        result.append((kind, blob[offset:offset + length]))
        offset += length
    if offset != total:
        raise ValueError("Invalid GLB chunk length")
    return result


def clean(source: bytes):
    parts = chunks(source)
    if not parts or parts[0][0] != b"JSON":
        raise ValueError("Missing JSON chunk")
    doc = json.loads(parts[0][1])
    nodes = doc["nodes"]
    removed = {i for i, n in enumerate(nodes) if n.get("name") in DETACHABLE}
    found = {nodes[i]["name"] for i in removed}
    if found != DETACHABLE:
        raise ValueError(f"Expected detachable nodes {sorted(DETACHABLE)}, found {sorted(found)}")
    # Remove links to detached nodes, including their child socket/light nodes.
    for node in nodes:
        if "children" in node:
            node["children"] = [i for i in node["children"] if i not in removed]
    for scene in doc.get("scenes", []):
        if "nodes" in scene:
            scene["nodes"] = [i for i in scene["nodes"] if i not in removed]
    # Keep original indices and unreferenced resources: no remapping needed.
    # Detached nodes themselves are removed from reachability, not the array.
    encoded = json.dumps(doc, separators=(",", ":")).encode("utf-8")
    encoded += b" " * (-len(encoded) % 4)
    rebuilt = [(b"JSON", encoded)] + parts[1:]
    body = b"".join(struct.pack("<I4s", len(data), kind) + data for kind, data in rebuilt)
    return struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body


def main():
    OUTPUT.write_bytes(clean(SOURCE.read_bytes()))
    print(f"Generated {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
