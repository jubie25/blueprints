# Changelog

Alle wesentlichen Änderungen am Blueprint „Wärmepumpe – Heizzyklenzähler (HT/NT, pro Tag)“.
Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

## [1.0.0] – 2026-10-14

### Hinzugefügt
- Zyklenerkennung über Leistungssensor mit Start-/Ende-Schwelle und jeweiliger Verzögerung.
- Getrennte Tageszähler für Haupttarif (HT) und Nebentarif (NT); Zuordnung nach Tarif zum Zyklusbeginn, auch über Tarifwechsel hinweg.
- Zyklus-Merker (`input_boolean`) gegen Doppelzählung, mit Bereinigung nach Home-Assistant-Neustart.
- Optionale Vortag-Zähler, die kurz vor Mitternacht (Standard 23:59:59) den Tagesendstand übernehmen.
- Tägliche Rückstellung der Tageszähler (Standard 00:00:00); Übernahme- und Rückstellzeit getrennt einstellbar.
- Alle Sensoren, Helfer, Schwellen, Verzögerungen und Zeiten über die Blueprint-Maske einstellbar.
- README mit Installation, Helfern, Eingaben und Hinweisen zur Langzeitstatistik.

[1.0.0]: https://github.com/jubie25/blueprints/blob/main/automation/Heat_Cycle_Counter
