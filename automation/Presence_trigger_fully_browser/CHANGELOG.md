# Changelog

Alle nennenswerten Änderungen an diesem Blueprint werden hier dokumentiert.
Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [Semantic Versioning](https://semver.org/lang/de/).

## [1.0.0] – 2026-10-15

### Hinzugefügt
- Erste Veröffentlichung als Blueprint, abgeleitet aus einer bestehenden Einzel-Automation.
- Eingabemaske für Präsenzsensor, Display-Schalter und Aktivitäts-Button.
- Optionale, eingeklappte Einstellungen für Zeiten und Wiederholungen (Standardwerte wie in der Original-Automation: 300 ms, 2 Drücke, 2 s, 51 s).
- Trigger-ID `Presence` beibehalten.

### Geändert
- Präsenzprüfung in der Schleife per `state`-Bedingung (`on`) statt `occupancy.is_detected`, damit jeder `binary_sensor` unabhängig von der Geräteklasse funktioniert.

[1.0.0]: https://github.com/<GITHUB-USER>/<REPOSITORY>/releases/tag/v1.0.0
