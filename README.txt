EcoSteps · Offline-Vorschau v1.0.3
ZIP entpacken und index.html öffnen.

Die Gestaltung, internen Links, Bilder und PDF-Downloads funktionieren lokal.
Telefon-, E-Mail- und externe Quellenlinks benötigen ihre jeweilige Anwendung
oder eine Internetverbindung. Formular, Terminauswahl und Cookies sind Offline-Demos.

Quellcode
Build offline: python3 build.py
Build für Live: python3 build.py --live
Optionaler Prüfserver: python3 -m http.server 8000 --directory dist/offline
Für die Offline-Vorschau genügt das direkte Öffnen von dist/offline/index.html.
Ausgaben stehen unter dist/offline und dist/live. Das Build-Skript benötigt Python 3
und keine externen Python-Pakete. Inhaltsinventar und Medien liegen unter content und assets.
In der ZIP stehen URL-Zuordnung.tsv und CHANGELOG.md neben index.html.

Bestandsquellen und Abweichungen (Abruf 19.11.2026)
- Navigation, Footer, interne Links und öffentliche WordPress-REST-Liste geprüft.
  /wp-json/wp/v2/pages meldete 21 veröffentlichte Seiten. /beratung/ ist zusätzlich
  als Einstieg verlinkt und zeigte den Inhalt von /beratung/beratungsqualität.
- /sitemap.xml und /wp-sitemap.xml waren nicht verfügbar. /referenzen/, /agb/ und
  /datenschutz/ hatten keine eigene erreichbare Bestandsseite. Datenschutz-Hinweise
  stehen im alten Impressum und sind dort als Bestandsinhalt erhalten.
- https://www.ecosteps-solar.de/impressum/ nennt Virnicher Str. 8, 53894 Mechernich.
  Die alte Karte unter https://www.ecosteps-solar.de/kontakt/ nennt Siemensstraße 25,
  50374 Erftstadt. Im Relaunch stehen die Angaben aus dem Impressum. Bitte bestätigen.
- https://www.ecosteps-solar.de/gewerbekunden/eigenverbrauch nennt in der alten Rechnung
  825 EUR für 12.772 kWh zu 0,22 EUR/kWh. Rechnerisch sind es 2.809,84 EUR.
  Die Originalwerte bleiben mit einem Hinweis erhalten.
- Die beiden YouTube-Videos bleiben auf den zugehörigen Seiten verlinkt. Für die
  Offline-Wiedergabe sind freigegebene Videodateien erforderlich.
- Das Foto im Einstieg stammt aus dem Bestands-Teaser für Gewerbekunden. Es wird
  auf der Startseite nicht als Nachweis eines bestimmten Projekts bezeichnet.

Vor Veröffentlichung
- Firmierung, Anschrift, Vertretung, Registerdaten, USt-ID und die Anwendbarkeit
  weiterer Impressumspflichten bestätigen. Impressum und Rechtstexte freigeben.
- Historische Preis-, Förder-, Vergütungs-, Produkt- und Renditeangaben prüfen.
  Kundenzitate, Referenzbilder und Produkt-PDFs für die erneute Nutzung freigeben.
- Neue Ratgebertexte und Rechenbeispiele freigeben. Die Beispielpreise sind
  fiktive Annahmen, keine aktuellen Vergütungssätze.
- Hostingziel, Domainzugang, Serverprotokolle, Speicherfristen, Verarbeitungsorte,
  Auftragsverarbeiter, Postfachdienst und mögliche Drittlandübermittlungen klären.
  Datenschutzerklärung anhand der endgültigen Konfiguration freigeben.
- Für AGB tatsächliche Angebots-, Vertrags-, Zahlungs-, Abnahme- und Widerrufsabläufe
  abstimmen. Vorhandene freigegebene Vertragsunterlagen gegebenenfalls bereitstellen.
- Für Versand oder Buchung Dienst, Zuständigkeit, Empfänger, Datenschutzangaben,
  Zugang und geprüften Bestätigungsablauf bereitstellen. Bis dahin stehen im
  Live-Build die direkten Kontaktwege zur Verfügung.
- Live-Weiterleitungen in dist/live/_redirects auf Eignung für das gewählte Hosting
  prüfen. Bestehende Schrägstrich-Pfade sollten direkt weiter funktionieren.
