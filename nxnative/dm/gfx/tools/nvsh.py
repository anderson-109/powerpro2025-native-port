"""NVSH control/code reader for offline shader extraction.

Program descriptors contain a packed offset list; stage IDs come from the
records, not list position. Descriptor spans locate code even when the control
section's own length excludes trailing metadata. All payload checks fail closed.
"""
import hashlib
import re
import struct
NV_STAGES = ('vs', 'ps', 'gs', 'hs', 'ds', 'cs')
SPH_STAGE = {1: 'vs', 2: 'hs', 3: 'ds', 4: 'gs', 5: 'ps'}
CTL = bytes.fromhex('34127698')
GFX = bytes.fromhex('78563412')
CS = bytes.fromhex('79563412')

def read_nvsh(data):
    records = []
    programs = []
    used_controls = set()
    used_codes = set()
    for m in re.finditer(b'NVSH', data):
        h = m.start()
        assert h + 64 <= len(data), ('NVSH header bounds', hex(h))
        version, kind, nstage, mask = struct.unpack_from('<4I', data, h + 4)
        if version != 1 or not 0 < mask < 64 or nstage != mask.bit_count():
            continue  # A name/string containing NVSH is not a container.
        offsets = struct.unpack_from('<6I', data, h + 20)
        program = []
        extents = []
        for si, rel in enumerate(offsets):
            assert bool(rel) == bool(si < nstage), ('packed stage records', hex(h), si)
            if not rel:
                continue
            r = h + rel
            assert rel >= 64 and r + 24 <= len(data), ('stage descriptor bounds', hex(h), si)
            marker, total, ctl_rel, nctl, code_rel, ncode = struct.unpack_from('<6I', data, r)
            assert 0 <= marker < 6 and mask & 1 << marker, ('stage marker', hex(r), marker)
            st = NV_STAGES[marker]
            assert total == nctl + ncode and ctl_rel == 0 and (code_rel == nctl), ('record layout', hex(r))
            c = r + 24 + ctl_rel
            g = r + 24 + code_rel
            assert 1888 <= nctl and nctl % 4 == 0 and (ncode > 0) and (g + ncode <= len(data)), ('payload bounds', hex(r))
            ctl = data[c:c + nctl]
            code = data[g:g + ncode]
            own_ctl = struct.unpack_from('<I', ctl, 32)[0]
            assert ctl[:4] == CTL and 1888 <= own_ctl <= nctl and (own_ctl % 4 == 0), ('control header', hex(c))
            assert struct.unpack_from('<I', ctl, 1796)[0] == ncode, ('control code length', hex(c))
            thread = struct.unpack_from('<3I', ctl, 1864)
            shared = struct.unpack_from('<I', ctl, 1876)[0]
            if st == 'cs':
                assert all(thread), ('compute group', hex(c))
                assert code[:4] != GFX, ('compute header', hex(g))
            else:
                assert code[:4] == GFX and ncode >= 128, ('graphics header', hex(g))
                actual = SPH_STAGE.get(struct.unpack_from('<I', code, 48)[0] >> 10 & 15)
                assert actual == st, ('SPH stage', hex(g), st, actual)
            assert c not in used_controls and g not in used_codes, ('overlap or duplicate address', hex(r))
            assert CTL not in code and b'BTCDBTCD' not in ctl + code, ('package delimiter collision', hex(c))
            used_controls.add(c)
            used_codes.add(g)
            extents.append((r, g + ncode))
            key = hashlib.sha256(ctl[:own_ctl if own_ctl < 2176 else 2176] + code).hexdigest()[:16]
            item = dict(program=hex(h), record=hex(r), control=hex(c), code=hex(g), stage=st, control_len=nctl, own_control_len=own_ctl, code_len=ncode, key=key, headerless=st == 'cs' and code[:4] != CS, group=list(thread) if st == 'cs' else None, shared=shared if st == 'cs' else None)
            records.append((item, ctl, code))
            program.append(item)
        assert len({x['stage'] for x in program}) == nstage, ('unique stages', hex(h))
        extents.sort()
        assert all((a[1] <= b[0] for a, b in zip(extents, extents[1:]))), ('intra-program overlap', hex(h))
        programs.append(dict(offset=hex(h), kind=kind, stage_mask=mask, stage_count=nstage, stages=program))
    return (programs, records)
