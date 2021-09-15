import gooey
import platform

gooey_root = os.path.dirname(gooey.__file__)
gooey_languages = Tree(os.path.join(gooey_root, 'languages'), prefix='gooey/languages')
gooey_images = Tree(os.path.join(gooey_root, 'images'), prefix='gooey/images')

a = Analysis(
    ['src/anonymizer.py'],
    hiddenimports=[],
    hookspath=None,
    runtime_hooks=None
)
pyz = PYZ(a.pure)
name = 'bytewireless-encoder-{}'.format(platform.platform(aliased=True, terse=True).split('-', maxsplit=1)[0])
options = [('u', None, 'OPTION')]

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    options,
    gooey_languages,  # Add them in to collected files
    gooey_images,  # Same here.
    name=name,
    debug=False,
    strip=None,
    upx=False,
    console=False,
)

