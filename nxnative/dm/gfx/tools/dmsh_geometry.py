"""Strict symbolic proof for the captured translated geometry programs.
Only this proven vertex-local subset is eligible for four-layer replay.
"""
import hashlib
import json
import re
if not __debug__:
    raise RuntimeError("Geometry proof requires assertions; do not use optimized Python")
from pathlib import Path


def verify(text):
    assert 'layout(triangles) in;' in text
    assert 'layout(max_vertices = 12, triangle_strip) out;' in text
    body = text.split('void main()\n{', 1)[1].rsplit('}', 1)[0]
    body = re.sub(r'if \(false\)\s*\{[^{}]*\}', '', body)
    values, out, vertices, groups = {}, {}, [], []
    layer = None

    def expr(s):
        s = s.strip()
        if s in values:
            return values[s]
        if re.fullmatch(r'\d+', s):
            return int(s)
        m = re.fullmatch(r'gl_in\[([^]]+)\]\.gl_Position\.([xyzw])', s)
        if m:
            return ('position', expr(m[1]), m[2])
        m = re.fullmatch(r'_24\[([^]]+)\]\.([xyzw])', s)
        if m:
            return ('uv', expr(m[1]), m[2])
        m = re.fullmatch(r'gp_c3_1\._m0\[(\d+)\]\.([xyzw])', s)
        if m:
            return ('ubo', int(m[1]), m[2])
        m = re.fullmatch(r'fma\(([^,]+), ([^,]+), ([^,]+)\)', s)
        if m:
            return ('fma', *(expr(x) for x in m.groups()))
        if s.count(' * ') == 1:
            a, b = s.split(' * ')
            return ('mul', expr(a), expr(b))
        raise AssertionError('unsupported expression: ' + s)

    for stmt in body.split(';'):
        stmt = stmt.strip()
        if not stmt:
            continue
        if stmt == 'EmitVertex()':
            assert layer is not None
            vertices.append((layer, dict(out)))
        elif stmt == 'EndPrimitive()':
            groups.append(len(vertices))
        else:
            m = re.fullmatch(r'(?:(?:float|int) )?([\w.]+) = (.+)', stmt)
            assert m, 'unsupported statement: ' + stmt
            lhs, rhs = m.groups()
            v = expr(rhs)
            if lhs == 'gl_Layer':
                layer = v
            elif lhs.startswith('gl_Position.') or lhs.startswith('_30.'):
                out[lhs] = v
            else:
                assert re.fullmatch(r'_\d+', lhs), lhs
                values[lhs] = v
    assert len(vertices) == 12 and groups == [3, 6, 9, 12]
    uv = 'layout(location = 0) in vec4 _24[3];' in text
    for index, (actual_layer, actual) in enumerate(vertices):
        l, v = divmod(index, 3)
        assert actual_layer == l
        for component, ch in enumerate('xyzw'):
            row = 4 * l + component
            expected = ('mul', ('position', v, 'x'), ('ubo', row, 'x'))
            for axis in 'yzw':
                expected = ('fma', ('position', v, axis), ('ubo', row, axis), expected)
            assert actual['gl_Position.' + ch] == expected, (index, ch)
        if uv:
            assert actual['_30.x'] == ('uv', v, 'x')
            assert actual['_30.y'] == ('uv', v, 'y')
        assert set(actual) == ({'gl_Position.' + ch for ch in 'xyzw'} | ({'_30.x', '_30.y'} if uv else set()))
    return {'layers': 4, 'vertices_per_layer': 3, 'matrix_rows': 16,
            'position_vertex_local': True, 'uv_xy_identity': uv,
            'execution_enabled': False}


def fused_source(src, recipe, layer):
    # Replaying a vertex shader must not duplicate storage writes or atomics.
    assert not re.search(r'\b(?:device|atomic\w*|threadgroup)\b|\.write\(', src)
    signature = 'vertex main0_out main0_z(main0_in in [[stage_in]], constant spvDescriptorSetBuffer0& spvDescriptorSet0 [[buffer(0)]])'
    assert src.count(signature) == 1
    start = src.index(signature)
    body = src[start + len(signature):].strip()
    assert body.startswith('{') and body.endswith('}') and body.count('{') == body.count('}')
    # The translated zero-near entry is kept intact and called before GS math.
    preamble = src[:src.index('vertex main0_out main0(')]
    helper = 'static inline main0_out geometry_vs(main0_in in, constant spvDescriptorSetBuffer0& spvDescriptorSet0)' + body
    uv = ''
    uvfield = ''
    if recipe['uv_xy_identity']:
        m = re.search(r'float4 (\w+) \[\[user\(locn0\)\]\]', preamble)
        assert m, 'UV input from preceding vertex stage missing'
        uvfield = 'float4 uv [[user(locn0)]];'
        uv = f'o.uv.xy = v.{m[1]}.xy;'
    fields = 'struct geometry_out { float4 position [[position, invariant]]; uint layer [[render_target_array_index]]; ' + uvfield + ' };\n'
    params = 'main0_in in [[stage_in]], constant spvDescriptorSetBuffer0& spvDescriptorSet0 [[buffer(0)]], constant float4* geometry_matrix [[buffer(14)]]'
    code = preamble + helper + '\n' + fields
    for name, convert in [('main0', True), ('main0_z', False)]:
        code += f'vertex geometry_out {name}({params}) {{\nmain0_out v = geometry_vs(in, spvDescriptorSet0);\ngeometry_out o = {{}}; o.layer = {layer};\n'
        for i, axis in enumerate('xyzw'):
            row = layer * 4 + i
            code += f'float4 r{i} = geometry_matrix[{row}];\no.position.{axis} = fma(v.gl_Position.w, r{i}.w, fma(v.gl_Position.z, r{i}.z, fma(v.gl_Position.y, r{i}.y, v.gl_Position.x * r{i}.x)));\n'
        if convert:
            code += 'o.position.z = fma(o.position.z, 0.5, o.position.w * 0.5);\n'
        code += uv + '\nreturn o;\n}\n'
    return code


def build(out, scratch, mtl, chain, game, iosout=None, selected=None):
    """Compile derived VS/GS pairs; ordinary GS failures remain separately reported."""
    import subprocess
    table = game.table('shader_geometry_pairs.tsv')
    if not table.exists():
        return
    out, scratch = Path(out), Path(scratch)
    manifest = {'chain': chain, 'recipe': 'vertex-local-four-layers-v1', 'pairs': {}}
    for line in table.read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        vs, gs = line.split('\t')
        if selected is not None and (vs not in selected or gs not in selected):
            continue
        spv = scratch / (gs + '.spv')
        assert spv.exists(), 'geometry SPIR-V unavailable: ' + gs
        glsl = subprocess.check_output(['spirv-cross', str(spv)], text=True)
        recipe = verify(glsl)
        reflection = json.loads((out / (vs + '_b.json')).read_text())
        assert reflection['chain'] == chain and reflection['stage'] == 'vs'
        assert not reflection.get('drv_reads') and not reflection.get('entry_tf')
        assert all(b['kind'] in ('cbuf', 'c1') and b['msl_type'].startswith('constant ') for b in reflection['bindings'])
        src = (out / (vs + '_b.metal')).read_text()
        keys = []
        for layer in range(4):
            key = hashlib.sha256(f'geometry-v1:{vs}:{gs}:{layer}'.encode()).hexdigest()[:16]
            path = out / (key + '_b.metal')
            path.write_text(fused_source(src, recipe, layer))
            mtl.compile('mac', str(path), str(out / (key + '_b.metallib')))
            if iosout:
                mtl.compile('ios', str(path), str(Path(iosout) / (key + '_b.metallib')))
            r = dict(reflection, key=key + '_b', dm_ctl=key, source=f'geometry fusion {vs}:{gs} layer {layer}',
                     geometry={'ubo_reg': 0, 'ubo_bytes': 256, 'layer': layer, 'vs': vs, 'gs': gs})
            for directory in (out, Path(iosout)) if iosout else (out,):
                target = r
                if iosout and directory == Path(iosout):
                    target = dict(r, chain_metal=json.loads((directory / (vs + '_b.json')).read_text())['chain_metal'])
                (directory / (key + '_b.json')).write_text(json.dumps(target, indent=1) + '\n')
            keys.append(key + '_b')
        manifest['pairs'][vs + ':' + gs] = keys
    for directory in (out, Path(iosout)) if iosout else (out,):
        (directory / '_geometry.json').write_text(json.dumps(manifest, indent=1) + '\n')
    print(f'geometry lowering: {len(manifest["pairs"])} proven VS/GS pairs, {4 * len(manifest["pairs"])} compiled layer variants')
