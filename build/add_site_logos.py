"""Official logos from the brands' own websites → logos/ + logos/logos.json (trimmed PNGs, SVGs as they are)."""
import json, os, shutil
from PIL import Image
# brand → (file in sitelogos/, source page, tile: 'light' or 'dark' for logos the brand publishes in white)
SITE = {
 'Navien': ('navien.png', 'https://www.navieninc.com/', 'light'),
 'Bradford White': ('bw-14.png', 'https://www.bradfordwhite.com/', 'dark'),
 'Bryant': ('bryant.svg', 'https://www.bryant.com/en/us/', 'light'),
 'MrCool': ('mrcool.svg', 'https://www.mrcool.com/', 'light'),
 'Aprilaire': ('aprilaire.svg', 'https://www.aprilaire.com/', 'dark'),
 'York': ('york.png', 'https://www.york.com/', 'light'),
 'Ruud': ('ruud.png', 'https://www.ruud.com/', 'light'),
 'Payne': ('payne.png', 'https://www.payne.com/ (Carrier image server; Payne is now WeatherMaker)', 'light'),
 'Weil-McLain': ('weil-mclain.svg', 'https://www.weil-mclain.com/', 'dark'),
 'Pioneer': ('pioneer.png', 'https://www.pioneerminisplit.com/', 'light'),
 'Heil': ('heil.png', 'https://www.heil-hvac.com/', 'light'),
 'Lochinvar': ('lochinvar.svg', 'https://www.lochinvar.com/', 'dark'),
 'Coleman': ('coleman.png', 'https://www.colemanac.com/ (Bosch Home Comfort media server)', 'light'),
 'Takagi': ('takagi.png', 'https://www.takagi.com/', 'dark'),
 'Comfortmaker': ('comfortmaker.png', 'https://www.comfortmaker.com/', 'light'),
 'Burnham': ('burnham.png', 'https://www.burnhamholdings.com/ (maker of Burnham boilers)', 'light'),
 'State': ('state.svg', 'https://www.statewaterheaters.com/', 'light'),
 'Peerless': ('peerless.png', 'https://www.peerlessboilers.com/', 'light'),
 'Armstrong': ('armstrong.png', 'https://www.alliedair.com/ (Armstrong Air maker)', 'light'),
 'Utica': ('utica.svg', 'https://www.uticaboilers.com/', 'light'),
 'Tempstar': ('tempstar.png', 'https://www.tempstar.com/', 'light'),
 'Ducane': ('ducane.png', 'https://www.alliedair.com/ (Ducane HVAC maker)', 'light'),
 'EcoSmart': ('ecosmart.png', 'https://www.ecosmartus.com/', 'light'),
 'Luxaire': ('luxaire.png', 'https://www.luxaire.com/', 'dark'),
 'Slant/Fin': ('slant-fin.png', 'https://www.slantfin.com/', 'light'),
 'Triangle Tube': ('triangle-tube.svg', 'https://www.triangletube.com/', 'dark'),
}
j = json.load(open('logos/logos.json', encoding='utf-8'))
for brand, (f, src, tile) in SITE.items():
    slug = brand.lower().replace('/', '-').replace(' ', '-')
    ext = os.path.splitext(f)[1]
    dest = f'logos/{slug}{ext}'
    if ext == '.png':
        im = Image.open('sitelogos/' + f).convert('RGBA')
        box = im.getchannel('A').getbbox()          # trim transparent margins
        if box: im = im.crop(box)
        im.save(dest)
    else:
        shutil.copyfile('sitelogos/' + f, dest)
    j[brand] = {'file': dest, 'source': src, 'license': "brand's own logo, from its website", 'kind': 'logo', 'tile': tile}
for b in j.values():
    b.setdefault('tile', 'light')
json.dump(j, open('logos/logos.json', 'w', encoding='utf-8'), indent=1)
print(len(j), 'brands with logos;', sum(1 for b in j.values() if b['kind'] == 'logo'), 'logos;', [k for k, v in j.items() if v['tile'] == 'dark'])
