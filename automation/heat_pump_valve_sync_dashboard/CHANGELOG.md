# Changelog

Alle wesentlichen Änderungen an diesem Blueprint. Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

## Monitoring (optional) 1.0.0 - 2026-11-16

### Hinzugefügt
- Package `heat_pump_valve_sync_monitor.yaml` mit Status-Text, Regler mit Bedarf, Alter des ältesten Bedarfs, Restzeit der Mindestpause sowie Starts und Laufzeit heute.
- Dashboard `heat_pump_valve_sync_dashboard.yaml` mit Statuskopf, Chips und einer Kachel pro Regler. Die Blueprint-Version ändert sich dadurch nicht.

## [1.1.1] - 2026-11-16

### Geändert
- Dokumentation: Pro Regler genau ein Bedarfsschalter und ein Adapter. Ein Adapter darf nie von zwei Reglern geschaltet werden (gegenseitiges Überschreiben bei Neustart oder `keep_alive`). Die Blueprint-Logik ist unverändert.

## [1.1.0] - 2026-11-16

### Hinzugefügt
- Eingabe "Dauerhaft offene Ventile": Diese Ventile bleiben offen, solange "Sync aktiv" an ist (z. B. ein Handtuchheizkörper ohne eigenen Regler als Mindestdurchfluss).

### Geändert
- Ist "Sync aktiv" aus, werden Bypass- und dauerhaft offene Ventile nicht mehr geschlossen, sondern nicht angefasst und können manuell bedient werden. Bisher wurden reine Bypass-Ventile im Rückfallmodus geschlossen.

## [1.0.0] - 2026-11-13

### Hinzugefügt
- Erste Version.
- Sammeln und Freigeben: Der Bedarf der Räume wird über virtuelle Schalter gesammelt und die Ventile werden gemeinsam geöffnet.
- Lauferkennung über eine Leistungsmessung mit Ein- und Ausschaltverzögerung (Helfer "Lauf aktiv").
- Freigabe nach Mindestanzahl Räume oder Höchstwartezeit, mit Mindestpause zwischen Freigaben.
- Bypass-Ventile für den Mindestdurchfluss.
- Zuordnung Bedarf → Ventile als YAML (ein Ventil darf mehreren Räumen zugeordnet sein).
- Rückfallmodus ("Sync aktiv" aus): Ventile folgen direkt dem Bedarf.
- Abgleich im Minutentakt, nur abweichende Ventile werden mit einstellbarer Pause geschaltet.
- Schutzfunktionen: Höchstdauer einer Freigabe, Höchstdauer "Lauf aktiv", Neubestimmung von "Lauf aktiv" beim Start von Home Assistant.
- Option "Ventile invertiert" für stromlos offene Ventile.
