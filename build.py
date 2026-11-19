from html import escape
from pathlib import Path
from urllib.parse import quote, urlsplit
import json, re, shutil, argparse

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--live', action='store_true', help='Statische Live-Fassung mit direkten Kontaktwegen')
parser.add_argument('--site-url', default='https://www.ecosteps-solar.de', help='Öffentliche HTTPS-Basis für den Live-Build')
args = parser.parse_args()
site_url = args.site_url.rstrip('/')
origin = urlsplit(site_url)
if not re.fullmatch(r'https://[a-zA-Z0-9.-]+(?::[0-9]+)?', site_url) or not origin.hostname:
    parser.error('--site-url muss eine HTTPS-Domain ohne Pfad sein')

def canonical_url(path):
    return site_url + '/' + (quote(path, safe='/')+'/' if path else '')

OUT = ROOT / 'dist' / ('live' if args.live else 'offline')
OUT.mkdir(parents=True, exist_ok=True)
source = json.loads((ROOT / 'content/sources.json').read_text())
pages = {key: item for key, item in source['pages'].items() if 'html' in item}
version = (ROOT / 'VERSION').read_text().strip()
phone = '02256 620 98 41'
mail = 'info@ecosteps-solar.de'
cta = 'Energieberatung anfragen'
articles = {}
if (ROOT / 'content/articles.json').exists():
    articles = json.loads((ROOT / 'content/articles.json').read_text())

def link(path, label, cls=''):
    return f'<a class="{cls}" href="@/{path}">{label}</a>'

def image(name, alt, eager=False):
    loading = '' if eager else ' loading="lazy"'
    return f'<img{loading} src="@/assets/{name}" alt="{escape(alt)}">'

def card(path, heading, desc, photo=None):
    illustration = image(*photo) if photo else ''
    return f'<article class="card">{illustration}<div><h3>{link(path, heading)}</h3><p>{desc}</p>{link(path, "Mehr erfahren <span aria-hidden=true>→</span>", "text-link")}</div></article>'

def intro(title, copy, eyebrow='EcoSteps'):
    return f'<section class="page-intro"><div class="wrap"><p class="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{copy}</p></div></section>'

def localize_legacy(html):
    def replace(match):
        key = match[1]
        return '@/'+(key+'/index.html' if key else 'index.html') if key in pages else 'https://www.ecosteps-solar.de/'+key
    html = re.sub(r'@@page/([^"\s]*)', replace, html).replace('@@asset/', '@/assets/')
    html = re.sub(r'<img(?![^>]*\balt=)', '<img alt=""', html)
    return html

def legacy(path):
    html = localize_legacy(pages[path]['html'])
    inquiry = source_inquiry(path)
    if inquiry:
        html = re.sub(r'<div class="wpcf7"[^>]*>\s*<div class="screen-reader-response"></div>\s*</div>', lambda _: inquiry, html, count=1)
    videos = original_videos(path)
    if path == 'photovoltaik/eigenverbrauch':
        html = re.sub(r'(<div class="fl-rich-text">.*?)(<p>\s*</p>)', lambda match: match[1]+videos, html, count=1, flags=re.S)
    if path == 'speicher/eigenverbrauch':
        html = re.sub(r'<div class="fl-video fl-embed-video"[^>]*>\s*</div>', lambda _: videos, html, count=1)
    return f'<div class="archive">{html}</div>'

def original_media(path):
    return ''.join(image(name, '') for name in pages[path].get('banners', []))

def original_videos(path):
    return ''.join(
        f'<p class="notice"><a href="{escape(url, quote=True)}">{escape(title)}</a> (YouTube, Internetverbindung erforderlich).</p>'
        for title, url in pages[path].get('videos', [])
    )

def source_inquiry(path):
    kind = pages[path].get('inquiry')
    if not kind:
        return ''
    if args.live:
        return f'<p>{link("beratung/index.html",cta,"button primary")}</p>'
    fields = [('Ihr Name*','text',True), ('Ihre PLZ*','text',True), ('Ihr Ort*','text',True)]
    if kind == 'contact':
        fields += [('Ihre E-Mail-Adresse*','email',True), ('Betreff','text',False), ('Ihre Nachricht','textarea',False)]
    else:
        fields += [('E-Mail*','email',True), ('Telefonnummer','tel',False)]
    controls = []
    for label, field_type, required in fields:
        constraint = ' required' if required else ''
        field = '<textarea rows="4"></textarea>' if field_type == 'textarea' else f'<input type="{field_type}"{constraint}>'
        controls.append(f'<label>{label}{field}</label>')
    return f"""
<section class="form-card legacy-inquiry">
  <h2>{'Schreiben Sie uns eine Nachricht!' if kind == 'contact' else 'Kontakt aufnehmen'}</h2>
  <p>Offline-Demo. Ihre Angaben werden nicht übertragen.</p>
  <form data-legacy-inquiry>
    <div class="fields">{''.join(controls)}</div>
    <p><a href="@/datenschutz/index.html">Datenschutzerklärung</a></p>
    <button class="button primary" type="submit" disabled>Senden</button>
    <p role="status"></p>
  </form>
</section>"""


def contact():
    return f'<a href="tel:+4922566209841">{phone}</a><br><a href="mailto:{mail}">{mail}</a>'

def primary_nav(current):
    groups = []
    for item in nav_items:
        label = escape(item['title'])
        if item['children']:
            children = []
            for child in item['children']:
                slug = child['path']
                active = ' aria-current="page"' if slug == current else ''
                children.append(f'<li><a href="@/{slug}/index.html"{active}>{escape(child["title"])}</a></li>')
            category = item['children'][0]['path'].split('/')[0]
            if category == 'beratung':
                children.append(f'<li>{link("beratung/index.html",cta,"nav-inquiry")}</li>')
            current_category = ' active' if current.split('/')[0] == category else ''
            groups.append(f'<li><details class="nav-group{current_category}"><summary>{label}</summary><ul>{"".join(children)}</ul></details></li>')
        else:
            active = ' aria-current="page"' if item['path'] == current else ''
            groups.append(f'<li><a href="@/{item["path"]}/index.html"{active}>{label}</a></li>')
    return '<ul class="nav-list">'+''.join(groups)+'</ul>'


def icon(name):
    return f'<span class="line-icon icon-{name}" aria-hidden="true"></span>'

def key_points(path):
    labels = highlights.get(path)
    if not labels:
        return ''
    category = path.split('/')[0]
    topic_icons = {'photovoltaik':'sun', 'speicher':'battery', 'heizung':'bolt',
                   'gewerbekunden':'grid', 'beratung':'target', 'service':'target'}
    first_icon = topic_icons[category]
    icons = (first_icon, 'clock' if first_icon == 'grid' else 'grid', 'target')
    if path == 'gewerbekunden/eigenverbrauch':
        third = '<strong class="metric">60,7 %</strong><span>Solarer Deckungsanteil im historischen Werkstattbeispiel</span><meter min="0" max="100" value="60.7" aria-label="Solarer Deckungsanteil in Prozent">60,7 %</meter>'
    else:
        third = f'{icon(icons[2])}<strong>{escape(labels[2])}</strong>'
    return f"""
<section class="wrap key-points" aria-label="Wichtige Themen">
  <ul>
    <li>{icon(icons[0])}<strong>{escape(labels[0])}</strong></li>
    <li>{icon(icons[1])}<strong>{escape(labels[1])}</strong></li>
    <li>{third}</li>
  </ul>
</section>"""

def seo_head(path, description):
    meta = f'<meta name="description" content="{escape(description, quote=True)}">'
    if not args.live or path == 'bestand/startseite':
        return meta + '<meta name="robots" content="noindex,follow">'
    url = canonical_url(path)
    meta += f'<link rel="canonical" href="{url}"><meta property="og:url" content="{url}">'
    if not path:
        business = {
            '@context':'https://schema.org',
            '@type':'Organization',
            'name':'ecosteps GmbH & Co. KG',
            'url':url,
            'logo':url+'assets/ecosteps_logo.jpg',
            'telephone':'+49 2256 6209841',
            'email':mail,
            'address':{'@type':'PostalAddress','streetAddress':'Virnicher Str. 8',
                       'postalCode':'53894','addressLocality':'Mechernich','addressCountry':'DE'}
        }
        meta += f'<script type="application/ld+json">{json.dumps(business, ensure_ascii=False)}</script>'
    return meta


def layout(path, title, body, description=None):
    file = OUT / (path+'/index.html' if path else 'index.html')
    depth = len(Path(path).parts)
    prefix = '../' * depth or './'
    nav = [('leistungen/index.html','Leistungen'),('energieratgeber/index.html','Energieratgeber'),('kontakt/index.html','Kontakt')]
    links = ''.join(link(url,label) for url,label in nav if url.split('/')[0] in paths)
    active = path.split('/')[0]
    links = links.replace(f'href="@/{active}/index.html"', f'href="@/{active}/index.html" aria-current="page"') if active in ('leistungen','energieratgeber','kontakt') else links
    legal = ''.join(link(k+'/index.html',label) for k,label in [('impressum','Impressum'),('datenschutz','Datenschutz'),('agb','AGB')] if k in paths)
    consultation = 'beratung/index.html' if 'beratung' in paths else 'kontakt/index.html'
    cookies = '<button type="button" data-cookie-settings>Cookie-Einstellungen</button>' if 'datenschutz' in paths else ''
    floating = link(consultation,cta+' <span aria-hidden="true">→</span>','fixed-cta') if articles else ''
    cookie_file = 'cookies-live.html' if args.live else 'cookies.html'
    banner = (ROOT / 'content' / cookie_file).read_text() if cookies else ''
    footer_links = links + link('referenzen/index.html','Referenzen')
    description = description or seo_descriptions[path]
    metadata = seo_head(path, description)
    doc = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · EcoSteps</title>{metadata}<link rel="icon" href="@/assets/ecosteps_logo.jpg" type="image/jpeg"><link rel="stylesheet" href="@/assets/site.css"><script src="@/assets/site.js" defer></script></head>
<body class="{'home' if not path else 'interior'}" data-mode="{'live' if args.live else 'offline'}">
<div class="site-frame"><a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="header"><div class="wrap header-inner">
{link('index.html',image('ecosteps_logo.jpg','EcoSteps – Startseite',True),'logo')}
<button class="menu" type="button" aria-expanded="false" aria-controls="navigation">Menü</button>
<nav id="navigation" aria-label="Hauptnavigation">{primary_nav(path)}</nav><div class="header-contact">{link("kontakt/index.html","Kontakt")}<a class="header-phone" href="tel:+4922566209841">{phone}</a></div>
</div></header>
<main id="inhalt" tabindex="-1">{body}</main>
<footer class="footer"><div class="wrap footer-grid"><div>{link('index.html',image('ecosteps_logo.jpg','EcoSteps – Startseite'),'logo')}<p>ecosteps GmbH &amp; Co. KG<br>Virnicher Str. 8<br>53894 Mechernich</p>{contact()}</div><div><h2>EcoSteps</h2>{footer_links}</div><div><h2>Rechtliches</h2>{legal}{cookies}</div></div></footer>
{floating}{banner}</div>
</body></html>'''
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(doc.replace('@/',prefix),encoding='utf-8')

def homepage():
    original = pages['']
    slides = ''.join(
        f'<figure class="hero-media"{" hidden" if index else ""}>{image(name, "", index == 0)}</figure>'
        for index, name in enumerate(original['banners'])
    )
    hero = f"""
<section class="hero" aria-labelledby="home-title" data-hero-slides>
  {slides}
  <div class="wrap hero-grid"><div class="hero-copy">
    <h1 id="home-title">Photovoltaik für<br>Haus und Gewerbe.</h1>
    {link('beratung/index.html',cta+' <span aria-hidden="true">→</span>','button primary')}
  </div></div>
  <div class="wrap slide-control"><button type="button" data-slide-next aria-label="Nächstes Startseitenbild"><span aria-hidden="true">→</span></button></div>
</section>"""
    teasers = [localize_legacy(teaser) for teaser in original['teasers']]
    rows = [(0, 1, 'featured'), (1, 2, 'featured'), (2, 4, 'pair'),
            (4, 6, 'pair'), (6, 7, 'featured'), (7, 9, 'pair')]
    original_rows = ''.join(
        f'<div class="home-original-row {style}">{"".join(teasers[start:end])}</div>'
        for start, end, style in rows
    )
    features = f"""
<section class="section wrap discovery" aria-labelledby="start-themes">
  <h2 id="start-themes">Solarstrom im Überblick</h2>
  <div class="discovery-grid">
    <article class="discovery-tile discovery-solar">
      {icon('sun')}<h3>Photovoltaik</h3><p>Solarstrom selbst erzeugen und im Gebäude nutzen.</p>
      {link('photovoltaik/eigenverbrauch/index.html','Eigenverbrauch verstehen →','text-link')}
    </article>
    <article class="discovery-tile discovery-storage">
      {image('ecosteps_slider_speicher-eigenverbrauch1.jpg','')}
      {icon('battery')}<h3>Stromspeicher</h3><p>Überschüsse für später speichern.</p>
      {link('speicher/eigenverbrauch/index.html','Speicher kennenlernen →','text-link')}
    </article>
    <article class="discovery-tile discovery-business">
      <strong class="metric">60,7 %</strong><h3>Solarer Deckungsanteil</h3>
      <p>In der historischen Jahresrechnung für eine Kfz-Werkstatt.</p>
      {link('gewerbekunden/eigenverbrauch/index.html','Werkstattbeispiel ansehen →','text-link')}
    </article>
  </div>
</section>"""
    return hero + features + f"""
<section class="section wrap home-original" id="ecosteps-bestand" aria-label="EcoSteps Angebote">
  <div class="home-original-grid">{original_rows}</div>
  <p class="notice">Preis-, Förder- und Leistungsangaben in den Originalbeiträgen können zeitgebunden sein.</p>
</section>
<section class="highlight"><div class="wrap guide-grid"><div>
  <h2>Welches Angebot passt zu Ihnen?</h2>
  <p>Informieren Sie sich über Eigenverbrauch und Anlagenplanung oder sprechen Sie direkt mit uns.</p>
  {link('energieratgeber/index.html','Energieratgeber →','text-link')}
</div>{link('beratung/index.html',cta,'button primary')}</div></section>"""


highlights = json.loads((ROOT / 'content/highlights.json').read_text())
seo_descriptions = {
    '': 'EcoSteps in Mechernich plant Photovoltaik, Stromspeicher und Solarwärme für Privathaushalte und Gewerbe. Jetzt Energieberatung anfragen.',
    'leistungen': 'EcoSteps-Leistungen im Überblick: Photovoltaik, Stromspeicher, Wärme mit Solarstrom, Energieberatung und Anlagenservice.',
    'referenzen': 'Beispiele für Photovoltaikanlagen von EcoSteps, darunter eine Kfz-Werkstatt mit dokumentiertem Lastprofil und solarem Deckungsanteil.',
    'kontakt': 'EcoSteps in Mechernich erreichen: Telefonnummer, E-Mail-Adresse und Anschrift für Fragen zu Photovoltaik und Energieberatung.',
    'beratung': 'Energieberatung bei EcoSteps in Mechernich anfragen und Photovoltaik, Stromspeicher und Eigenverbrauch für Ihr Gebäude planen.',
    'service': 'EcoSteps-Anlagenservice für Photovoltaik: Erträge überwachen, Leistungseinbußen erkennen und bestehende PV-Anlagen betreuen.',
    'energieratgeber': 'Energieratgeber von EcoSteps: Solarstrom nutzen, PV-Anlagen modernisieren und Eigenverbrauch für Haushalt oder Betrieb berechnen.',
    'bestand/startseite': 'Archiv der bisherigen EcoSteps-Startseite mit Meldungen, Angeboten und Hinweisen zur Photovoltaik.',
    'impressum': 'Impressum der ecosteps GmbH & Co. KG mit Sitz, Kontakt und Unternehmensangaben.',
    'datenschutz': 'Datenschutzerklärung der ecosteps GmbH & Co. KG mit Angaben zu Kontakt, Formularen und Cookie-Einstellungen.',
    'agb': 'Entwurf der Allgemeinen Geschäftsbedingungen der ecosteps GmbH & Co. KG.'
}
nav_items = json.loads((ROOT / "content/navigation.json").read_text())
topics = json.loads((ROOT / 'content/topics.json').read_text())
paths = set(pages) | {'leistungen','bestand/startseite','referenzen'}
if articles:
    paths |= {'energieratgeber',*articles}
if (ROOT / 'content/cookies.html').exists():
    paths |= {'datenschutz','agb'}
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
layout('', 'Solarstrom für Privathaushalte und Unternehmen', homepage())
layout('bestand/startseite','Inhalte der bisherigen Startseite',intro('Bisherige Startseite','Die folgenden Meldungen und Angebote stammen von der Bestandswebsite. Preis- und Leistungsangaben können zeitgebunden sein.','Bestandsinhalte')+f'<section class="section wrap prose">{legacy("")}</section>')
def topic_links(category, current=None):
    entries = topics[category]['pages']
    items = []
    for slug, (title, description) in entries.items():
        key = f'{category}/{slug}'
        if key not in pages or key == current:
            continue
        items.append(f'<li>{link(key+"/index.html", f"<strong>{title}</strong><span>{description}</span><span class=service-arrow aria-hidden=true>→</span>")}</li>')
    return '<ul class="service-list">'+''.join(items)+'</ul>'

overview = []
for category, topic in topics.items():
    overview.append(f"""
<section class="topic-area" id="{category}">
  <div>{image(*topic['photo'])}<h2>{topic['title']}</h2><p>{topic['intro']}</p></div>
  {topic_links(category)}
</section>""")
overview_nav = ''.join(f'<a href="#{key}">{item["title"]}</a>' for key,item in topics.items())
overview_nav += '<a href="#anlagenservice">Anlagenservice</a>'
layout('referenzen','Referenzen',intro('Referenzen','Beispiele aus der bisherigen EcoSteps-Website.')+'<section class="section wrap cards two">'+card('gewerbekunden/eigenverbrauch/index.html','Kfz-Werkstatt','Historisches Anlagenbeispiel mit Leistungsprofil und Jahreswerten.',('werkstatt.jpg','Arbeit in einer Kfz-Werkstatt, Motiv der Bestandsseite'))+card('photovoltaik/eigenverbrauch/index.html#4','Kundenanlagen','Historische Beispiele für Eigenverbrauch in Privathaushalten.')+'</section>')
layout('leistungen','Leistungen',intro('Unsere Leistungen','Photovoltaik, Speicher, Wärme und Anlagenservice.')+f"""
<div class="wrap topic-overview">
  <nav class="topic-index" aria-label="Leistungsbereiche">{overview_nav}</nav>
  {''.join(overview)}
  <section class="topic-area topic-service" id="anlagenservice">
    <div><h2>Anlagenservice</h2><p>Erträge überwachen und schleichende Leistungseinbußen früh erkennen.</p></div>
    {link('service/index.html','Zum Anlagenservice →','text-link')}
  </section>
</div>""")
for key,p in pages.items():
    if not key: continue
    title = escape(p['title'])
    description = seo_descriptions.get(key)
    body = intro(title,'','Bestandsinhalte')+f'<section class="section wrap prose">{legacy(key)}</section>'
    category, _, slug = key.partition('/')
    if category in topics and slug in topics[category]['pages']:
        topic = topics[category]
        label, description = topic['pages'][slug]
        overview_link = link(f'leistungen/index.html#{category}',topic['title'],'text-link')
        body = intro(label,description,overview_link)+f'''
<section class="section wrap detail-grid">
  <article class="prose">
    <p class="notice">Bestandsinhalt. Angaben zu Preisen, Produkten, Vergütung und Förderung können zeitgebunden sein.</p>
    {legacy(key)}
    <p class="source-note">Quelle: <a href="{escape(p['url'], quote=True)}">EcoSteps-Bestandswebsite</a></p>
  </article>
  <aside class="detail-related" aria-label="Verwandte Seiten">
    <h2>Weitere Themen</h2>{topic_links(category,key)}
    <p>{link('beratung/index.html',cta,'button primary')}</p>
  </aside>
</section>'''
        p_title = f"{label} | {topic['title']}" if label != topic['title'] else label
    else:
        p_title = p['title']
    if key == 'speicher/technik':
        body = re.sub(r'<h2>([^<]*[Ff]lexibl[^<]*)</h2>', r'<h2 id="5">\1</h2>', body, count=1)
    if key == 'gewerbekunden/eigenverbrauch':
        body = body.replace('<div class="archive">','<p class="notice">Die historische Beispielrechnung enthält abweichende Werte: 12.772 kWh Netzbezug zu 0,22 €/kWh ergeben etwa 2.810 € im Jahr. In der Originaltabelle stehen 825 €.</p><div class="archive">',1)
    if key == 'kontakt':
        body = intro('Kontakt','Schreiben Sie uns eine Nachricht oder rufen Sie uns an.')+f'''
<section class="section wrap consult">
  <div class="prose"><h2>Telefon und E-Mail</h2><p>{contact()}</p>{link('beratung/index.html',cta,'button primary')}</div>
  <div class="form-card"><h2>Anschrift</h2><address>ecosteps GmbH &amp; Co. KG<br>Virnicher Str. 8<br>53894 Mechernich</address></div>
</section>'''
    if key == 'beratung' and (ROOT/'content/consultation.html').exists():
        form = '' if args.live else (ROOT/'content/consultation.html').read_text().replace('@/datenschutz/index.html', '@/impressum/index.html' if 'datenschutz' not in paths else '@/datenschutz/index.html')
        body = intro('Energieberatung anfragen','Wir klären, welche Lösung zu Ihrem Stromverbrauch, Ihrer Fläche und Ihren Zielen passt.')+f'''<section class="section wrap consult"><div class="prose"><h2>So bereiten Sie sich vor</h2><ul><li>Jahresstromverbrauch oder letzte Stromabrechnung</li><li>Angaben zu einer vorhandenen PV-Anlage und zum Speicher</li><li>Bei Unternehmen die typischen Betriebs- und Verbrauchszeiten</li></ul><h2>Direkter Kontakt</h2>{contact()}</div>{form}</section>'''
    if key == 'impressum' and (ROOT/'content/legal.html').exists():
        body = intro('Impressum','')+(ROOT/'content/legal.html').read_text()+f'<section class="section wrap prose"><details><summary>Impressum und Datenschutzhinweise der Bestandswebsite</summary>{legacy(key)}</details></section>'
    media = original_media(key)
    if media:
        body = body.replace('</section>', f'<div class="wrap source-banner">{media}</div></section>', 1)
    if key in highlights:
        intro_end = body.index('</section>') + len('</section>')
        body = body[:intro_end] + key_points(key) + body[intro_end:]
    if key == 'kontakt':
        body += f'<div class="wrap prose source-extras">{source_inquiry(key)}</div>'
    layout(key,p_title if key!='beratung' else 'Energieberatung in Mechernich',body,description)
if articles:
    layout('energieratgeber','Energieratgeber',intro('Energieratgeber','Antworten rund um Solarstrom, Eigenverbrauch und die Planung Ihrer Anlage.')+'<section class="section wrap cards">'+''.join(card(key+'/index.html',a['title'],a['intro']) for key,a in articles.items())+'</section>')
    for key,a in articles.items():
        layout(key,a['title'],intro(a['title'],a['intro'],'Energieratgeber')+f'<section class="section wrap prose">{a["html"]}<p>{link("beratung/index.html",cta,"button primary")}</p></section>',a["intro"])
if 'datenschutz' in paths:
    for key,title in [('datenschutz','Datenschutzerklärung'),('agb','Allgemeine Geschäftsbedingungen')]:
        layout(key,title,intro(title,'Entwurf zur Freigabe','Rechtliches')+(ROOT/f'content/{key}.html').read_text())
rows=['Quell-URL\tOffline-Ziel\tStatus']
for key,p in source['pages'].items():
    target = ('bestand/startseite/index.html' if not key else key+'/index.html') if key in pages else '—'
    if key in paths and key not in pages:
        target = key+'/index.html'
    status = p.get('error','Übernommen')
    if not key:
        target = 'index.html#ecosteps-bestand + bestand/startseite/index.html'
    if key == 'beratung':
        status = 'Beratungseinstieg neu; Original unter beratung/beratungsqualität/index.html'
    if key in ('datenschutz','agb','referenzen') and key not in pages:
        status += '; neue Zielseite erstellt'
    if key == 'kontakt':
        status = 'Kontaktwege übernommen; Kartenadresse abweichend, Karte ausgelassen'
    rows.append(f"{p['url']}\t{target}\t{status}")
for url,name,ok in source['media']:
    rows.append(f'{url}\tassets/{name}\t'+('Übernommen' if ok else 'Nicht abrufbar'))
for key, page in pages.items():
    for _, url in page.get('videos', []):
        rows.append(f'{url}\t{key}/index.html\tExterner Klicklink; keine lokale Videodatei')
(OUT/'URL-Zuordnung.tsv').write_text('\n'.join(rows)+'\n')
if args.live:
    sitemap = ''.join(f'<url><loc>{canonical_url(path)}</loc></url>' for path in sorted(paths - {'bestand/startseite'}))
    (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+sitemap+'</urlset>\n')
    (OUT/'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {canonical_url("")}sitemap.xml\n')
    (OUT/'_redirects').write_text('\n'.join(f'/{key} /{key}/ 301' for key in sorted(paths) if key)+'\n')
for name in ('README.txt','CHANGELOG.md'):
    if (ROOT/name).exists(): shutil.copy2(ROOT/name,OUT/name)
print(f'{version} · {len(list(OUT.rglob("index.html")))} Seiten · {OUT}')
