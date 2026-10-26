# City & Suburban brand pages: collection cards (preview)

Static preview on GitHub Pages: https://logeshmaximus.github.io/city-suburban-brand-pages/

- `index.html`: the brand hub, a copy of the live https://citysuburbanheating.com/services/ page (header, hero, trust band, footer) with one cluster card per brand, in the live "Explore by system" card design.
- `<brand>/index.html`: one page per brand, a copy of the live https://citysuburbanheating.com/services/heating/ page with that brand's pages as service cards, and the same search.

Brands and pages come from the "Brand Pages" tab of the CitySubUrban | Internal sheet: the brand is the start of each page title, before the equipment. 49 brands, 90 pages.

No brand page is published yet, so brand page cards show their status ("Page written, publishing soon." for the 10 Sanity drafts, otherwise "Page coming soon.") instead of a link. Photos only where they show the right brand (American Standard, Nest); other cards use the design's no-photo version. Pages carry noindex (preview only).

## Rebuild

    python -I build/make_brands.py build
    python -I build/build_brand_site.py build build/brands.json build/drafts.json <out dir>
