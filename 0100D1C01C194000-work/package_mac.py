"""Package a self-contained local Mac build without modifying diagnostic runs."""
from pathlib import Path
import json, plistlib, shutil, subprocess, hashlib, shlex, os, sys
w=Path(__file__).resolve().parent
repo=w.parent/'nxnative'
p=w/'profile/0100D1C01C194000'
v=(p/'dmsh_chain.h').read_text().split('"')[1]
app=w/'dist/macos/PowerPro2025.app'
c=app/'Contents'; r=c/'Resources'; m=c/'MacOS'
for d in (r,m): d.mkdir(parents=True,exist_ok=True)
def install_icon():
    iconset=w/'build/PowerPro2025.iconset'
    iconset.mkdir(parents=True,exist_ok=True)
    for size in (16,32,128,256,512):
        for scale in (1,2):
            pixels=size*scale
            suffix='@2x' if scale==2 else ''
            subprocess.run(['/usr/bin/sips','-s','format','png','-z',str(pixels),str(pixels),str(w/'data/v983040/icon.jpg'),'--out',str(iconset/f'icon_{size}x{size}{suffix}.png')],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['/usr/bin/iconutil','-c','icns',str(iconset),'-o',str(r/'PowerPro2025.icns')],check=True)
    info=c/'Info.plist'
    if info.exists():
        metadata=plistlib.loads(info.read_bytes())
        metadata['CFBundleIconFile']='PowerPro2025.icns'
        info.write_bytes(plistlib.dumps(metadata))
    app.touch()
if '--icon-only' in sys.argv:
    install_icon()
    print(app)
    sys.exit(0)
def clone(src,dst):
    if dst.exists(): return
    subprocess.run(['/bin/cp','-cR',str(src),str(dst)],check=True)
# Compile the bundle entry and host together to preserve Launch Services identity.
clone(w/'data/v983040/RomFS',r/'romfs')
clone(w/'build/patched_v983040',r/'dm')
for name in ('shader_map.tsv','pso_manifest.tsv','c1_full.tsv','cb_extent.tsv','game.tsv','dmsh_chain.h'):
    shutil.copy2(p/name,r/'dm'/name)
(r/'msl').mkdir(exist_ok=True)
clone(w/f'build/cache/metal_shader_cache/b-{v}',r/f'msl/b-{v}')
(r/'dm/font').mkdir(exist_ok=True)
shutil.copyfile('/System/Library/Fonts/Supplemental/Arial Unicode.ttf',r/'dm/font/standard.ttf')
shutil.copy2(w/'build/font/nintendo_ext.ttf',r/'dm/font/nintendo_ext.ttf')
for f in ('LICENSE','README.md'):
    if (repo/f).exists(): shutil.copy2(repo/f,r/f)
source=w/'build/mac_launcher.m'
source.write_text(r'''#import <Cocoa/Cocoa.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/file.h>
#include <stdio.h>
extern char **environ;
static void fail(NSString *message) {
    NSAlert *a=[NSAlert new]; a.messageText=@"PowerPro 2025"; a.informativeText=message; [a runModal]; exit(1);
}
int main(int argc, char **argv) { @autoreleasepool {
    (void)argc; (void)argv;
    NSString *res=NSBundle.mainBundle.resourcePath;
    NSString *base=[NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory,NSUserDomainMask,YES)[0] stringByAppendingPathComponent:@"local.nxnative.powerpro2025"];
    NSFileManager *fm=NSFileManager.defaultManager;
    for (NSString *part in @[@"",@"save",@"temp"]) {
        NSError *err=nil;
        if (![fm createDirectoryAtPath:[base stringByAppendingPathComponent:part] withIntermediateDirectories:YES attributes:nil error:&err]) fail(err.localizedDescription);
    }
    int lock=open([[base stringByAppendingPathComponent:@"run.lock"] fileSystemRepresentation],O_CREAT|O_RDWR,0600);
    if (lock<0 || flock(lock,LOCK_EX|LOCK_NB)) fail(@"Another copy is already running, or its state directory is unavailable.");
    // Independent state: never import or overwrite an active diagnostic session.
    for (NSString *key in NSProcessInfo.processInfo.environment) if ([key hasPrefix:@"DM_"]) unsetenv(key.UTF8String);
    NSDictionary *env=@{@"DM_ROOT":base,@"DM_ROMFS":[res stringByAppendingPathComponent:@"romfs"],@"DM_SAVE":[base stringByAppendingPathComponent:@"save"],@"DM_TEMP":[base stringByAppendingPathComponent:@"temp"],@"DM_MSL_DIR":[res stringByAppendingPathComponent:@"msl"],@"DM_FONT_DIR":[res stringByAppendingPathComponent:@"dm/font"],@"DM_NVN_SHMAP":[res stringByAppendingPathComponent:@"dm/shader_map.tsv"],@"DM_PSO_USER":[base stringByAppendingPathComponent:@"pso_user.tsv"],@"DM_PSO_MANIFEST":@"off",@"DM_WINDOW":@"1",@"DM_AUDIO":@"1"};
    for (NSString *key in env) setenv(key.UTF8String,[env[key] UTF8String],1);
    NSString *log=[base stringByAppendingPathComponent:@"log.txt"];
    [fm removeItemAtPath:[base stringByAppendingPathComponent:@"log.prev.txt"] error:nil];
    [fm moveItemAtPath:log toPath:[base stringByAppendingPathComponent:@"log.prev.txt"] error:nil];
    if (!freopen(log.fileSystemRepresentation,"w",stderr)) fail(@"Cannot create the runtime log.");
    chdir(base.fileSystemRepresentation);
    NSString *host=[NSBundle.mainBundle.executablePath.stringByDeletingLastPathComponent stringByAppendingPathComponent:@"dmhost"];
    char *args[]={(char *)host.fileSystemRepresentation,(char *)[res stringByAppendingPathComponent:@"dm"].fileSystemRepresentation,NULL};
    return dm_host_main(2,args);
} }
''')
entry = source.read_text()
entry = entry.replace('#import <Cocoa/Cocoa.h>', '#import <Cocoa/Cocoa.h>\n#define main dm_host_main\n#include "' + str(repo/'dm/host/main.c') + '"\n#undef main')
source.write_text(entry)
env=dict(os.environ,DM_GAMES_DIR=str(w/'profile'),MACOSX_DEPLOYMENT_TARGET='26.0')
dry=subprocess.check_output(['make','-s','-n','-B','GAME=0100D1C01C194000','dmhost'],cwd=repo/'dm/host',env=env,text=True)
cmd=shlex.split(next(line for line in dry.splitlines() if ' -o dmhost ' in line))
cmd[cmd.index('main.c')]=str(source)
cmd[cmd.index('-o')+1]=str(m/'dmhost')
subprocess.run(cmd,cwd=repo/'dm/host',env=env,check=True)
old=m/'PowerPro2025'
if old.exists(): old.unlink()
(c/'Info.plist').write_bytes(plistlib.dumps({'CFBundleExecutable':'dmhost','CFBundleIdentifier':'local.nxnative.powerpro2025','CFBundleName':'PowerPro 2025','CFBundleDisplayName':'PowerPro 2025','CFBundlePackageType':'APPL','CFBundleVersion':'1.13.0','CFBundleShortVersionString':'1.13.0','LSMinimumSystemVersion':'26.0','NSHighResolutionCapable':True,'GCSupportsControllerUserInteraction':True,'GCSupportedGameControllers':[{'ProfileName':'ExtendedGamepad'}]}))
install_icon()
manifest={'title_id':'0100D1C01C194000','game_version':'1.13.0','chain':v,'host_sha256':hashlib.sha256((m/'dmhost').read_bytes()).hexdigest(),'state_directory':'~/Library/Application Support/local.nxnative.powerpro2025','status':'experimental; full-match and iPad acceptance pending'}
(r/'build-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(app)
