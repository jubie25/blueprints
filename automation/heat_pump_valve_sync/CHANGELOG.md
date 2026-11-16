# Changelog

Alle wesentlichen Änderungen an diesem Blueprint. Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

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
