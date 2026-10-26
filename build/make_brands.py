"""Brand Pages tab (CitySubUrban | Internal, gid 1336777568) → brands.json and drafts.json.

Rows are in sheet order (highest keyword volume first). The letters are the services the row's
secondary keywords cover, in their volume order: r repair, i installation, s service,
m maintenance, x replacement.
  python -I make_brands.py <out dir>
"""
import json, os, re, sys

ROWS = """Rheem Water Heater Repair & Installation|rismx
Carrier Air Conditioner Repair & Installation|rism
Nest Thermostat Repair & Installation|ir
Rheem Tankless Water Heater Repair & Installation|rmis
Navien Tankless Water Heater Repair & Installation|mris
Bradford White Water Heater Repair & Installation|rismx
Lennox Furnace Repair & Installation|rsmix
Trane Air Conditioner Repair & Installation|rsim
Trane Furnace Repair & Installation|irmsx
Rinnai Tankless Water Heater Repair & Installation|irsm
Carrier Furnace Repair & Installation|rxsim
Lennox Air Conditioner Repair & Installation|rmsix
Goodman Furnace Repair & Installation|irsmx
Rheem Air Conditioner Repair & Installation|rmis
Goodman Air Conditioner Repair & Installation|rism
Mitsubishi Mini Split Repair & Installation|imrs
Mitsubishi Air Conditioner Repair & Installation|rism
Rheem Furnace Repair & Installation|rsim
Bryant Furnace Repair & Installation|rims
MrCool Mini Split Repair & Installation|irm
Daikin Mini Split Repair & Installation|irms
Aprilaire Humidifier Repair & Installation|isr
AO Smith Water Heater Repair & Installation|irmsx
Goodman Heat Pump Repair & Installation|ris
Amana Furnace Repair & Installation|rsim
Amana Air Conditioner Repair & Installation|rsm
Bosch Tankless Water Heater Repair & Installation|rsmi
Daikin Air Conditioner Repair & Installation|rsim
LG Air Conditioner Repair & Installation|rism
Honeywell Thermostat Repair & Installation|ir
Trane Heat Pump Repair & Installation|rism
York Furnace Repair & Installation|rism
Mitsubishi Heat Pump Repair & Installation|ismr
Ruud Air Conditioner Repair & Installation|rm
Navien Boiler Repair & Installation|isrm
York Air Conditioner Repair & Installation|rsm
American Standard Air Conditioner Repair & Installation|ri
Bosch Heat Pump Repair & Installation|irsm
Carrier Heat Pump Repair & Installation|rmis
Fujitsu Mini Split Repair & Installation|rims
Noritz Tankless Water Heater Repair & Installation|rims
Bryant Heat Pump Repair & Installation|ir
Ecobee Thermostat Repair & Installation|ir
Bryant Air Conditioner Repair & Installation|ris
Rheem Heat Pump Repair & Installation|ris
Daikin Heat Pump Repair & Installation|irms
Payne Furnace Repair & Installation|rsm
Ruud Furnace Repair & Installation|rim
American Standard Furnace Repair & Installation|ris
Weil-McLain Boiler Repair & Installation|mrsi
Pioneer Mini Split Repair & Installation|irs
LG Mini Split Repair & Installation|ir
Heil Furnace Repair & Installation|rmi
Lochinvar Boiler Repair & Installation|rsm
Gree Mini Split Repair & Installation|rmi
Coleman Furnace Repair & Installation|rix
Takagi Tankless Water Heater Repair & Installation|rm
York Heat Pump Repair & Installation|ri
Lennox Heat Pump Repair & Installation|rsim
Coleman Air Conditioner Repair & Installation|r
Bosch Boiler Repair & Installation|rism
Viessmann Boiler Repair & Installation|rism
Comfortmaker Furnace Repair & Installation|r
Ruud Water Heater Repair & Installation|ri
Burnham Boiler Repair & Installation|rm
Buderus Boiler Repair & Installation|rsm
Fujitsu Heat Pump Repair & Installation|rism
Whirlpool Water Heater Repair & Installation|r
Bosch Water Heater Repair & Installation|rs
State Water Heater Repair & Installation|rs
Payne Air Conditioner Repair & Installation|r
Honeywell Humidifier Repair & Installation|ir
Samsung Mini Split Repair & Installation|ri
Peerless Boiler Repair & Installation|r
Heil Air Conditioner Repair & Installation|r
Armstrong Furnace Repair & Installation|r
Utica Boiler Repair & Installation|ri
Tempstar Furnace Repair & Installation|r
Ducane Furnace Repair & Installation|r
EcoSmart Tankless Water Heater Repair & Installation|ri
Carrier Mini Split Repair & Installation|im
Luxaire Furnace Repair & Installation|r
American Standard Heat Pump Repair & Installation|r
Slant/Fin Boiler Repair & Installation|x
Triangle Tube Boiler Repair & Installation|r
Daikin Furnace Repair & Installation|r
Armstrong Air Conditioner Repair & Installation|r
Amana Heat Pump Repair & Installation|r
Rinnai Boiler Repair & Installation|i
Lennox Mini Split Repair & Installation|r"""

# equipment: (name in the title, singular in text, plural in text, photo the live service cards use for it)
EQUIPMENT = [
    ('Tankless Water Heater', 'tankless water heater', 'tankless water heaters', '/services/images/services/city-suburban/furnace-water-heater-room.jpg'),
    ('Water Heater', 'water heater', 'water heaters', 'https://cdn.sanity.io/images/boolyxr0/production/cc8f3c279a0b0f5cae58c0088f52dadb86e017a9-709x900.jpg'),
    ('Air Conditioner', 'air conditioner', 'air conditioners', '/services/reference-assets/as-ac.png'),
    ('Mini Split', 'mini-split', 'mini-splits', '/services/reference-assets/svc-ductless.jpg'),
    ('Heat Pump', 'heat pump', 'heat pumps', '/services/reference-assets/as-heat-pump.png'),
    ('Furnace', 'furnace', 'furnaces', '/services/reference-assets/svc-heating-repair.jpg'),
    ('Boiler', 'boiler', 'boilers', '/services/reference-assets/job-boiler-1.jpg'),
    ('Thermostat', 'thermostat', 'thermostats', 'https://cdn.sanity.io/images/boolyxr0/production/801b31702589e333ca1833732c9ffd327d7ee3a8-1920x1954.jpg'),
    ('Humidifier', 'humidifier', 'humidifiers', '/services/reference-assets/as-steam-humidifier.jpg'),
]
# Photos only where the photo shows that brand: most of the live site's equipment photos are
# American Standard units with the logo visible, which would be wrong on any other brand's card.
# Every other card uses the design's own no-photo version (the "CS" mark).
BRAND_PHOTOS = {
    ('American Standard', 'Furnace'): '/services/reference-assets/svc-heating-installation.jpg',
    ('American Standard', 'Air Conditioner'): '/services/reference-assets/as-ac.png',
    ('American Standard', 'Heat Pump'): '/services/reference-assets/as-heat-pump.png',
    ('Nest', 'Thermostat'): 'https://cdn.sanity.io/images/boolyxr0/production/801b31702589e333ca1833732c9ffd327d7ee3a8-1920x1954.jpg',
}
# City & Suburban's own technician photos (photo side of the site's blog banners, no brand on the unit)
CS_PHOTO = {'Tankless Water Heater': 'water-heater', 'Water Heater': 'water-heater', 'Air Conditioner': 'air-conditioner',
            'Mini Split': 'mini-split', 'Heat Pump': 'heat-pump', 'Furnace': 'furnace', 'Boiler': 'boiler',
            'Thermostat': 'hvac', 'Humidifier': 'hvac'}
SERVICES = {'r': 'repair', 'i': 'installation', 's': 'service', 'm': 'maintenance', 'x': 'replacement'}

# Brand page drafts in Sanity (boolyxr0, type brandPage), none published yet: title → page slug
DRAFTS = {
    'American Standard Furnace Repair & Installation': 'american-standard-furnace-repair-chicago',
    'Bradford White Water Heater Repair & Installation': 'bradford-white-water-heater-repair-chicago',
    'Carrier Air Conditioner Repair & Installation': 'carrier-air-conditioner-repair-chicago',
    'Lennox Furnace Repair & Installation': 'lennox-furnace-repair-chicago',
    'Navien Tankless Water Heater Repair & Installation': 'navien-tankless-water-heater-repair-chicago',
    'Nest Thermostat Repair & Installation': 'nest-thermostat-installation-chicago',
    'Rheem Tankless Water Heater Repair & Installation': 'rheem-tankless-water-heater-repair-chicago',
    'Rheem Water Heater Repair & Installation': 'rheem-water-heater-repair-chicago',
    'Trane Air Conditioner Repair & Installation': 'trane-air-conditioner-repair-chicago',
    'Trane Furnace Repair & Installation': 'trane-furnace-installation-chicago',
}

def join(items):
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + ' and ' + items[-1]

brands = {}
for line in ROWS.splitlines():
    title, codes = line.split('|')
    head = title.replace(' Repair & Installation', '')
    eq = next(e for e in EQUIPMENT if head.endswith(' ' + e[0]))
    brand = head[: -len(eq[0]) - 1]
    slug = re.sub(r'[^a-z0-9]+', '-', brand.lower()).strip('-')
    b = brands.setdefault(brand, {'name': brand, 'slug': slug, 'pages': [], 'equipmentPlural': []})
    if eq[2] not in b['equipmentPlural']:
        b['equipmentPlural'].append(eq[2])
    b['pages'].append({
        'title': title,
        'equipment': eq[1],
        'image': BRAND_PHOTOS.get((brand, eq[0])) or 'file:crops/cs-' + CS_PHOTO[eq[0]] + '.jpg',
        'description': f"{brand} {eq[1]} {join([SERVICES[c] for c in codes])} in Chicago.",
    })
# Brand images: logos.json (public-domain / CC0 logos from Wikimedia Commons, American Standard from the
# City & Suburban site, a CC0 photo of a Bryant sign). Brands without one get a wordmark tile.
logos = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logos', 'logos.json'), encoding='utf-8')) if len(sys.argv) < 3 else json.load(open(sys.argv[2], encoding='utf-8'))
for b in brands.values():
    lg = logos.get(b['name'])
    b['brandImage'] = ('file:' + lg['file']) if lg else None
    b['brandImageKind'] = lg['kind'] if lg else None
    b['brandTile'] = (lg or {}).get('tile', 'light')  # 'dark' for logos the brand publishes in white

out = sys.argv[1]
json.dump(list(brands.values()), open(os.path.join(out, 'brands.json'), 'w', encoding='utf-8'), indent=1)
json.dump(DRAFTS, open(os.path.join(out, 'drafts.json'), 'w', encoding='utf-8'), indent=1)
print(len(brands), 'brands,', sum(len(b['pages']) for b in brands.values()), 'pages; drafts matched:',
      sum(1 for b in brands.values() for p in b['pages'] if p['title'] in DRAFTS))
