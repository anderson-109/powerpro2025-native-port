"""Reproducible local preparation using the checked-out project's own tools."""
from pathlib import Path
import importlib.util
import os
import sys

WORK = Path(__file__).resolve().parent
ROOT = WORK.parent
REPO = ROOT / 'nxnative'
TITLE = '0100D1C01C194000'
VERSION = 'v983040'
DATA = WORK / 'data' / VERSION
PROFILE_ROOT = WORK / 'profile'
PROFILE = PROFILE_ROOT / TITLE
PATCHED = WORK / 'build' / f'patched_{VERSION}'
LOGS = WORK / 'logs'
sys.path[:0] = [str(REPO / 'dm/games'), str(REPO / 'dm/tools')]
import game
import profile_guess

spec = importlib.util.spec_from_file_location('nxbuild', REPO / 'scripts/build_ipa_from_nsp.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
builder.pg = profile_guess

os.environ['DM_GAMES_DIR'] = str(PROFILE_ROOT)
os.environ['DM_GAME'] = TITLE
os.environ['DM_ROOT'] = str(WORK)
env = dict(os.environ)
env['PATH'] = str(Path(sys.executable).parent) + os.pathsep + env['PATH']
LOGS.mkdir(exist_ok=True)

def check_identity(g):
    builds = g.builds()[VERSION]
    for module in g.words('modules'):
        assert builder.build_id(DATA / 'ExeFS' / module) == builds[module], module

phase = sys.argv[1]
if phase == 'profile':
    facts = profile_guess.facts_of(DATA / 'ExeFS', ROOT / f'{TITLE}_survey/extract/romfs_manifest.tsv')
    builder.write_profile(PROFILE, int(TITLE, 16), {
        'F': facts, 'name': 'Powerful Pro Baseball 2024-2025', 'display': '1.13.0',
        'version': VERSION, 'survey': str(ROOT / f'{TITLE}_survey/survey.md')})
    g = game.load(TITLE)
    check_identity(g)
    builder.provisional_prep(sys.executable, REPO, env, LOGS, g)
elif phase == 'rewrite':
    g = game.load(TITLE)
    check_identity(g)
    builder.rewrite(sys.executable, REPO, DATA / 'ExeFS', PATCHED, env, LOGS, g)
    builder.refine_after_rewrite(g, DATA, PATCHED)
elif phase == 'build':
    env['MACOSX_DEPLOYMENT_TARGET'] = '26.0'
    g = game.load(TITLE)
    check_identity(g)
    local_chain = WORK / 'build/shader-chain/dm/gfx/tools/dmsh_chain.py'
    if local_chain.exists():
        builder.run([sys.executable, local_chain, '--header'], LOGS / 'dmsh_chain.log', env=env)
    else:
        builder.provisional_prep(sys.executable, REPO, env, LOGS, g)
    builder.build_mac_host(REPO, WORK / 'build/dmhost', env, LOGS, g)
else:
    raise SystemExit('phase must be profile, rewrite or build')
