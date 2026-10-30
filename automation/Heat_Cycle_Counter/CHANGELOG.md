# Changelog

Alle wesentlichen Änderungen am Blueprint „Wärmepumpe – Heizzyklenzähler (HT/NT, pro Tag)“.
Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

## [1.1.0] – 2026-10-27

### Hinzugefügt
- Optionale **Gesamtzähler HT/NT**, die nie zurückgesetzt werden. Zusammen mit einem Template-Sensor (`state_class: total_increasing`) ermöglichen sie Langzeitstatistik und frei wählbare Zeiträume über die Datumsauswahl des Energie-Dashboards.
- README: Anleitung für Template-Sensor und Dashboard-Karten (`energy-date-selection`, `statistics-graph`, `statistic`).

### Geändert
- Die Tageszähler HT/NT sind jetzt **optional**. Es muss mindestens ein Zählerpaar (Tages- oder Gesamtzähler) gesetzt sein. Bestehende Automationen funktionieren unverändert weiter.
- Die Vortag-Zähler werden nur übernommen, wenn der zugehörige Tageszähler gesetzt ist.

## [1.0.0] – 2026-10-14

Erstveröffentlichung.

### Hinzugefügt
- Zyklenerkennung über Leistungssensor mit Start-/Ende-Schwelle und jeweiliger Verzögerung.
- Getrennte Tageszähler für Haupttarif (HT) und Nebentarif (NT); Zuordnung nach Tarif zum Zyklusbeginn, auch über Tarifwechsel hinweg.
- Zyklus-Merker (`input_boolean`) gegen Doppelzählung, mit Bereinigung nach Home-Assistant-Neustart.
- Optionale Vortag-Zähler, die kurz vor Mitternacht (Standard 23:59:59) den Tagesendstand übernehmen.
- Tägliche Rückstellung der Tageszähler (Standard 00:00:00); Übernahme- und Rückstellzeit getrennt einstellbar.
- Alle Sensoren, Helfer, Schwellen, Verzögerungen und Zeiten über die Blueprint-Maske einstellbar.
- README mit Installation, Helfern, Eingaben und Hinweisen zur Langzeitstatistik.

[1.1.0]: https://github.com/jubie25/blueprints/blob/main/automation/Heat_Cycle_Counter
[1.0.0]: https://github.com/jubie25/blueprints/blob/main/automation/Heat_Cycle_Counter
