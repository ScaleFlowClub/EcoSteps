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
    return f'<article class="card">{illustration}<div><h3>{link(path, heading)}</h3><p>{desc}</p>{link(path, "Mehr erfahren <span aria-hidden=true>↗</span>", "text-link")}</div></article>'

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
    floating = link(consultation,cta+' <span aria-hidden="true">↗</span>','fixed-cta') if articles else ''
    banner = (ROOT / 'content/cookies.html').read_text() if cookies and not args.live else ''
    doc = f'''<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} · EcoSteps</title><link rel="stylesheet" href="@/assets/site.css"><script src="@/assets/site.js" defer></script></head>
<body data-mode="{'live' if args.live else 'offline'}">
<a class="skip" href="#inhalt">Zum Inhalt springen</a>
<header class="header"><div class="wrap header-inner">
{link('index.html',image('ecosteps_logo.jpg','EcoSteps – Startseite',True),'logo')}
<button class="menu" type="button" aria-expanded="false" aria-controls="navigation">Menü</button>
<nav id="navigation" aria-label="Hauptnavigation">{links}</nav><a class="header-phone" href="tel:+4922566209841">{phone}</a>
</div></header>
<main id="inhalt" tabindex="-1">{body}</main>
<footer class="footer"><div class="wrap footer-grid"><div>{link('index.html',image('ecosteps_logo.jpg','EcoSteps – Startseite'),'logo')}<p>ecosteps GmbH &amp; Co. KG<br>Virnicher Str. 8<br>53894 Mechernich</p>{contact()}</div><div><h2>EcoSteps</h2>{links}</div><div><h2>Rechtliches</h2>{legal}{cookies}</div></div></footer>
{floating}{banner}
</body></html>'''
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(doc.replace('@/',prefix),encoding='utf-8')

def homepage():
    hero = f'''<section class="hero"><div class="wrap hero-grid"><div class="hero-copy"><p class="eyebrow">Photovoltaik · Speicher · Energieberatung</p><h1>Solarstrom.<br><em>Für Ihren Alltag.</em></h1><p>Wir planen Photovoltaik für Privathaushalte und Unternehmen. Nutzen Sie mehr eigenen Strom, senken Sie Ihre Energiekosten und beziehen Sie weniger aus dem Netz.</p>{link('beratung/index.html',cta+' <span aria-hidden="true">↗</span>','button primary')}</div><figure class="hero-media">{image('ecosteps_640x385-teaser_home-gewerbe.jpg','Photovoltaikmodule auf den Dächern eines Gewerbegebäudes',True)}</figure></div></section>
<section class="proof"><div class="wrap"><span><strong>Seit 2005</strong> im Solarmarkt</span><span><strong>Produktneutral</strong> beraten</span><span><strong>Individuell</strong> geplant</span></div></section>'''
    services = ''.join([card('photovoltaik/eigenverbrauch/index.html','Photovoltaik','Solarstrom erzeugen und passend zum eigenen Verbrauch nutzen.'),card('speicher/eigenverbrauch/index.html','Stromspeicher','Tagsüber erzeugten Solarstrom für später speichern.'),card('service/index.html','Anlagenservice','Erträge im Blick behalten und bestehende Technik weiterentwickeln.')])
    audience = ''.join([card('photovoltaik/eigenverbrauch/index.html','Für Privathaushalte','Planen Sie Solarstrom für Ihr Zuhause.',('ecosteps_640x385-teaser_home-4.jpg','Zwei Menschen genießen die Sonne')),card('gewerbekunden/eigenverbrauch/index.html','Für Unternehmen','Richten Sie die Anlage an Betriebszeiten und Verbrauch aus.',('ecosteps_640x385-teaser_home-gewerbe.jpg','Solarmodule auf Gewerbedächern'))])
    guide = f'<section class="highlight"><div class="wrap"><p class="eyebrow">Energieratgeber</p><h2>Wie viel Solarstrom können Sie selbst nutzen?</h2><p>Erfahren Sie, wie Eigenverbrauch, Speicher und Anlagengröße zusammenspielen.</p>{link("energieratgeber/index.html","Zum Energieratgeber ↗","button primary")}</div></section>' if articles else ''
    references = card('referenzen/index.html','PV-Anlage auf einer Kfz-Werkstatt','Das Bestandsbeispiel zeigt 54,2 kWp Anlagenleistung und einen solaren Deckungsanteil von 60,7 %.',('werkstatt.jpg','Arbeit in einer Kfz-Werkstatt, Motiv der Bestandsseite'))
    return hero+f'<section class="section wrap"><p class="eyebrow">Unsere Leistungen</p><h2>Technik, die zu Ihrem Verbrauch passt.</h2><div class="cards">{services}</div></section><section class="section light"><div class="wrap"><h2>Solarstrom für Zuhause und Betrieb</h2><div class="cards two">{audience}</div></div></section>'+guide+f'<section class="section wrap"><p class="eyebrow">Erfahrung mit Photovoltaik</p><h2>Fast 1.000 Anlagen von 2008 bis 2015</h2><div class="cards two">{references}</div><p class="archive-link">{link("bestand/startseite/index.html","Meldungen und Angebote der bisherigen Startseite ↗","text-link")}</p></section>'

categories = {'photovoltaik':'Photovoltaik','speicher':'Stromspeicher','heizung':'Heizung','gewerbekunden':'Für Unternehmen','beratung':'Energieberatung'}
paths = set(pages) | {'leistungen','bestand/startseite','referenzen'}
if articles:
    paths |= {'energieratgeber',*articles}
if (ROOT / 'content/cookies.html').exists():
    paths |= {'datenschutz','agb'}
shutil.copytree(ROOT / 'assets', OUT / 'assets', dirs_exist_ok=True)
layout('', 'Solarstrom für Privathaushalte und Unternehmen', homepage())
layout('bestand/startseite','Inhalte der bisherigen Startseite',intro('Bisherige Startseite','Die folgenden Meldungen und Angebote stammen von der Bestandswebsite. Preis- und Leistungsangaben können zeitgebunden sein.','Bestandsinhalte')+f'<section class="section wrap prose">{legacy("")}</section>')
sections = ''
for category, label in categories.items():
    entries = [(k,p) for k,p in pages.items() if k.startswith(category+'/')]
    if entries:
        sections += f'<h2>{label}</h2><ul>'+''.join(f'<li>{link(k+"/index.html",escape(p["title"].split(" - ")[-1]))}</li>' for k,p in entries)+'</ul>'
layout('referenzen','Referenzen',intro('Referenzen','Beispiele aus der bisherigen EcoSteps-Website.')+'<section class="section wrap cards two">'+card('gewerbekunden/eigenverbrauch/index.html','Kfz-Werkstatt','Historisches Anlagenbeispiel mit Leistungsprofil und Jahreswerten.',('werkstatt.jpg','Arbeit in einer Kfz-Werkstatt, Motiv der Bestandsseite'))+card('photovoltaik/eigenverbrauch/index.html#4','Kundenanlagen','Historische Beispiele für Eigenverbrauch in Privathaushalten.')+'</section>')
layout('leistungen','Leistungen',intro('Unsere Leistungen','Photovoltaik, Speicher, Wärme und Anlagenservice.')+f'<section class="section wrap prose">{sections}<h2>Anlagenservice</h2>{link("service/index.html","Zum Anlagenservice ↗","text-link")}</section>')
for key,p in pages.items():
    if not key: continue
    title = escape(p['title'])
    body = intro(title,'','Bestandsinhalte')+f'<section class="section wrap prose">{legacy(key)}</section>'
    if key.startswith(('photovoltaik/','speicher/','heizung/','gewerbekunden/','beratung/')):
        body = body.replace('<div class="archive">','<p class="notice">Bestandsinhalt. Angaben zu Preisen, Produkten, Vergütung und Förderung können zeitgebunden sein.</p><div class="archive">',1)
    if key == 'photovoltaik/eigenverbrauch':
        video = '<p class="notice"><a href="https://www.youtube.com/watch?v=w3wNNmuIyEM">EcoSteps-Video zu Photovoltaik, Speicher und Heizung ansehen</a> (YouTube, Internetverbindung erforderlich).</p>'
        body = body.replace('<p></p>', video, 1)
    if key == 'gewerbekunden/eigenverbrauch':
        body = body.replace('<div class="archive">','<p class="notice">Die historische Beispielrechnung enthält abweichende Werte: 12.772 kWh Netzbezug zu 0,22 €/kWh ergeben etwa 2.810 € im Jahr. In der Originaltabelle stehen 825 €.</p><div class="archive">',1)
    if key == 'kontakt':
        body = intro('Kontakt','Schreiben Sie uns eine Nachricht oder rufen Sie uns an.')+f'<section class="section wrap prose">{contact()}<p>{link("beratung/index.html",cta,"button primary")}</p></section>'
    if key == 'beratung' and (ROOT/'content/consultation.html').exists():
        form = '' if args.live else (ROOT/'content/consultation.html').read_text()
        body = intro('Beratungsgespräch anfragen','Wir klären, welche Lösung zu Ihrem Stromverbrauch, Ihrer Fläche und Ihren Zielen passt.','Energieberatung')+f'''<section class="section wrap consult"><div class="prose"><h2>So bereiten Sie sich vor</h2><ul><li>Jahresstromverbrauch oder letzte Stromabrechnung</li><li>Angaben zu einer vorhandenen PV-Anlage und zum Speicher</li><li>Bei Unternehmen die typischen Betriebs- und Verbrauchszeiten</li></ul><h2>Direkter Kontakt</h2>{contact()}</div>{form}</section>'''
    if key == 'impressum' and (ROOT/'content/legal.html').exists():
        body = intro('Impressum','')+(ROOT/'content/legal.html').read_text()+f'<section class="section wrap prose"><details><summary>Impressum und Datenschutzhinweise der Bestandswebsite</summary>{legacy(key)}</details></section>'
    layout(key,p['title'] if key!='beratung' else 'Beratungsgespräch anfragen',body)
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
    rows.append(f"{p['url']}\t{target}\t{p.get('error','Übernommen')}")
for url,name,ok in source['media']:
    rows.append(f'{url}\tassets/{name}\t'+('Übernommen' if ok else 'Nicht abrufbar'))
(OUT/'URL-Zuordnung.tsv').write_text('\n'.join(rows)+'\n')
if args.live:
    (OUT/'_redirects').write_text('\n'.join(f'/{key} /{key}/ 301' for key in sorted(paths) if key)+'\n')
for name in ('README.txt','CHANGELOG.md'):
    if (ROOT/name).exists(): shutil.copy2(ROOT/name,OUT/name)
print(f'{version} · {len(list(OUT.rglob("index.html")))} Seiten · {OUT}')
