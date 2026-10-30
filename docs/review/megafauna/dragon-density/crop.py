"""crop.py IN.png OUT.jpg: the globe part of a shot.py screenshot (the left 770 px of its 1100 x 740 clip), as a JPEG.

Run: uv run --with pillow python docs/review/megafauna/dragon-density/crop.py shots/peoples.png docs/review/megafauna/dragon-density/charts/viewer-peoples.jpg
"""
import sys

from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
im.crop((0, 0, 770, 740)).save(sys.argv[2], quality=86)
