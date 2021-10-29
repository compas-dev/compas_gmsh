import os
from PIL import Image

here = os.path.dirname(__file__)
paths = []
# for name in os.listdir(here):
for name in ['plate.png', 'tets.png', 'csg.png', 'remeshing.png']:
    filepath = os.path.join(here, name)
    basename, ext = os.path.splitext(filepath)
    paths.append(filepath)

grid = Image.new('RGBA', (1600, 900), (255, 255, 255, 255))

xsize = 800
ysize = 450
n = 2

stop = False
for index in range(len(paths)):
    row = index // n
    col = index - row * n
    print(row, col)
    path = paths[index]
    image = Image.open(path)
    w, h = image.size
    factor = min(xsize / w, ysize / h)
    item = image.resize((int(w * factor), int(h * factor)))
    grid.paste(item, (xsize * col, ysize * row))

grid.save('docs/_images/grid.png', quality=96)
