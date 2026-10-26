"""Build the static City & Suburban brand pages site (GitHub Pages) from the live service pages.

  python -I build_brand_site.py <src dir with hub.html + heating.html> <brands.json> <drafts.json> <out dir>

hub.html  = https://citysuburbanheating.com/services/          (cluster cards "Explore by system")
heating.html = https://citysuburbanheating.com/services/heating/ (service cards, search)
The live header, hero layout, trust band and footer are kept as they are; only the cards and the
page-specific copy change. Assets (CSS, fonts, images) are downloaded next to the pages.
"""
import html, json, os, re, shutil, subprocess, sys, urllib.parse

SRC, BRANDS, DRAFTS, OUT = sys.argv[1:5]
LIVE = 'https://citysuburbanheating.com'
os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)

def fetch(url, dest):
    if os.path.exists(dest):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    subprocess.run(['curl', '-sfL', '-o', dest, url], check=True)

def local_asset(path):
    """/services/... asset → assets/<file>, downloaded once; file:<path> = a local file, copied.
    Returns the path relative to the site root."""
    if path.startswith('file:'):
        src = path[5:]
        name = ('brand-' if 'logos' in src.replace('\\', '/').split('/') else '') + os.path.basename(src)
        dest = os.path.join(OUT, 'assets', name)
        if not os.path.exists(dest):
            shutil.copyfile(src, dest)
        return 'assets/' + name
    clean = path.split('?')[0]
    name = re.sub(r'[^A-Za-z0-9._-]', '_', clean.strip('/').replace('services/', '', 1))
    fetch(LIVE + clean if clean.startswith('/') else clean, os.path.join(OUT, 'assets', name))
    return 'assets/' + name

esc = lambda s: html.escape(s, quote=True)

def strip_and_localise(page, depth):
    """Live HTML → static: no Next scripts, local CSS/images, links back to the live site."""
    up = '../' * depth
    page = re.sub(r'<script\b.*?</script>', '', page, flags=re.S)
    page = re.sub(r'<link[^>]+rel="(?:preload|modulepreload|prefetch|preconnect|dns-prefetch)"[^>]*>', '', page)
    page = page.replace('<!-- -->', '')

    def css(m):
        href = m.group(1)
        name = 'assets/' + os.path.basename(href)
        dest = os.path.join(OUT, name)
        if not os.path.exists(dest):
            fetch(LIVE + href, dest)
            text = open(dest, encoding='utf-8').read()
            # fonts and images inside the CSS
            def u(mm):
                ref = mm.group(1).strip('\'"')
                if ref.startswith('data:') or ref.startswith('http'):
                    return mm.group(0)
                ref = urllib.parse.urljoin(href, ref)  # relative to the CSS file, e.g. ../media/font.woff2
                return 'url(' + local_asset(ref).replace('assets/', '', 1) + ')'
            open(dest, 'w', encoding='utf-8').write(re.sub(r'url\(([^)]+)\)', u, text))
        return f'<link rel="stylesheet" href="{up}{name}"/>'
    page = re.sub(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*/?>', css, page)

    # images and backgrounds served from /services/
    page = re.sub(r'(src|data-card-image|data-panel-image)="(/services/[^"]+\.(?:png|jpe?g|webp|svg|gif|avif))"',
                  lambda m: f'{m.group(1)}="{up}{local_asset(m.group(2))}"', page)
    page = re.sub(r'url\(&quot;(/services/[^&]+)&quot;\)', lambda m: f'url(&quot;{up}{local_asset(m.group(1))}&quot;)', page)
    page = re.sub(r'(<link[^>]+rel="(?:icon|apple-touch-icon)"[^>]+href=")(/[^"]+)"', lambda m: f'{m.group(1)}{up}{local_asset(m.group(2))}"', page)
    # every other site link goes to the live site
    page = re.sub(r'href="(/[^"]*)"', lambda m: f'href="{LIVE}{m.group(1)}"', page)
    return page

NAV_JS = """<script>
/* The live header's menu behaviour (site-navigation.tsx), without React */
(function(){
  var nav=document.getElementById('site-primary-navigation'), t=document.querySelector('.site-menu-toggle');
  if(t&&nav){t.addEventListener('click',function(e){e.stopPropagation();var o=!nav.classList.contains('is-open');nav.classList.toggle('is-open',o);t.setAttribute('aria-expanded',o);t.setAttribute('aria-label',o?'Close navigation menu':'Open navigation menu')});
    document.addEventListener('click',function(e){if(nav.classList.contains('is-open')&&!t.parentNode.contains(e.target)){nav.classList.remove('is-open');t.setAttribute('aria-expanded',false)}});
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('is-open')){nav.classList.remove('is-open');t.setAttribute('aria-expanded',false);t.focus()}})}
  document.querySelectorAll('.site-submenu-toggle').forEach(function(b){b.addEventListener('click',function(){var li=b.closest('li'),o=!li.classList.contains('is-expanded');li.classList.toggle('is-expanded',o);b.setAttribute('aria-expanded',o);var s=b.querySelector('span');if(s)s.textContent=o?'\\u2212':'+'})});
})();
</script>"""

SEARCH_JS = """<script>
/* Search, as on the live service collection pages */
(function(){
  var input=document.querySelector('.collection-toolbar input'), cards=[].slice.call(document.querySelectorAll('.collection-card')),
      shown=document.querySelector('.collection-result-count strong'), empty=document.querySelector('.collection-empty');
  if(!input)return;
  function run(){var q=input.value.trim().toLowerCase(),n=0;cards.forEach(function(c){var ok=!q||c.textContent.toLowerCase().indexOf(q)>-1;c.hidden=!ok;if(ok)n++});shown.textContent=n;if(empty)empty.hidden=n>0}
  input.addEventListener('input',run);
  var clear=empty&&empty.querySelector('button');if(clear)clear.addEventListener('click',function(){input.value='';run();input.focus()});
})();
</script>"""

BRAND_CSS = '''<style>
/* Brand images on the live card design: logos on white, a wordmark tile where no free logo exists */
.cluster-card-media.brand-media{background:#fff}
.cluster-card-media.brand-media:after{background:linear-gradient(#0000 72%,#09263a12)}
.cluster-card-media.brand-media img{object-fit:contain;padding:15% 14%}
.brand-wordmark{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;padding:0 10%;text-align:center;color:var(--collection-charcoal);font-family:var(--font-space-grotesk),sans-serif;font-weight:700;letter-spacing:-.04em;font-size:clamp(28px,3.2vw,42px);line-height:1}
.brand-wordmark:after{content:"";position:absolute;left:50%;bottom:22%;width:48px;height:3px;margin-left:-24px;background:var(--collection-lime)}
.brand-panel-logo{position:absolute;z-index:1;right:28px;top:24px;background:#fff;border-radius:10px;padding:10px 14px;box-shadow:0 10px 26px #0000002e;max-width:42%}
.brand-panel-logo img{display:block;max-width:100%;max-height:44px;margin:auto}
.collection-level-stat:has(.brand-panel-logo):before{display:none}
.collection-level-stat:has(.brand-panel-logo)>span{max-width:calc(58% - 28px)}
/* City & Suburban photos are portrait: keep the technician's head in the wide card */
.collection-card-media{background-position:center 22%!important}
/* the brand count has two digits (the live panel has one): keep "brands" clear of the house icon on narrower laptops */
@media (min-width:821px) and (max-width:1180px){.collection-hero-panel-count strong{font-size:50px}}
</style>'''

def finish(page, depth, extra_js=''):
    page = page.replace('</head>', BRAND_CSS + '</head>', 1)
    page = strip_and_localise(page, depth)
    return page.replace('</body>', NAV_JS + extra_js + '</body>')

def set_meta(page, title, description):
    page = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', page, flags=re.S)
    page = re.sub(r'(<meta name="description" content=")[^"]*', lambda m: m.group(1) + esc(description), page)
    page = re.sub(r'<meta property="og:[^>]+>|<meta name="twitter:[^>]+>|<link rel="canonical"[^>]+>', '', page)
    # a preview: keep it out of search results
    return page.replace('<head>', '<head><meta name="robots" content="noindex, nofollow"/>', 1)

brands = json.load(open(BRANDS, encoding='utf-8'))
drafts = json.load(open(DRAFTS, encoding='utf-8'))
for b in brands:
    b['brandImage'] = b['brandImage'] and local_asset(b['brandImage'])
    for p in b['pages']:
        p['image'] = p['image'] and local_asset(p['image'])

def plural_list(items):
    return items[0] if len(items) == 1 else ', '.join(items[:-1]) + (',' if len(items) > 2 else '') + ' and ' + items[-1]

# ── Brand hub: /services/ with one cluster card per brand ─────────────────────
hub = open(os.path.join(SRC, 'hub.html'), encoding='utf-8').read()
cards = []
for b in brands:
    n = len(b['pages'])
    equip = [e[0].upper() + e[1:] if i == 0 else e for i, e in enumerate(b['equipmentPlural'])]
    cards.append(
        f'<a aria-label="View all {esc(b["name"])} services" class="cluster-card" data-system="{b["slug"]}" href="{b["slug"]}/">' +
        (f'<span class="cluster-card-media brand-media"><img alt="{esc(b["name"])} logo" decoding="async" loading="lazy" src="{b["brandImage"]}"/>' if b['brandImageKind'] == 'logo' else
         f'<span class="cluster-card-media"><img alt="{esc(b["name"])}" decoding="async" loading="lazy" src="{b["brandImage"]}"/>' if b['brandImageKind'] == 'photo' else
         f'<span class="cluster-card-media brand-media"><span class="brand-wordmark" aria-hidden="true">{esc(b["name"])}</span>') +
        f'<span class="cluster-card-count">{n} {"service" if n == 1 else "services"}</span></span>'
        f'<span class="cluster-card-content"><strong class="cluster-card-title">{esc(b["name"])}</strong>'
        f'<span class="cluster-card-description-text">{esc(plural_list(equip))}.</span>'
        f'<span class="cluster-card-link">Explore services <span aria-hidden="true">→</span></span></span></a>')
total = sum(len(b['pages']) for b in brands)
hub = re.sub(r'(<div class="cluster-card-grid">).*?(</div></div></section>)', lambda m: m.group(1) + ''.join(cards) + m.group(2), hub, count=1, flags=re.S)
hub = hub.replace('<h1>Trusted HVAC experts for Chicago homes</h1>', '<h1>HVAC brands we repair and install in Chicago</h1>')
hub = hub.replace('<p>Explore dependable heating, cooling, indoor-air-quality, and commercial HVAC services for Chicago homes and buildings.</p>',
                  f'<p>Repair, installation and maintenance for {len(brands)} heating, cooling and water heater brands in Chicago homes and buildings.</p>')
hub = hub.replace('>Explore service categories<', '>Explore brands<')
hub = re.sub(r'aria-label="4 HVAC service categories"', f'aria-label="{len(brands)} HVAC brands"', hub)
hub = hub.replace('<span class="collection-hero-panel-kicker">Whole-home comfort</span>', '<span class="collection-hero-panel-kicker">Brands we service</span>')
hub = re.sub(r'(<div class="collection-hero-panel-count"><strong>)4(</strong><span>)service<br/>systems', rf'\g<1>{len(brands)}\g<2>brands', hub)
hub = hub.replace('<p class="cluster-directory-eyebrow">Find your system</p>', '<p class="cluster-directory-eyebrow">Find your brand</p>')
hub = hub.replace('>Explore by system</h2>', '>Explore by brand</h2>')
hub = hub.replace('<p>Choose a service category to see the help available for your home or business.</p>',
                  "<p>Choose your equipment's brand to see the repair and installation help available for it.</p>")
hub = set_meta(hub, 'HVAC Brands We Service in Chicago | City & Suburban',
               f'Repair, installation and maintenance for {len(brands)} heating, cooling and water heater brands in Chicago.')
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(finish(hub, 0))

# ── One page per brand: /services/heating/ with the brand's pages as service cards ──
tpl = open(os.path.join(SRC, 'heating.html'), encoding='utf-8').read()
for b in brands:
    page = tpl
    n = len(b['pages'])
    name = esc(b['name'])
    page = re.sub(r'<li><a href="/services/">Services</a></li><li aria-current="page">Heating</li>',
                  f'<li><a href="/services/">Services</a></li><li><a href="../">Brands</a></li><li aria-current="page">{name}</li>', page)
    page = page.replace('<h1>Heating<!-- --> services in Chicago</h1>', f'<h1>{name} services in Chicago</h1>')
    equip = plural_list(b['equipmentPlural'])
    page = page.replace('<p>Heating repair, installation, maintenance, heat pumps, boilers and system plans for Chicago homes.</p>',
                        f'<p>{name} {esc(equip)}: repair, installation and maintenance for Chicago homes.</p>')
    page = page.replace('>Browse services<', f'>Browse {name} services<')
    panel_bg = f',url(&quot;../{b["brandImage"]}&quot;)' if b['brandImageKind'] == 'photo' else ''
    panel_logo = (f'<div class="brand-panel-logo"><img alt="{name} logo" src="../{b["brandImage"]}"/></div>' if b['brandImageKind'] == 'logo' else '')
    page = re.sub(r'<div class="collection-level-stat collection-level-stat-image" data-panel-image="[^"]*" style="background-image:(linear-gradient\(.*?\)),url\(&quot;[^&]*&quot;\)"><span>Heating</span><strong>18</strong><h2>Services<!-- --> in this category</h2>',
                  lambda m: f'<div class="collection-level-stat collection-level-stat-image" style="background-image:{m.group(1)}{panel_bg}"><span>{name}</span><strong>{n}</strong><h2>{"Service" if n == 1 else "Services"} for this brand</h2>{panel_logo}', page, flags=re.S)
    page = page.replace('<p class="collection-kicker">Heating directory</p>', f'<p class="collection-kicker">{name} directory</p>')
    page = page.replace('<h2 id="service-directory-title">Choose a heating service</h2>', f'<h2 id="service-directory-title">Choose a {name} service</h2>')
    page = page.replace('<p>Pick the service that matches what the equipment is doing:',
                        f'<p>Pick the page for your {name} equipment, then the service that matches what it is doing:')
    page = re.sub(r'placeholder="Search by service or area"', 'placeholder="Search by equipment or service"', page)
    page = re.sub(r'Showing <strong>18</strong> of <!-- -->18<!-- --> services', f'Showing <strong>{n}</strong> of {n} {"service" if n == 1 else "services"}', page)
    cs = []
    for p in b['pages']:
        # No brand page is published yet: the card shows its status instead of a link (a link would 404).
        # Once a page is live, give the card href="https://citysuburbanheating.com/services/<brand>/<page slug>/".
        d = drafts.get(p['title'])
        note = ('Page written, publishing soon.' if d else 'Page coming soon.')
        note = f'<span class="collection-card-description" style="font-style:italic;opacity:.75">{note}</span>'
        future = f' data-live-path="/services/{b["slug"]}/{d}/"' if d else ''
        cs.append(
            (f'<a class="collection-card"{future} data-card-image="../{p["image"]}">'
             f'<span class="collection-card-media" style="background-image:linear-gradient(180deg, rgba(9,38,58,0) 45%, rgba(9,38,58,.14)), url(&quot;../{p["image"]}&quot;)" role="img" aria-label="{esc(p["title"])} in Chicago"></span>'
             if p['image'] else
             f'<a class="collection-card"{future}>'
             f'<span class="collection-card-media collection-card-media-empty" role="img" aria-label="{esc(p["title"])} in Chicago"><span aria-hidden="true">CS</span></span>') +
            f'<span class="collection-card-content"><strong>{esc(p["title"])}</strong>'
            f'<span class="collection-card-description">{esc(p["description"])}</span>{note}</span></a>')
    empty = ('<div class="collection-empty" hidden><h3>No matching services</h3><p>Try a broader service name or clear the search.</p>'
             '<button type="button">Clear filters</button></div>')
    page = re.sub(r'(<div class="collection-card-grid">).*?(</div></div></section>)', lambda m: empty + m.group(1) + ''.join(cs) + m.group(2), page, count=1, flags=re.S)
    page = re.sub(r'<details class="collection-photo-credits">.*?</details>', '', page, flags=re.S)
    page = set_meta(page, f'{b["name"]} HVAC Services in Chicago | City & Suburban',
                    f'{b["name"]} {equip}: repair, installation and maintenance in Chicago.')
    os.makedirs(os.path.join(OUT, b['slug']), exist_ok=True)
    open(os.path.join(OUT, b['slug'], 'index.html'), 'w', encoding='utf-8').write(finish(page, 1, SEARCH_JS))

print(len(brands), 'brands,', total, 'pages')
