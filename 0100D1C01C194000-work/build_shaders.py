"""Build this game's shader chain with locally pinned tools, preserving upstream's lock."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import sys

w = Path(__file__).resolve().parent
root = w.parent
repo = root / 'nxnative'
chain = w / 'build/shader-chain'
for rel in ('dm/gfx/tools', 'dm/ios/tools'):
    shutil.copytree(repo / rel, chain / rel, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns('__pycache__', 'obj', 'bin'))
(chain / 'dm/games').mkdir(parents=True, exist_ok=True)
shutil.copy2(repo / 'dm/games/game.py', chain / 'dm/games/game.py')
env = dict(os.environ, DM_GAME='0100D1C01C194000', DM_GAMES_DIR=str(w / 'profile'),
           DM_ROOT=str(w), DOTNET_ROOT='/opt/homebrew/Cellar/dotnet/10.0.400/libexec', J='2',
           IOSOUT=str(w / 'build/ios/dmsh_b'))
env['PATH'] = os.pathsep.join([str(root / '.tools/bin'), str(root / '.tools/venv/bin'),
                             '/opt/homebrew/bin', '/usr/bin', '/bin', '/usr/sbin', '/sbin'])
tools = chain / 'dm/gfx/tools'
profile = w / 'profile/0100D1C01C194000'
cache = w / 'build/cache/metal_shader_cache'
sources = {str(p.relative_to(chain)): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in chain.rglob('*') if p.is_file() and p.suffix in ('.py', '.cs', '.csproj')}
(w / 'logs/shader-tool-sources.json').write_text(json.dumps(sources, indent=2) + '\n')
def run(name, script, *args):
    with (w / 'logs' / name).open('w') as out:
        subprocess.run([sys.executable, str(tools / script), *map(str, args)], env=env,
                       stdout=out, stderr=subprocess.STDOUT, check=True)
run('shader-tool-lock.log', 'dmsh_chain.py', '--update-lock')
run('shader-tool-check.log', 'dmsh_chain.py', '--check-tools')
run('shader-chain-header.log', 'dmsh_chain.py', '--header')
run('shader-build.log', 'dmsh_build.py', w / 'shader/pkg', cache)
version = subprocess.check_output([sys.executable, str(tools / 'dmsh_chain.py')], env=env, text=True).strip()
run('shader-c1-guard.log', 'c1_guard.py', cache / f'b-{version}', profile / 'c1_full.tsv')
run('shader-cb-extent.log', 'cb_extent.py', cache / f'b-{version}', profile / 'cb_extent.tsv')
print('Shader chain:', version)
