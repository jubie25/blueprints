# Changelog

Alle nennenswerten Änderungen an diesem Blueprint werden hier dokumentiert.
Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [Semantic Versioning](https://semver.org/lang/de/).

## [1.2.0] – 2026-10-18

### Hinzugefügt
- Neue Auswahlliste „Verhalten zu Beginn“ im eingeklappten Abschnitt „Display beim Start des Ablaufs“ mit den Optionen „Display-Reset (Aus, Pause, Ein)“, „Nur einschalten“, „Nur ausschalten“ und „Display-Schalter nicht verändern“. Standard ist der Display-Reset, das Verhalten bestehender Automationen bleibt damit unverändert.

### Geändert
- Die Pause zwischen Aus und Ein wird nur noch beim Display-Reset angewendet.
- Hinweis: Bei Automationen, die vor 1.2.0 aus dem Blueprint erstellt wurden, gilt der Standard (Display-Reset), solange die Auswahl nicht geändert wird.

## [1.1.1] – 2026-10-16

### Behoben
- `min_version` korrekt verschachtelt unter `blueprint.homeassistant.min_version` statt direkt unter `blueprint:`, damit Home Assistant die Mindestversion auswertet.

## [1.1.0] – 2026-10-15

### Geändert
- Ausführungsmodus von `restart` auf `single` (mit `max_exceeded: silent`) umgestellt. Ein erneuter Trigger startet den Ablauf nicht mehr neu, dadurch entfällt der erneute Aus/Ein-Zyklus am Display (Flackern). Das periodische Triggern des Displays bleibt unverändert.
- Blueprint in `presence_trigger_fully_browser` umbenannt (Blueprint-Name und Dateiname).
- `author` und `source_url` auf das GitHub-Repository eingetragen.

## [1.0.0] – 2026-10-15

### Hinzugefügt
- Erste Veröffentlichung als Blueprint, abgeleitet aus einer bestehenden Einzel-Automation.
- Eingabemaske für Präsenzsensor, Display-Schalter und Aktivitäts-Button.
- Optionale, eingeklappte Einstellungen für Zeiten und Wiederholungen (Standardwerte wie in der Original-Automation: 300 ms, 2 Drücke, 2 s, 51 s).
- Trigger-ID `Presence` beibehalten.

### Geändert
- Präsenzprüfung in der Schleife per `state`-Bedingung (`on`) statt `occupancy.is_detected`, damit jeder `binary_sensor` unabhängig von der Geräteklasse funktioniert.
