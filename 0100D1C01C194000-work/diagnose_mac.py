"""Bounded first-boot diagnostic; creates a new save/temp directory per run."""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import time
import plistlib
import shutil

work = Path(__file__).resolve().parent
root = work.parent
parser = argparse.ArgumentParser()
parser.add_argument('--seconds', type=int, default=30)
parser.add_argument('--window', action='store_true')
parser.add_argument('--trace-services', action='store_true')
parser.add_argument('--shots', help='comma-separated present frame numbers to capture')
parser.add_argument('--session', help='named isolated save session, reused for restart/load validation')
parser.add_argument('--audio', action='store_true')
parser.add_argument('--no-audio-dump', action='store_true', help='play audio without retaining a long PCM dump')
parser.add_argument('--fslog', action='store_true', help='bounded file-read trace for save reload evidence')
parser.add_argument('--passdump', help='bounded present-frame range for draw/binding diagnostics')
parser.add_argument('--passdump-trigger', action='store_true', help='poll run/passdump.trigger for 1..16 diagnostic frames')
parser.add_argument('--texdump', type=int, help='present frame for attachment readback')
parser.add_argument('--texinfo', help='texture dimensions for bounded storage diagnostics and raw readback')
parser.add_argument('--texdump-trigger', action='store_true', help='one-shot run/texdump.trigger attachment readback')
parser.add_argument('--textrace', help='bounded texture write provenance for WxH')
parser.add_argument('--texraw-mips', action='store_true', help='bounded raw mip-chain readbacks for selected textures')
parser.add_argument('--hidlog', action='store_true', help='bounded actual guest input receipts')
parser.add_argument('--keys', help='built-in scripted controller input')
parser.add_argument('--bundle', action='store_true', help='run an identifiable Mac app bundle for UI inspection')
args = parser.parse_args()
assert 1 <= args.seconds <= 7200
run_id = datetime.now(ZoneInfo('Asia/Taipei')).strftime('%Y%m%dT%H%M%S%z')
run = work / 'run' / run_id
run.mkdir(parents=True)
for name in ('save', 'temp', 'cache'):
    (run / name).mkdir()
save = run / 'save'
if args.session:
    assert re.fullmatch(r'[a-zA-Z0-9_-]{1,48}', args.session)
    save = work / 'sessions' / args.session / 'save'
    save.mkdir(parents=True, exist_ok=True)
profile = work / 'profile/0100D1C01C194000'
host = work / 'build/dmhost'
if args.bundle:
    app = work / 'build/PowerProDiagnostic.app'
    contents = app / 'Contents'
    (contents / 'MacOS').mkdir(parents=True, exist_ok=True)
    shutil.copy2(host, contents / 'MacOS/dmhost')
    (contents / 'Info.plist').write_bytes(plistlib.dumps({
        'CFBundleExecutable': 'dmhost', 'CFBundleIdentifier': 'local.nxnative.pawapuro2025.diagnostic',
        'CFBundleName': 'PowerPro 2025 Diagnostic', 'CFBundlePackageType': 'APPL',
        'CFBundleVersion': '1', 'NSHighResolutionCapable': True,
    }))
    host = contents / 'MacOS/dmhost'
patched = work / 'build/patched_v983040'
build_row = next(line.split('\t') for line in (profile / 'game.tsv').read_text().splitlines()
                 if line.startswith('build\tv983040\t'))
expected = dict(part.split('=', 1) for part in build_row[3:])
for module, build_id in expected.items():
    fixups = (patched / f'{module}.fixups.tsv').read_text()
    actual = re.search(r'^# BUILD_ID\s+(\w+)', fixups, re.M)
    original = (work / 'data/v983040/ExeFS' / module).read_bytes()
    if actual is None or actual[1] != build_id or original[0x40:0x50].hex() != build_id:
        raise SystemExit(f'Build ID mismatch: {module}; refusing guest execution')
env = {k: v for k, v in os.environ.items() if not k.startswith('DM_')}
env.update({
    'DM_ROOT': str(work), 'DM_ROMFS': str(work / 'data/v983040/RomFS'),
    'DM_SAVE': str(save), 'DM_TEMP': str(run / 'temp'),
    'DM_MSL_DIR': str(work / 'build/cache/metal_shader_cache'),
    'DM_FONT_DIR': str(work / 'build/font'),
    'DM_NVN_SHMAP': str(profile / 'shader_map.tsv'),
    'DM_PSO_USER': str(run / 'pso_user.tsv'),
    'DM_PSO_MANIFEST': 'off', 'DM_BOOTPROF': '1',
    'DM_MEMSTAT': str(run / 'memory.tsv'),
})
if args.window:
    env['DM_WINDOW'] = '1'
if args.audio:
    env['DM_AUDIO'] = '1'
    if not args.no_audio_dump:
        env['DM_AUDIO_DUMP'] = str(run / 'audio.pcm')
if args.keys:
    env['DM_KEYS'] = args.keys
if args.fslog:
    env['DM_FSLOG'] = str(run / 'file_reads.tsv')
if args.passdump:
    assert re.fullmatch(r'\d+(-\d+)?', args.passdump)
    env['DM_NVN_PASSDUMP'] = args.passdump
    env['DM_NVN_PASSDUMP_ALL'] = '1'
if args.passdump_trigger:
    env['DM_NVN_PASSDUMP_TRIGGER'] = str(run / 'passdump.trigger')
    env['DM_NVN_PASSDUMP_ALL'] = '1'
if args.texdump is not None:
    assert args.texdump > 0
    env['DM_NVN_TEXDUMP'] = f'{args.texdump}:{run}/attachment_%d.png'
if args.texinfo:
    assert re.fullmatch(r'\d+x\d+(x\d+)?', args.texinfo)
    env['DM_NVN_TEXINFO'] = args.texinfo
    env['DM_NVN_TEXRAW'] = 'info'
if args.texdump_trigger:
    env['DM_NVN_TEXDUMP'] = f'999999999:{run}/attachment_%d.png'
    env['DM_NVN_TEXDUMP_TRIGGER'] = str(run / 'texdump.trigger')
if args.textrace:
    assert re.fullmatch(r'\d+x\d+', args.textrace)
    env['DM_NVN_TEXTRACE'] = args.textrace
if args.texraw_mips:
    env['DM_NVN_TEXRAW_MIPS'] = '1'
if args.hidlog:
    env['DM_HID_RECEIPT_LOG'] = str(run / 'hid-receipts.jsonl')
if args.trace_services:
    env['DM_SVC'] = '1'
    env['DM_IMPORTS'] = '1'
if args.shots:
    assert re.fullmatch(r'\d+(,\d+){0,15}', args.shots)
    env['DM_NVN_SHOT'] = args.shots + ':' + str(run / 'frame_%d.png')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
meta = {
    'run_id': run_id, 'host_os': platform.mac_ver()[0], 'machine': platform.machine(),
    'hardware': subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string'], text=True).strip(),
    'source_commit': subprocess.check_output(['git', '-C', str(root / 'nxnative'), 'rev-parse', 'HEAD'], text=True).strip(),
    'source_status': subprocess.check_output(['git', '-C', str(root / 'nxnative'), 'status', '--short'], text=True),
    'source_diff_sha256': hashlib.sha256(subprocess.check_output(['git', '-C', str(root / 'nxnative'), 'diff', 'HEAD', '--'])).hexdigest(),
    'host_sha256': sha(host), 'profile_sha256': sha(profile / 'game.tsv'),
    'shader_chain_header': (profile / 'dmsh_chain.h').read_text(),
    'fixups_sha256': {m: sha(patched / f'{m}.fixups.tsv') for m in ('main', 'subsdk0', 'sdk')},
    'patched_sha256': {m: sha(patched / f'{m}.patched.bin') for m in expected},
    'module_build_ids': expected,
    'environment': {k: v for k, v in env.items() if k.startswith('DM_')},
    'time_limit_seconds': args.seconds,
    'scope': 'Bounded Mac diagnostic with optional interactive input, audio, and persistent isolated save session. Results require observed UI and log evidence.',
}
(run / 'metadata.json').write_text(json.dumps(meta, indent=2) + '\n')
print('run:', run, flush=True)
log = run / 'boot.log'
started = time.monotonic()
reason = 'process_exit'
with log.open('w') as out:
    p = subprocess.Popen([str(host), str(patched)], cwd=run, env=env, stdout=out, stderr=subprocess.STDOUT)
    try:
        while p.poll() is None:
            if time.monotonic() - started >= args.seconds:
                reason = 'diagnostic_time_limit'
                break
            if log.stat().st_size > 16 * 1024 * 1024:
                reason = 'diagnostic_log_limit'
                break
            if args.fslog and (run / 'file_reads.tsv').exists() and (run / 'file_reads.tsv').stat().st_size > 32 * 1024 * 1024:
                reason = 'diagnostic_file_trace_limit'
                break
            time.sleep(0.1)
    finally:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
result = {'run_id': run_id, 'returncode': p.returncode, 'reason': reason,
          'elapsed_seconds': round(time.monotonic() - started, 3), 'log_bytes': log.stat().st_size}
(run / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
print('log:', log)
