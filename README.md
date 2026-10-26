# City & Suburban brand pages: collection cards (preview)

Static preview on GitHub Pages: https://logeshmaximus.github.io/city-suburban-brand-pages/

- `index.html`: the brand hub, a copy of the live https://citysuburbanheating.com/services/ page (header, hero, trust band, footer) with one cluster card per brand, in the live "Explore by system" card design.
- `<brand>/index.html`: one page per brand, a copy of the live https://citysuburbanheating.com/services/heating/ page with that brand's pages as service cards, and the same search.

Brands and pages come from the "Brand Pages" tab of the CitySubUrban | Internal sheet: the brand is the start of each page title, before the equipment. 49 brands, 90 pages.

No brand page is published yet, so brand page cards show their status ("Page written, publishing soon." for the 10 Sanity drafts, otherwise "Page coming soon.") instead of a link. Pages carry noindex (preview only).

## Images

- **Brand cards and the brand page panel: the brand's own image.** 22 logos from Wikimedia Commons, all public domain (no credit needed); the American Standard logo from the City & Suburban site; a CC0 photo of a real Bryant Heating & Cooling sign. Sources and licenses: `build/brand-images.json`. Brands with no free logo (25) show their name as a wordmark tile in the site font.
- **Service cards on a brand page: City & Suburban's own photos.** The photo side of the site's own blog images (technician at an AC unit, furnace, heat pump, mini-split, boiler, water heater; unbranded units), cropped by `build/crop.py`. American Standard and Nest pages keep their own brand photos from the live site.
- **The hero panel** shows only the number of brands.

## Rebuild

    python -I build/make_brands.py build
    python -I build/build_brand_site.py build build/brands.json build/drafts.json <out dir>
