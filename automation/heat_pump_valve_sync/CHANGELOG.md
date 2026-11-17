# Changelog

Alle wesentlichen Änderungen an diesem Blueprint. Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

## Blueprint 1.2.0 - 2026-11-17

### Hinzugefügt
- Neues Feld "Bedarfsschalter (für die Auslösung)": Eine Änderung eines Bedarfsschalters löst die Automatisierung sofort aus. **Das Feld ist Pflicht; nach dem Update dort alle Bedarfsschalter aus der Zuordnung eintragen.**
- Neues Feld "Sicherheitstakt" (1, 2, 5, 10 oder 15 Minuten, Standard 5) statt des festen Minutentakts. Er erkennt das Ablaufen von Mindestpause und Höchstwartezeit.
- `stored_traces: 50`, damit die Traces nicht mehr nach wenigen Minuten überschrieben werden.
- Der Sicherheitstakt gleicht "Lauf aktiv" mit der Leistungsmessung ab und korrigiert so einen verpassten Schwellenübergang.

### Geändert
- `continue_on_error` beim Schalten der Ventile: Ein fehlgeschlagener Schaltbefehl bricht die Automatisierung nicht mehr ab, die übrigen Ventile werden trotzdem geschaltet.

## Monitoring (optional) 1.1.0 - 2026-11-16

### Hinzugefügt
- Dashboard: Kompakte Karte "Ventile real" mit dem tatsächlichen Zustand aller 25 Ventile (offen, zu, nicht erreichbar), gruppiert nach Etage, mit Zähler "x von 25 offen". Sie liest die Ventilschalter direkt und aktualisiert sich bei jeder Zustandsänderung.

## Monitoring (optional) 1.0.2 - 2026-11-16

### Behoben
- Dashboard: Das Feld für den Namen hieß `n`. YAML 1.1 liest das als `false`, der Raw-Editor schrieb daraus den Schlüssel `'false'`, und die Kachel zeigte den Namen nicht an. Das Feld heißt jetzt `lbl`.

### Geändert
- Dashboard: OGBad ist als dauerhaft offen beschriftet (Eintrag unter "Dauerhaft offene Ventile" im Blueprint), EGKüche bleibt Bypass.
- Dashboard: Entity-IDs auf den tatsächlichen Stand gebracht (`climate.egaz_thermostat_raum`, `climate.ogsz_thermostat_raum`, `switch.ogbad_handtuch_2`).
- Dashboard: Kachel-Text "Ventil offen ohne Bedarf" statt "(Lauf/Bypass)".

## Monitoring (optional) 1.0.1 - 2026-11-16

### Geändert
- Dashboard: Die Chips "Lauf" und "Freigabe" sind reine Statusanzeigen und lassen sich nicht mehr per Tipp umschalten. Die Chips mit Sensorwerten und die Mindestdurchfluss-Kacheln öffnen die Detailansicht statt zu schalten. Nur "Sync" schaltet weiterhin um.

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
