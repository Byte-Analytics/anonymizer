import os.path
import platform

gooey_languages = Tree(os.path.join('gooey', 'languages'), prefix='gooey/languages')
gooey_images = Tree('images', prefix='images')

a = Analysis(['anonymizer.py'], hiddenimports=[], hookspath=None, runtime_hooks=None)
pyz = PYZ(a.pure)
platform = platform.platform(aliased=True, terse=True).split('-', maxsplit=1)[0].lower()  # 'windows', 'macos', 'linux'
if platform == 'windows':
    icon_file = 'program_icon.ico'
else:
    icon_file = 'program_icon.png'
icon = os.path.join('images', icon_file)

name = 'byteanalytics-encoder'  # -{}'.format(platform)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [('u', None, 'OPTION')],
    gooey_languages,
    gooey_images,
    name=name,
    debug=False,
    strip=None,
    upx=False,
    console=False,
    icon=icon,
)

if platform == 'macos':
    app = BUNDLE(
        exe,
        name=name + '.app',
        icon=icon
    )
