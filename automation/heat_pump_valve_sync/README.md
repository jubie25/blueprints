# Wärmepumpe – Ventil-Synchronisation (Sammeln & Freigeben)

**Version 1.2.0** · Home Assistant Blueprint (Automation)

Eine Wärmepumpe ohne Leistungsmodulation, die in der Übergangszeit mit kleinem Puffer und kleiner Heizlast betrieben wird, taktet: Der Puffer ist in Minuten voll, der Verdichter schaltet ab. Dieser Blueprint nutzt den Estrich als zusätzlichen Puffer. Er sammelt den Wärmebedarf der Räume und öffnet die Ventile aller Räume mit Bedarf **gemeinsam**, solange die Wärmepumpe läuft. Die Last steigt, die Läufe werden länger, und die Pausen dazwischen auch.

## Wie es funktioniert

1. Jeder Raumregler (z. B. Generic Thermostat) schaltet nicht mehr das echte Ventil, sondern einen virtuellen Schalter. Dessen Zustand ist der **Bedarf** des Raums. Da der Generic Thermostat als Heizer nur `switch`-Entitäten zulässt, ist das ein Template-Schalter als Adapter vor einem `input_boolean`.
2. Der Blueprint erkennt anhand einer Leistungsmessung, ob die Wärmepumpe läuft.
3. **Freigabe:** Wenn mindestens *N* Räume Bedarf haben (oder der älteste Bedarf die *Höchstwartezeit* erreicht) und seit der letzten Freigabe die *Mindestpause* vergangen ist, werden die Ventile aller Räume mit Bedarf geöffnet. Der Puffer entleert sich, die Wärmepumpe startet.
4. Läuft die Wärmepumpe, bleiben alle Ventile mit Bedarf offen. Dazu öffnen die **Bypass-Ventile** (z. B. das Bad) für den Mindestdurchfluss. **Dauerhaft offene Ventile** (z. B. ein Handtuchheizkörper ohne eigenen Regler) bleiben offen, solange "Sync aktiv" an ist. Ist es aus, fasst der Blueprint Bypass- und dauerhaft offene Ventile nicht an, sie können manuell bedient werden.
5. Mit dem Laufende endet die Freigabe, die Ventile schließen. Der Bedarf bleibt in den virtuellen Schaltern erhalten, bis der Raumregler ihn selbst beendet.

Die Ventile werden bei jeder Änderung eines Bedarfsschalters, bei Laufstart und Laufende sowie im einstellbaren Sicherheitstakt (Standard 5 Minuten) abgeglichen. Nur Ventile, deren Istzustand vom Sollzustand abweicht, werden geschaltet, mit einer kleinen Pause dazwischen.

## Voraussetzungen

- Home Assistant 2024.10 oder neuer.
- Pro Regler (Heizer) ein `input_boolean` als Bedarf und ein Template-Schalter als Adapter. Der Adapter wird als Heizer des Reglers eingetragen, der `input_boolean` in der Zuordnung des Blueprints.
- Echte Ventile als `switch` (`an` = offen, sonst "Ventile invertiert" aktivieren).
- Drei Helfer (`input_boolean`): *Lauf aktiv*, *Freigabe aktiv*, *Sync aktiv*. Eine fertige Vorlage liegt in `heat_pump_valve_sync_helpers.yaml`.
- Eine Leistungsmessung der Wärmepumpe in Watt.

## Einrichtung

1. **Helfer anlegen:** Inhalt von `heat_pump_valve_sync_helpers.yaml` als Package einbinden und für jeden Regler einen Bedarfsschalter plus Adapter-Schalter ergänzen.
2. **Raumregler umstellen:** Bei jedem Generic Thermostat den Heizer vom echten Ventil auf den eigenen Adapter-Schalter (`switch.<regler>_heater_adapter`) ändern. In die Zuordnung des Blueprints kommt dagegen der `input_boolean` (`demand`).
3. **Blueprint importieren** und eine Automatisierung daraus erstellen.
4. **Zuordnung eintragen** (siehe unten), dieselben Bedarfsschalter noch einmal in der Liste "Bedarfsschalter (für die Auslösung)" auswählen, Leistungsmessung und die drei Helfer auswählen.
5. **Zuerst mit "Sync aktiv" = aus starten.** Die Ventile folgen dann direkt dem Bedarf. Prüfe, ob alle Ventile wie erwartet schalten, erst dann "Sync aktiv" einschalten.

### Beispiel für die Zuordnung

```yaml
- demand: input_boolean.egwz_fenster_heat_demand
  valves: switch.egwz_heizventil_fenster
- demand: input_boolean.egwz_tuer_heat_demand
  valves: switch.egwz_heizventil_tuer
- demand: input_boolean.egkueche_heat_demand
  valves: switch.egkueche_heizventil
```

`demand` und `valves` dürfen je ein einzelner Eintrag oder eine Liste sein. Ein Ventil darf in mehreren Einträgen vorkommen. Es öffnet, sobald irgendein zugehöriger Bedarf besteht.

## Parameter

| Parameter | Standard | Bedeutung |
|---|---|---|
| Schwelle "Wärmepumpe läuft" | 500 W | Leistung, ab der ein Lauf erkannt wird |
| Einschaltverzögerung | 60 s | So lange muss die Leistung darüber liegen |
| Ausschaltverzögerung | 120 s | So lange muss sie darunter liegen |
| Mindestanzahl Räume | 2 | Freigabe ab so vielen Räumen mit Bedarf |
| Mindestpause zwischen Freigaben | 45 min | Hauptstellschraube für die Zahl der Starts |
| Höchstwartezeit | 60 min | Freigabe auch bei weniger Räumen nach dieser Zeit |
| Höchstdauer einer Freigabe | 180 min | Schutz, falls kein Lauf folgt |
| Höchstdauer "Lauf aktiv" | 4 h | Schutz vor hängendem Helfer |
| Sicherheitstakt | 5 min | Zeitgesteuerter Abgleich für Pausen-Ablauf und verpasste Ereignisse |
| Pause zwischen Schaltvorgängen | 100 ms | Abstand beim Schalten mehrerer Ventile |

**Tuning:** Zu viele Starts: *Mindestpause* erhöhen. Räume bleiben zu kalt: *Mindestpause* und *Höchstwartezeit* verkleinern. Beobachte Starts pro Tag, Laufzeit pro Start und die Raumtemperaturen, jeweils bei vergleichbarem Wetter.

## Grenzen und Sicherheit

- **Notfall-Rückbau:** Wird die Automatisierung deaktiviert oder gelöscht, bleiben die Ventile im letzten Zustand stehen, und die Räume bekommen keine Wärme mehr, weil der Bedarf nur noch in den virtuellen Schaltern liegt. Dann bei den Raumreglern den Heizer wieder auf das echte Ventil umstellen.
- **Ein Adapter, ein Regler:** Ein Adapter darf immer nur von **einem** Regler geschaltet werden. Zwei Regler auf demselben Adapter überschreiben sich gegenseitig, z. B. bei Neustart oder `keep_alive`: Der Regler ohne Bedarf setzt den Bedarf des anderen wieder zurück. Räume mit mehreren Reglern bekommen deshalb pro Regler einen eigenen Bedarfsschalter und Adapter. Die Zuordnung darf mehrere `demand`-Einträge für dasselbe Ventil enthalten (ODER-Verknüpfung).
- **Mindestdurchfluss:** Mindestens ein Bypass-Ventil oder dauerhaft offenes Ventil sollte eingetragen sein, sonst fehlt der Wärmepumpe bei geschlossenen Ventilen der Durchfluss. Ventile öffnen thermisch mit Verzögerung (ca. 3 Minuten). Der Bypass öffnet deshalb schon bei der Freigabe.
- **Anlaufstrom:** Durch das gemeinsame Öffnen schalten regelmäßig viele thermische Antriebe gleichzeitig. Prüfe Absicherung, Netzteil bzw. Trafo und Relaismodule auf den Anlaufstrom aller Antriebe.
- **Auflösung:** Bedarfsänderungen lösen sofort aus, sofern der Schalter in der Liste "Bedarfsschalter (für die Auslösung)" steht. Der Ablauf von Mindestpause und Höchstwartezeit wird im Sicherheitstakt erkannt, also bis zu so viele Minuten später, wie dort eingestellt sind.
- **Traces:** Der Blueprint speichert 50 Traces statt der Standardwerte. Dank der Auslösung per Ereignis füllen sie sich nicht mehr im Minutentakt.
- **Fehlerhafte Schaltbefehle:** Schlägt das Schalten eines Ventils fehl, werden die übrigen Ventile trotzdem geschaltet. Das Ventil wird beim nächsten Abgleich erneut versucht.
- **Neustart von Home Assistant:** Die Wartezeiten beginnen danach von vorn. "Lauf aktiv" wird beim Start anhand der Leistungsmessung neu bestimmt.
- **Warmwasser:** Heiz- und Warmwasserläufe werden nicht unterschieden. Bei einem reinen Warmwasserlauf öffnen die Ventile ohne Wirkung. Nach dem Lauf folgt die nächste Freigabe nach der Mindestpause.
- Der Blueprint ersetzt keine Schutzfunktionen der Wärmepumpe.

## Fehlersuche

- **Ventile schalten nicht:** *Sync aktiv* prüfen und in den Automatisierungs-Traces nachsehen, ob die Zuordnung (YAML) korrekt gelesen wird. Ventile mit Zustand `unavailable` werden übersprungen.
- **Ventile öffnen/schließen invertiert:** "Ventile invertiert" umschalten.
- **Neuer Bedarf wird erst spät erkannt:** Prüfen, ob der Bedarfsschalter in der Liste "Bedarfsschalter (für die Auslösung)" steht.
- **Freigabe kommt nie:** Mindestpause und Höchstwartezeit prüfen, ebenso, ob die Bedarfsschalter tatsächlich vom Raumregler geschaltet werden.
- **Lauf wird nicht erkannt:** Schwelle und Leistungsmessung prüfen. Der Helfer *Lauf aktiv* sollte beim Verdichterlauf nach der Einschaltverzögerung auf `an` gehen.

## Monitoring (optional)

Zwei zusätzliche Dateien zeigen den Zustand des Systems übersichtlich an. Sie ändern am Blueprint nichts und lesen nur vorhandene Helfer, Bedarfsschalter, Ventile und Climates.

- `heat_pump_valve_sync_monitor.yaml` (Package): Template-Sensoren für Status-Text, Anzahl Regler mit Bedarf, Alter des ältesten Bedarfs und Restzeit der Mindestpause, dazu Starts und Laufzeit seit Mitternacht (`history_stats`). **Einstellen:** Im Sensor "Pause Rest" den Wert `min_pause` auf die Mindestpause aus dem Blueprint setzen.
- `heat_pump_valve_sync_dashboard.yaml` (Dashboard): Statuskopf, Chips (Sync, Lauf, Freigabe, Bedarf, Pause, Starts, Laufzeit) und je Etage ein Raster mit einer Kachel pro Regler (Raumtemperatur Ist/Soll, Zustand: heizt, wartet auf Freigabe, Ventil offen, ruht) sowie eine Zeile für die Mindestdurchfluss-Ventile. Benötigt die HACS-Karten `mushroom` und `button-card`. Den Inhalt im Raw-Konfigurationseditor eines neuen Dashboards einfügen.
- Die Climates müssen dem Schema `climate.<raum>_thermostat[_fenster|_tuer|_zkino]` folgen, und die Leistungsmessung heißt im Dashboard `sensor.klima_waermepumpe_power`. Beides lässt sich in der Datei anpassen.
- Die Entity-IDs der beiden `history_stats`-Sensoren leiten sich aus dem Namen ab (`sensor.wp_ventil_sync_starts_heute`, `sensor.wp_ventil_sync_laufzeit_heute`). Weichen sie bei dir ab, im Dashboard anpassen.

## Dateien

- `heat_pump_valve_sync.yaml`: der Blueprint
- `heat_pump_valve_sync_helpers.yaml`: Vorlage für die Helfer (Bedarfsschalter und Adapter)
- `heat_pump_valve_sync_rooms.yaml`: Beispiel für eine vollständige Zuordnung (ein konkretes Haus)
- `heat_pump_valve_sync_monitor.yaml`: Monitoring-Package (optional)
- `heat_pump_valve_sync_dashboard.yaml`: Dashboard-Ansicht (optional)
- `CHANGELOG.md`: Änderungshistorie
