from html import escape
from pathlib import Path
import json, re, shutil, argparse

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--live', action='store_true', help='Statische Live-Fassung mit direkten Kontaktwegen')
args = parser.parse_args()
OUT = ROOT / 'dist' / ('live' if args.live else 'offline')
OUT.mkdir(parents=True, exist_ok=True)
source = json.loads((ROOT / 'content/sources.json').read_text())
pages = {key: item for key, item in source['pages'].items() if 'html' in item}
version = (ROOT / 'VERSION').read_text().strip()
phone = '02256 620 98 41'
mail = 'info@ecosteps-solar.de'
cta = 'Beratungsgespräch anfragen'
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

def legacy(path):
    p = pages[path]
    html = p['html']
    def replace(match):
        key = match[1]
        return '@/'+(key+'/index.html' if key else 'index.html') if key in pages else 'https://www.ecosteps-solar.de/'+key
    html = re.sub(r'@@page/([^"\s]*)', replace, html).replace('@@asset/', '@/assets/')
    html = re.sub(r'<img(?![^>]*\balt=)', '<img alt=""', html)
    return f'<div class="archive">{html}</div>'

def contact():
    return f'<a href="tel:+4922566209841">{phone}</a><br><a href="mailto:{mail}">{mail}</a>'

def layout(path, title, body):
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
    doc = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · EcoSteps</title><link rel="stylesheet" href="@/assets/site.css"><script src="@/assets/site.js" defer></script></head>
<body class="{'home' if not path else 'interior'}" data-mode="{'live' if args.live else 'offline'}">
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="header"><div class="wrap header-inner">
{link('index.html',image('ecosteps_logo.jpg','EcoSteps – Startseite',True),'logo')}
<button class="menu" type="button" aria-expanded="false" aria-controls="navigation">Menü</button>
<nav id="navigation" aria-label="Hauptnavigation">{links}</nav><a class="header-phone" href="tel:+4922566209841">{phone}</a>
</div></header>
<main id="inhalt" tabindex="-1">{body}</main>
<footer class="footer"><div class="wrap footer-grid"><div>{link('index.html',image('ecosteps_logo.jpg','EcoSteps – Startseite'),'logo')}<p>ecosteps GmbH &amp; Co. KG<br>Virnicher Str. 8<br>53894 Mechernich</p>{contact()}</div><div><h2>EcoSteps</h2>{footer_links}</div><div><h2>Rechtliches</h2>{legal}{cookies}</div></div></footer>
{floating}{banner}
</body></html>'''
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(doc.replace('@/',prefix),encoding='utf-8')

def homepage():
    hero = f"""
<section class="hero" aria-labelledby="home-title">
  <figure class="hero-media">{image('ecosteps_640x385-teaser_home-gewerbe.jpg','Photovoltaik auf den Dächern eines Gewerbegebäudes',True)}</figure>
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Photovoltaik · Speicher · Energieberatung</p>
      <h1 id="home-title">Solarstrom.<br><em>Für Ihren Alltag.</em></h1>
      <p>Wir planen Photovoltaik für Privathaushalte und Unternehmen. Nutzen Sie mehr eigenen Strom und senken Sie Ihren Netzbezug.</p>
      {link('beratung/index.html',cta+' <span aria-hidden="true">→</span>','button primary')}
    </div>
    <aside class="hero-note">
      <strong>Seit 2005</strong>
      <span>EcoSteps plant Photovoltaik für Haushalte und Betriebe.</span>
    </aside>
  </div>
</section>
<section class="proof" aria-label="So arbeitet EcoSteps"><div class="wrap">
  <span><strong>Produktneutral</strong> beraten</span>
  <span><strong>Individuell</strong> geplant</span>
  <span><strong>Vor Ort</strong> in Mechernich</span>
</div></section>"""

    approach = f"""
<section class="section wrap approach">
  <div class="section-heading"><p class="eyebrow">Eigenverbrauch</p><h2>Mehr vom eigenen<br>Solarstrom nutzen.</h2></div>
  <div class="cards feature-grid">
    <article class="card feature feature-simple"><div>
      <h3>Solarstrom direkt nutzen</h3>
      <p>Wenn Ihre Anlage Strom erzeugt, versorgt sie laufende Geräte direkt.</p>
      {link('photovoltaik/eigenverbrauch/index.html','So funktioniert Eigenverbrauch <span aria-hidden="true">→</span>','text-link')}
    </div></article>
    <article class="card feature feature-photo">
      {image('ecosteps_640x385-teaser_home-4.jpg','Zwei Menschen genießen die Sonne')}
      <div><h3>Für den Abend speichern</h3><p>Ein Speicher macht Solarstrom auch nach Sonnenuntergang nutzbar.</p>
      {link('speicher/eigenverbrauch/index.html','Speicher kennenlernen <span aria-hidden="true">→</span>','text-link')}</div>
    </article>
    <article class="card feature feature-dark"><div>
      <p class="feature-number">60,7<span> %</span></p>
      <h3>Solarer Deckungsanteil</h3>
      <p>In der dokumentierten Jahresrechnung für eine Kfz-Werkstatt.</p>
      {link('gewerbekunden/eigenverbrauch/index.html','Werkstattbeispiel ansehen <span aria-hidden="true">→</span>','text-link')}
    </div></article>
  </div>
</section>"""

    services = [
        ('photovoltaik/eigenverbrauch/index.html','Photovoltaik','Anlagen passend zu Dachfläche und Stromverbrauch.'),
        ('speicher/eigenverbrauch/index.html','Stromspeicher','Solarstrom speichern und später nutzen.'),
        ('heizung/waerme-erzeugen/index.html','Wärme mit Solarstrom','Überschüsse für Warmwasser und Heizung einsetzen.'),
        ('service/index.html','Anlagenservice','Erträge prüfen und bestehende Anlagen betreuen.'),
    ]
    service_rows = ''.join(
        f'<li>{link(url, f"<strong>{title}</strong><span>{description}</span><span class=service-arrow aria-hidden=true>→</span>")}</li>'
        for url, title, description in services
    )
    offering = f"""
<section class="section offering">
  <div class="wrap offering-grid">
    <div>
      <p class="eyebrow">Leistungen</p><h2>Von der Planung<br>bis zum Anlagenservice.</h2>
      {link('leistungen/index.html','Alle Leistungen <span aria-hidden="true">→</span>','button primary')}
      <div class="offering-photos">
        {image('ecosteps_PhoVo_Produkte.jpg','Photovoltaikmotiv aus der EcoSteps-Produktübersicht')}
        {image('ecosteps_640x385-teaser_home-gewerbe.jpg','Photovoltaik auf einem Gewerbedach')}
      </div>
    </div>
    <ul class="service-list">{service_rows}</ul>
  </div>
</section>
<section class="section wrap">
  <div class="section-heading"><p class="eyebrow">Für wen wir planen</p><h2>Solarstrom für Zuhause<br>und den Betrieb.</h2></div>
  <div class="audience-links">
    {link('photovoltaik/eigenverbrauch/index.html','Für Privathaushalte <span aria-hidden="true">→</span>')}
    {link('gewerbekunden/eigenverbrauch/index.html','Für Unternehmen <span aria-hidden="true">→</span>')}
  </div>
</section>
<section class="highlight"><div class="wrap guide-grid"><div>
  <p class="eyebrow">Energieratgeber</p><h2>Wie viel Solarstrom können Sie selbst nutzen?</h2>
  <p>Erfahren Sie, wie Eigenverbrauch, Speicher und Anlagengröße zusammenspielen.</p></div>
  {link('energieratgeber/index.html','Zum Energieratgeber <span aria-hidden="true">→</span>','button primary')}
</div></section>
<section class="section wrap home-references">
  <p class="eyebrow">Referenzen</p><h2>Fast 1.000 Anlagen von 2008 bis 2015.</h2>
  <div class="audience-links">
    {link('referenzen/index.html','Referenzen ansehen <span aria-hidden="true">→</span>')}
    {link('bestand/startseite/index.html','Bisherige Meldungen und Angebote <span aria-hidden="true">→</span>')}
  </div>
</section>"""
    return hero + approach + offering


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
        p_title = label
    else:
        p_title = p['title']
    if key == 'speicher/technik':
        body = re.sub(r'<h2>([^<]*[Ff]lexibl[^<]*)</h2>', r'<h2 id="5">\1</h2>', body, count=1)
    if key == 'photovoltaik/eigenverbrauch':
        video = '<p class="notice"><a href="https://www.youtube.com/watch?v=w3wNNmuIyEM">EcoSteps-Video zu Photovoltaik, Speicher und Heizung ansehen</a> (YouTube, Internetverbindung erforderlich).</p>'
        body = body.replace('<p></p>', video, 1)
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
        body = intro('Beratungsgespräch anfragen','Wir klären, welche Lösung zu Ihrem Stromverbrauch, Ihrer Fläche und Ihren Zielen passt.','Energieberatung')+f'''<section class="section wrap consult"><div class="prose"><h2>So bereiten Sie sich vor</h2><ul><li>Jahresstromverbrauch oder letzte Stromabrechnung</li><li>Angaben zu einer vorhandenen PV-Anlage und zum Speicher</li><li>Bei Unternehmen die typischen Betriebs- und Verbrauchszeiten</li></ul><h2>Direkter Kontakt</h2>{contact()}</div>{form}</section>'''
    if key == 'impressum' and (ROOT/'content/legal.html').exists():
        body = intro('Impressum','')+(ROOT/'content/legal.html').read_text()+f'<section class="section wrap prose"><details><summary>Impressum und Datenschutzhinweise der Bestandswebsite</summary>{legacy(key)}</details></section>'
    layout(key,p_title if key!='beratung' else 'Beratungsgespräch anfragen',body)
if articles:
    layout('energieratgeber','Energieratgeber',intro('Energieratgeber','Antworten rund um Solarstrom, Eigenverbrauch und die Planung Ihrer Anlage.')+'<section class="section wrap cards">'+''.join(card(key+'/index.html',a['title'],a['intro']) for key,a in articles.items())+'</section>')
    for key,a in articles.items():
        layout(key,a['title'],intro(a['title'],a['intro'],'Energieratgeber')+f'<section class="section wrap prose">{a["html"]}<p>{link("beratung/index.html",cta,"button primary")}</p></section>')
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
        target = 'index.html + bestand/startseite/index.html'
    if key == 'beratung':
        status = 'Beratungseinstieg neu; Original unter beratung/beratungsqualität/index.html'
    if key in ('datenschutz','agb','referenzen') and key not in pages:
        status += '; neue Zielseite erstellt'
    if key == 'kontakt':
        status = 'Kontaktwege übernommen; Kartenadresse abweichend, Karte ausgelassen'
    rows.append(f"{p['url']}\t{target}\t{status}")
for url,name,ok in source['media']:
    rows.append(f'{url}\tassets/{name}\t'+('Übernommen' if ok else 'Nicht abrufbar'))
rows.append('https://www.youtube.com/embed/w3wNNmuIyEM\tphotovoltaik/eigenverbrauch/index.html\tExterner Klicklink; keine lokale Videodatei')
(OUT/'URL-Zuordnung.tsv').write_text('\n'.join(rows)+'\n')
if args.live:
    (OUT/'_redirects').write_text('\n'.join(f'/{key} /{key}/ 301' for key in sorted(paths) if key)+'\n')
for name in ('README.txt','CHANGELOG.md'):
    if (ROOT/name).exists(): shutil.copy2(ROOT/name,OUT/name)
print(f'{version} · {len(list(OUT.rglob("index.html")))} Seiten · {OUT}')
