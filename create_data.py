import os
import shutil
from PIL import Image

FILE = 'rendered_filenames.txt'
NEWLINECHAR = '<N>'

CODE = 'Network/data/code.txt'
IMAGELOC = 'Network/data/imageLoc.txt'
IMAGES = 'Network/data/images'

image_index = 1

for file in open(FILE, 'r').readlines():
    file = file.replace('\n', '')

    image = file.replace('.dart', '.png')

    try:
        i = Image.open(image)
    except:
        continue

    code = open(file, 'r').read()
    code = code.replace('\n', NEWLINECHAR)

    with open(CODE, 'a') as c:
        c.write(code+'\n')

    new_image_loc = os.path.join(IMAGES, f'{image_index}.png')
    shutil.copy(image, new_image_loc)
    
    with open(IMAGELOC, 'a') as img:
        img.write(new_image_loc+'\n')

    image_index += 1