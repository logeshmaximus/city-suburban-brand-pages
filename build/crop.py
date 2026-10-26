from PIL import Image
import sys
# equipment → (source banner from the City & Suburban WordPress library, left edge of the photo side)
SRC = {
 'air-conditioner': ('wpimg/8fde2777-6396-400d-9dcd-49cff4.png', .60),
 'furnace': ('wpimg/cbbb2c7e-1bd1-4a6d-b680-be3ebf.png', .64),
 'heat-pump': ('wpimg/740606f6-4aff-466a-9d89-c22dcb.png', .58),
 'mini-split': ('wpimg/81829c3e-ee77-4aeb-80ed-9c51bf.png', .68),
 'boiler': ('wpimg/f2e89cc7-2f5f-43d0-bde3-2c58fa.png', .67),
 'water-heater': ('wpimg/generated-image-6.png.png', .67),
 'hvac': ('wpimg/a155b3d2-1e78-4eb2-81d5-1c3c9c.png', .65),
}
for name, (f, x) in SRC.items():
    im = Image.open(f).convert('RGB'); w, h = im.size
    c = im.crop((int(w * x), 0, w, h))
    c.thumbnail((900, 900)); c.save(f'crops/cs-{name}.jpg', quality=82)
    print(name, im.size, '->', c.size)
