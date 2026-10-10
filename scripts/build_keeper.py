#!/usr/bin/env python3
"""Export a static Keeper plus a standards-based, rigid-weighted glTF skin.

Skinning is deliberately separate from today's Sindri model compatibility path.
All animations are in place. No engine-specific animator component is invented.
"""
import argparse
import copy
import json
import math
import struct

import numpy as np
from scipy.spatial.transform import Rotation
from keeper_shapes import ROOT, JOINTS, NAMES, PARTS, kit

OUT = ROOT / 'assets/characters/keeper'
BIND = np.array([joint[2] for joint in JOINTS], float)
PARENTS = [None if j[1] is None else NAMES.index(j[1]) for j in JOINTS]
CLIPS = {'idle': (2.0, True), 'walk': (1.0, True), 'run': (.7, True),
         'carry_idle': (2.0, True), 'interact': (1.2, False)}


def pose(clip, time):
    """Local source rotations and pelvis translation, shared by GLB and previews."""
    duration = CLIPS[clip][0]
    phase = time/duration*2*math.pi
    angles = {name: [0., 0., 0.] for name in NAMES}
    bob = 0.
    if clip in ['walk', 'run']:
        running = clip == 'run'
        swing = 36 if running else 23
        for side, offset in [('l', 0), ('r', math.pi)]:
            wave = math.sin(phase+offset)
            thigh = swing*wave
            knee = -(60 if running else 35)*max(0., -wave)
            angles['thigh_'+side][0] = thigh
            angles['shin_'+side][0] = knee
            angles['foot_'+side][0] = -thigh*.35-knee*.45
            angles['upper_arm_'+side][0] = -wave*(28 if running else 16)
            angles['forearm_'+side][0] = 35 if running else 10
        angles['chest'][0] = -8 if running else -2
        angles['chest'][2] = math.sin(phase)*3
        bob = abs(math.sin(phase))*(.028 if running else .012)
    else:
        breath = math.sin(phase)
        angles['chest'][0] = breath*.9
        angles['head'][2] = breath*1.2
        if clip == 'carry_idle':
            for side in ['l', 'r']:
                angles['upper_arm_'+side][0] = 58+breath
                angles['forearm_'+side][0] = 22
        elif clip == 'interact':
            reach = math.sin(math.pi*time/duration)**2
            angles['upper_arm_r'][0] = 65*reach
            angles['forearm_r'][0] = 25*reach
            angles['head'][0] = -12*reach
    quats = np.array([Rotation.from_euler('xyz', angles[n], degrees=True).as_quat() for n in NAMES])
    return quats, bob


def read_glb(path):
    raw = path.read_bytes()
    size = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+size])
    binary_size = struct.unpack_from('<I', raw, 20+size)[0]
    return doc, bytearray(raw[28+size:28+size+binary_size])


def write_glb(path, doc, data):
    doc['buffers'] = [{'byteLength': len(data)}]
    js = json.dumps(doc, separators=(',', ':')).encode()
    js += b' ' * (-len(js) % 4)
    data += b'\0' * (-len(data) % 4)
    path.write_bytes(struct.pack('<4sII', b'glTF', 2, 28+len(js)+len(data)) +
                     struct.pack('<I4s', len(js), b'JSON') + js +
                     struct.pack('<I4s', len(data), b'BIN\0') + data)


def add_accessor(doc, data, values, gltf_type, component=5126):
    values = np.asarray(values, dtype='<f4' if component == 5126 else '<u2')
    data += b'\0' * (-len(data) % 4)
    offset = len(data)
    data.extend(values.tobytes())
    view = len(doc['bufferViews'])
    doc['bufferViews'].append({'buffer': 0, 'byteOffset': offset, 'byteLength': values.nbytes})
    accessor = {'bufferView': view, 'componentType': component, 'count': len(values), 'type': gltf_type}
    if gltf_type == 'SCALAR':
        accessor.update(min=[float(values.min())], max=[float(values.max())])
    doc['accessors'].append(accessor)
    return len(doc['accessors'])-1


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    kit.P = OUT
    item = {'name': 'Keeper', 'asset': 'keeper', 'position': [0, 0, 0], 'yaw_degrees': 0, 'group': 'character'}
    stats = kit.export(OUT/'keeper_static.glb', [item])
    doc, data = read_glb(OUT/'keeper_static.glb')
    doc['nodes'][0]['name'] = 'LT_Keeper'
    doc['asset']['generator'] = 'Low Tide Keeper v0.1'
    for node in doc['nodes']:
        if node.get('children') == []:
            del node['children']
    used = sorted({p['material'] for m in doc['meshes'] for p in m['primitives']})
    remap = {old: new for new, old in enumerate(used)}
    doc['materials'] = [doc['materials'][i] for i in used]
    for mesh in doc['meshes']:
        for primitive in mesh['primitives']:
            primitive['material'] = remap[primitive['material']]
    write_glb(OUT/'keeper_static.glb', doc, data)
    # Keep the static export free of skins, joint attributes and animation clips.
    rig = copy.deepcopy(doc)
    data = bytearray(data)
    joint_base = len(rig['nodes'])
    # The skinned mesh is a scene root; the named character root moves its skeleton.
    rig['nodes'][0]['children'] = [joint_base]
    rig['scenes'][0]['nodes'] = [0, 1]
    for i, (name, parent, _) in enumerate(JOINTS):
        local = BIND[i] if parent is None else BIND[i]-BIND[PARENTS[i]]
        children = [joint_base+j for j, p in enumerate(PARENTS) if p == i]
        node = {'name': name, 'translation': (kit.C@local).tolist(), 'rotation': [0, 0, 0, 1]}
        if children:
            node['children'] = children
        rig['nodes'].append(node)
    inverse_bind = []
    for origin in BIND:
        matrix = np.eye(4)
        matrix[:3, 3] = -(kit.C@origin)
        inverse_bind.append(matrix.T.reshape(16))  # glTF matrices are column-major.
    ibm = add_accessor(rig, data, inverse_bind, 'MAT4')
    rig['skins'] = [{'name': 'Keeper_17_joint_rig', 'skeleton': joint_base,
                     'joints': list(range(joint_base, joint_base+len(JOINTS))), 'inverseBindMatrices': ibm}]
    rig['nodes'][1]['skin'] = 0
    for prim in rig['meshes'][0]['primitives']:
        mat = rig['materials'][prim['material']]['name'].removeprefix('LT_')
        joints = []
        for part in PARTS:
            if part['mat'] == mat:
                joints.extend([[part['joint'], 0, 0, 0]]*(len(part['f'])*3))
        weights = np.zeros((len(joints), 4))
        weights[:, 0] = 1
        prim['attributes']['JOINTS_0'] = add_accessor(rig, data, joints, 'VEC4', 5123)
        prim['attributes']['WEIGHTS_0'] = add_accessor(rig, data, weights, 'VEC4')
        for attribute in ['JOINTS_0', 'WEIGHTS_0']:
            index = prim['attributes'][attribute]
            rig['bufferViews'][rig['accessors'][index]['bufferView']]['target'] = 34962
    rig['animations'] = []
    for name, (duration, loop) in CLIPS.items():
        times = np.linspace(0, duration, 25)
        poses = [pose(name, t) for t in times]
        animation = {'name': name, 'samplers': [], 'channels': [],
                     'extras': {'loop_hint': loop, 'root_motion': False}}
        time_acc = add_accessor(rig, data, times, 'SCALAR')
        for j in range(1, len(JOINTS)):
            source_quats = np.array([p[0][j] for p in poses])
            # Quaternion vector part transforms under the same proper basis rotation.
            quats = np.column_stack([source_quats[:, :3]@kit.C.T, source_quats[:, 3]])
            animation['channels'].append({'sampler': len(animation['samplers']),
                                           'target': {'node': joint_base+j, 'path': 'rotation'}})
            animation['samplers'].append({'input': time_acc, 'output': add_accessor(rig, data, quats, 'VEC4'),
                                          'interpolation': 'LINEAR'})
        translations = [kit.C@(BIND[1]-BIND[0]+[0, 0, p[1]]) for p in poses]
        animation['channels'].append({'sampler': len(animation['samplers']),
                                       'target': {'node': joint_base+1, 'path': 'translation'}})
        animation['samplers'].append({'input': time_acc, 'output': add_accessor(rig, data, translations, 'VEC3'),
                                      'interpolation': 'LINEAR'})
        rig['animations'].append(animation)
    write_glb(OUT/'keeper_rigged.glb', rig, data)
    vertices = np.concatenate([p['v'] for p in PARTS])
    info = {'version': '0.1', 'units': 'meters', 'gltf_axes': 'Y up, -Z forward, X right',
            'source_axes': 'Z up, +Y forward, X right', 'pivot': 'ground center between feet',
            'bounds_source_m': [vertices.min(0).tolist(), vertices.max(0).tolist()],
            'triangles': stats['triangles_instanced'], 'joints': len(JOINTS),
            'weighting': 'Rigid 1.0 to one joint per vertex; segmented low-poly design, not smooth skin.',
            'clips': [{'name': n, 'duration_seconds': d, 'loop_hint': l, 'root_motion': False}
                      for n, (d, l) in CLIPS.items()],
            'engine_status': 'PR #507 slice 6b unimplemented at c50e6b20; use static model for current Sindri.',
            'controller_proposal': {'type': 'capsule', 'height_total_m': 1.87, 'radius_m': .24,
                                    'center_gltf': [0, .935, 0], 'status': 'not configured in engine; excludes arm/backpack protrusions'}}
    (OUT/'manifest.json').write_text(json.dumps(info, indent=2)+'\n')
    print(f'Keeper: {stats["triangles_instanced"]} triangles, {len(JOINTS)} joints, {len(CLIPS)} clips')


def posed_parts(clip, time):
    quats, bob = pose(clip, time)
    matrices = []
    for i, parent in enumerate(PARENTS):
        local = np.eye(4)
        local[:3, :3] = Rotation.from_quat(quats[i]).as_matrix()
        local[:3, 3] = BIND[i] if parent is None else BIND[i]-BIND[parent]
        if i == 1:
            local[2, 3] += bob
        matrices.append(local if parent is None else matrices[parent]@local)
    parts = []
    for part in PARTS:
        j = part['joint']
        moved = part.copy()
        moved['v'] = (part['v']-BIND[j])@matrices[j][:3, :3].T+matrices[j][:3, 3]
        parts.append(moved)
    return parts


def render():
    from render_preview import render as render_meshes
    from PIL import Image
    kit.K['keeper_preview'] = {'parts': PARTS}
    items = [{'name': 'front', 'asset': 'keeper_preview', 'position': [-.65, 0, 0], 'yaw_degrees': 0},
             {'name': 'back', 'asset': 'keeper_preview', 'position': [.65, 0, 0], 'yaw_degrees': 180}]
    render_meshes(items, OUT/'preview.png', w=1200, h=1000, eye=(3, 11, 4), scale=350,
                  target=(0, 0, .95), light=(-3, 6, 8))
    frames = []
    for i in range(16):
        kit.K['keeper_preview']['parts'] = posed_parts('walk', i/16)
        temp = OUT/'.walk_frame.png'
        render_meshes([{'name': 'walk', 'asset': 'keeper_preview', 'position': [0, 0, 0], 'yaw_degrees': 0}],
                      temp, w=480, h=600, eye=(5, 11, 4), scale=240,
                      target=(0, 0, .95), light=(-3, 6, 8))
        frames.append(Image.open(temp).convert('RGB'))
    frames[0].save(OUT/'walk_preview.gif', save_all=True, append_images=frames[1:], duration=62, loop=0)
    temp.unlink()
    kit.K['keeper_preview']['parts'] = PARTS


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    build()
    if args.render:
        render()
