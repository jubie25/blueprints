# Changelog

Alle wesentlichen Änderungen an diesem Blueprint. Format nach [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), Versionierung nach [SemVer](https://semver.org/lang/de/).

## Blueprint 1.3.0 - 2026-11-18

### Behoben
- Mindestpause und Höchstwartezeit zählen jetzt ab dem Ende der letzten Freigabe **oder** des letzten Laufs, je nachdem, was später war. Bisher zählte nur die Freigabe, nach einem Lauf ohne Freigabe (z. B. Warmwasser) konnte die nächste Freigabe sofort folgen.
- Der Sicherheitstakt korrigiert "Lauf aktiv" nicht mehr. Fiel ein Takt in die Ausschaltverzögerung, wurde der Lauf vorzeitig beendet (bei 5 min Takt und 60 s Verzögerung etwa jeder fünfte Lauf). Stattdessen wird "Lauf aktiv" beim Start von Home Assistant und beim Neuladen der Automatisierungen (`automation_reloaded`) aus der Leistungsmessung bestimmt.

### Hinzugefügt
- Ereignis `heat_pump_valve_sync_config` mit allen Einstellungen (beim Start, Neuladen, Umschalten von "Sync aktiv" und im Sicherheitstakt).
- Ereignis `heat_pump_valve_sync_run_end` mit `duration_min`, der Laufdauer bereinigt um Ein- und Ausschaltverzögerung.

## Monitoring (optional) 1.6.0 - 2026-11-18

### Geändert
- Package: Neuer Sensor `sensor.heat_pump_valve_sync_config` speichert die Einstellungen der Automatisierung. Status, Regler mit Bedarf, ältester Bedarf und Pause Rest lesen Helfer, Zuordnung und Mindestpause daraus. Die festen Werte `min_pause`, `on_delay`, `off_delay` und die Helfernamen in den Templates entfallen. Pause Rest zählt wie der Blueprint ab Freigabe- oder Laufende.
- Package: "Lauf Heute" nimmt die Laufdauer aus dem Ereignis `heat_pump_valve_sync_run_end` statt sie selbst zu berechnen.
- Package: Fest bleibt nur der Helfer "Lauf aktiv" in den beiden `history_stats`-Sensoren.
- Dashboard: `vsync_special_cfg` entfällt. "Ventile real" und "Mindestdurchfluss" lesen Bypass- und dauerhaft offene Ventile aus der Konfiguration, die Namen kommen aus dem Anzeigenamen der Entität. Statuskopf (Leistung) und die Chips "Lauf" und "Freigabe" lesen ebenfalls daraus.

### Hinweise
- Voraussetzung ist Blueprint 1.3.0. Bis das erste Konfigurationsereignis eintrifft, zeigen Status und Mindestdurchfluss "Warte auf Einstellungen".

## Blueprint 1.2.0 - 2026-11-17

### Hinzugefügt
- Neues Feld "Bedarfsschalter (für die Auslösung)": Eine Änderung eines Bedarfsschalters löst die Automatisierung sofort aus. **Das Feld ist Pflicht; nach dem Update dort alle Bedarfsschalter aus der Zuordnung eintragen.**
- Neues Feld "Sicherheitstakt" (1, 2, 5, 10 oder 15 Minuten, Standard 5) statt des festen Minutentakts. Er erkennt das Ablaufen von Mindestpause und Höchstwartezeit.
- `stored_traces: 50`, damit die Traces nicht mehr nach wenigen Minuten überschrieben werden.
- Der Sicherheitstakt gleicht "Lauf aktiv" mit der Leistungsmessung ab und korrigiert so einen verpassten Schwellenübergang.

### Geändert
- `continue_on_error` beim Schalten der Ventile: Ein fehlgeschlagener Schaltbefehl bricht die Automatisierung nicht mehr ab, die übrigen Ventile werden trotzdem geschaltet.

## Monitoring (optional) 1.5.0 - 2026-11-17

### Hinzugefügt
- Package: Sensor `sensor.heat_pump_valve_sync_run_today` ("WP Ventil-Sync Lauf Heute"). Er berechnet beim Laufende die Dauer jedes Laufs aus dem Helfer "Lauf aktiv" und zieht den Versatz durch Ein- und Ausschaltverzögerung ab (`off_delay - on_delay`, Standard 50 s). Zustand ist der Tagesdurchschnitt in Minuten, Attribute: `count`, `min`, `max`, `last_run`, `total`, `durations`, `day`.
- Package: Um Mitternacht (oder beim ersten Lauf eines neuen Tages) werden die Tageswerte als `yesterday_*`-Attribute übernommen und der Sensor `sensor.heat_pump_valve_sync_run_yesterday` ("WP Ventil-Sync Lauf Vortag") liefert Durchschnitt, Min, Max, Anzahl und Summe des Vortags. Beide Sensoren haben `state_class: measurement` für Langzeitstatistiken.
- Dashboard: Chips für Durchschnitt, Min und Max der Lauf-Dauer heute sowie ein Chip "Vortag".

### Hinweise
- **Einstellen:** Im Package `on_delay` und `off_delay` auf die Werte der Automatisierung setzen (Einschalt- und Ausschaltverzögerung, Standard 10 s und 60 s).
- Die Auswertung beginnt mit dem ersten Laufende nach der Einbindung. Frühere Läufe fehlen.

## Monitoring (optional) 1.4.0 - 2026-11-17

### Geändert
- Dashboard: Jede Etage und "Mindestdurchfluss" liegt in einem Container (`vertical-stack`) mit einfarbigem, durchscheinendem Hintergrund (`card-mod`). Der Ton ist halbtransparent und passt sich damit dem Day- und dem Night-Theme an. Die Kacheln selbst tragen keinen Etagenton mehr, die Kopfzeilen sind schlicht.
- Dashboard: Benötigt zusätzlich die HACS-Karte `card-mod`.

## Monitoring (optional) 1.3.1 - 2026-11-17

### Geändert
- Dashboard: Statt des Farbstreifens am Rand tragen die Kacheln einer Etage im Ruhezustand einen dezenten, einfarbigen Hintergrund in der Etagenfarbe. Die Kopfzeile der Etage ist etwas kräftiger in derselben Farbe getönt. Die Statusfarben (heizt, wartet, offen) überlagern den Etagenton unverändert.

## Monitoring (optional) 1.3.0 - 2026-11-17

### Geändert
- Dashboard: Die Etagen sind dezent gruppiert. Jede Etage hat eine Kopfzeile mit farbigem Streifen und dem Zähler "x von n mit Bedarf". Die Kacheln der Etage tragen denselben Farbstreifen am linken Rand. Auch "Mindestdurchfluss" hat eine eigene Kopfzeile.

## Monitoring (optional) 1.2.1 - 2026-11-17

### Geändert
- Dashboard: Die Legende zeigt die Kachelfarben als Farbfelder mit Kurzbeschreibung statt als Fließtext.

## Monitoring (optional) 1.2.0 - 2026-11-17

### Geändert
- Dashboard: Bypass- und dauerhaft offene Ventile stehen nur noch in einer Liste (`vsync_special_cfg` am Dateianfang). Der Abschnitt "Mindestdurchfluss" ist eine dynamische Karte, die aus dieser Liste die Kacheln baut. "Ventile real" ergänzt Ventile, die keine Raumventile sind, automatisch in einer Zeile "+" und unterstreicht Bypass- und dauerhaft offene Ventile.
- Dashboard: Die Kacheln unter "Mindestdurchfluss" öffnen beim Tippen nicht mehr die Detailansicht.

## Monitoring (optional) 1.1.1 - 2026-11-17

### Behoben
- Package und Dashboard lasen die Helfer unter den Beispielnamen `heat_pump_valve_sync_running/_release/_enabled`. In der Praxis heißen sie `bphelper_ventilsync_lauf_aktiv/_freigabe_aktiv/_sync_aktiv`, deshalb blieben Lauf, Freigabe, Starts und Laufzeit auf 0, obwohl der Blueprint korrekt arbeitete. Die Namen sind angepasst. Wer andere Helfernamen nutzt, ersetzt sie in `heat_pump_valve_sync_monitor.yaml` und `heat_pump_valve_sync_dashboard.yaml`.
- Monitor: Mindestpause auf 30 min (Wert aus der Automatisierung).

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
