import json
import os.path
from PIL import Image
import random

BASE_DIR = os.path.dirname(__file__)
PIE_DATABASE = os.path.join(BASE_DIR, 'pies.json')

with open(PIE_DATABASE) as f:
    pie_data_raw = json.load(f)

# Total pies
def step1_total():
    total_pies = 0
    for m, p in pie_data_raw.items():
        total_pies += len(p)
    print('Total pies: {}'.format(total_pies))

# Pies to make
def step2_pies_to_make():
    pies_to_make = []
    for m, ps in pie_data_raw.items():
        for p, _, date in ps:
            if not date:
                pies_to_make.append((m, p))
    print('{} remaining pies to make:'.format(len(pies_to_make)))
    for m, p in pies_to_make:
        print('    {} ({})'.format(p, m))

# Pies to photograph
# TODO - photographs for the remaining (and convert them to JPG)
def shortname(pie):
    '''canonically shorten the pie name from the JSON data
    and also directory names on the file system'''
    paren = pie.find('(')
    if paren != -1:
        pie = pie[:paren]
    pie = pie.lower()
    return ''.join(ch for ch in pie if ch.isalpha())

PHOTO_DIR = os.path.join(os.path.expanduser('~'), 'Pictures', 'pies')
photo_dirs = {}
for f in os.listdir(PHOTO_DIR):
    potential_dir = os.path.join(PHOTO_DIR, f)
    if os.path.isdir(potential_dir):
        short = shortname(f)
        photo_dirs[short] = potential_dir

pies_with_photos = []
pies_without_photos = []
for _, ps in pie_data_raw.items():
    for p, _, date in ps:
        short = shortname(p)
        dir_ = photo_dirs.get(short)
        if dir_ and os.listdir(dir_):
            pies_with_photos.append((p, date))
        else:
            pies_without_photos.append((p, date))

def step3_pies_to_photograph():
    print('{} pies with photos:'.format(len(pies_with_photos)))
    for p, date in sorted(pies_with_photos, key=lambda x: x[1]):
        print('    {} {}'.format(p, date))
    print('{} pies without photos:'.format(len(pies_without_photos)))
    for p, date in sorted(pies_without_photos, key=lambda x: x[1]):
        print('    {} {}'.format(p, date))

# Generate photo collage
# TODO - generate it using arbitrary photos -- maybe in order of when the pies were made, with Alison selfie in the middle
def square(image):
    (w, h) = image.size
    if w == h:
        return image
    elif w > h:
        diff = w - h
        trim = diff / 2
        # 800 x 600 --> 0 0 800 600
        # left upper right lower
        return image.crop((trim, 0, w - trim, h))
    else:
        diff = h - w
        trim = diff / 2
        return image.crop((0, trim, w, h - trim))

def create_collage(cols, rows, thumbnail_pixels, images, center, filename="collage.jpg"):
    width = cols * thumbnail_pixels
    height = rows * thumbnail_pixels
    collage = Image.new('RGB', (width, height))

    thumbnails = []
    for p in images:
        im = square(Image.open(p))
        im.thumbnail((thumbnail_pixels, thumbnail_pixels))
        thumbnails.append(im)
    i = 0
    x = 0
    y = 0
    for col in range(cols):
        for row in range(rows):
            if abs(col - cols // 2) <= 1 and abs(row - rows // 2) <= 1:
                if col == cols // 2 - 1 and row == rows // 2 - 1:
                    center_im = square(Image.open(center))
                    # center_im.thumbnail((thumbnail_pixels * 3, thumbnail_pixels * 3))
                    # collage.paste(center_im, (x, y))
                    center_im.thumbnail((thumbnail_pixels * 2, thumbnail_pixels * 2))
                    collage.paste(center_im, (x + thumbnail_pixels//2, y + thumbnail_pixels//2))
            else:
                collage.paste(thumbnails[i], (x, y))
                i += 1
            y += thumbnail_pixels
        x += thumbnail_pixels
        y = 0

    collage.save(filename)

def step4_collage():
    photo_per_pie = []
    bonus_photos = []
    for p, date in pies_with_photos:
        short = shortname(p)
        dir_ = photo_dirs[short]
        files = [f for f in os.listdir(dir_) if f != '.DS_Store']
        if len(files) == 1:
            f = random.choice(files)
            photo_per_pie.append(os.path.join(dir_, f))
        else:
            f1, f2 = random.sample(files, 2)
            photo_per_pie.append(os.path.join(dir_, f1))
            bonus_photos.append(os.path.join(dir_, f2))
    
    print(len(photo_per_pie))
    print(len(bonus_photos))
    
    selfie = os.path.join(PHOTO_DIR, 'allison selfie.jpg')
    create_collage(9, 9, 256, photo_per_pie + bonus_photos, selfie)

if __name__ == '__main__':
    step1_total()
    step2_pies_to_make()
    step3_pies_to_photograph()
    step4_collage()
