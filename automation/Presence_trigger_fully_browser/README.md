# presence_trigger_fully_browser

Home-Assistant-Blueprint, der das Display eines Wallterminals (z. B. Tablet/Panel mit Fully Kiosk Browser und Display-Schalter) einschaltet, sobald ein Präsenzsensor Anwesenheit meldet, und es wach hält, solange die Präsenz anhält.

[![Blueprint in Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fjubie25%2Fblueprints%2Fblob%2Fmain%2Fautomation%2FPresence_trigger_fully_browser%2Fpresence_trigger_fully_browser.yaml)

## Funktionsweise

1. Der Präsenzsensor wechselt von `aus` auf `an`.
2. Beim Start des Ablaufs wird der Display-Schalter ausgeschaltet, kurz gewartet und wieder eingeschaltet (Reset des Displays). Über eine Auswahlliste lässt sich das ändern: nur ein- oder nur ausschalten oder den Display-Schalter gar nicht anfassen (siehe „Display beim Start des Ablaufs“).
3. Solange der Präsenzsensor `an` ist, wird in Zyklen der Button „Bewegung/Aktivität auslösen“ mehrfach gedrückt, damit das Terminal nicht in den Standby geht.
4. Sobald keine Präsenz mehr erkannt wird, endet die Schleife. Das Ausschalten des Displays übernimmt das Terminal selbst (z. B. per Timeout).

Der Modus ist `single` (mit `max_exceeded: silent`): Ein erneuter Trigger, während der Ablauf noch läuft, startet ihn nicht neu. So gibt es keinen erneuten Aus/Ein-Zyklus am Display und kein Flackern. Das Display wird währenddessen weiterhin periodisch getriggert. Wird die Präsenz zwischendurch kurz unterbrochen und kommt innerhalb der Wartezeit zwischen zwei Zyklen zurück, läuft die Schleife einfach weiter.

## Voraussetzungen

- Home Assistant **2024.10.0** oder neuer
- Ein `binary_sensor` als Präsenzsensor
- Ein `switch` zum Ein-/Ausschalten des Displays
- Ein `button`, der am Terminal Aktivität auslöst

## Eingaben

### Entitäten

| Eingabe | Typ | Beschreibung |
|---|---|---|
| Präsenzsensor | `binary_sensor` | Meldet Anwesenheit (`on` = Präsenz) |
| Display-Schalter | `switch` | Schaltet das Display ein/aus |
| Button „Bewegung/Aktivität auslösen“ | `button` | Hält den Bildschirm wach |

### Display beim Start des Ablaufs (optional, eingeklappt)

Eine Auswahlliste „Verhalten zu Beginn“ (Standard: Display-Reset):

| Auswahl | Ergebnis |
|---|---|
| Display-Reset (Aus, Pause, Ein) | Aus, Pause, Ein (bisheriges Verhalten) |
| Nur einschalten | Display-Schalter wird eingeschaltet, ohne Pause |
| Nur ausschalten | Display-Schalter wird ausgeschaltet, ohne Pause |
| Display-Schalter nicht verändern | Der Display-Schalter bleibt unberührt, nur der Aktivitäts-Button wird periodisch gedrückt |

Der Display-Schalter bleibt dabei trotzdem eine Pflichteingabe.

### Zeiten & Wiederholungen (optional, eingeklappt)

| Eingabe | Standard | Beschreibung |
|---|---|---|
| Pause zwischen Aus und Ein | 300 ms | Wartezeit beim Display-Reset (nur beim Display-Reset) |
| Anzahl Button-Betätigungen je Zyklus | 2 | Drücke pro Zyklus |
| Pause zwischen Button-Betätigungen | 2 s | Abstand der Drücke |
| Wartezeit zwischen den Zyklen | 51 s | Sollte kleiner als der Display-Timeout des Terminals sein |

## Installation

**Per Import-Button:** Badge oben anklicken und den Import bestätigen.

**Manuell:**
1. Datei `presence_trigger_fully_browser.yaml` nach
   `config/blueprints/automation/jubie25/` kopieren.
2. In Home Assistant: *Einstellungen → Automationen & Szenen → Blueprints* → ggf. neu laden.

## Verwendung

*Einstellungen → Automationen & Szenen → Blueprints → „presence_trigger_fully_browser“ → Automation erstellen.*
Entitäten auswählen, der Automation einen eigenen Namen geben (z. B. „EGEZ Wallterminal an bei Präsenz“) und speichern. Für jedes weitere Terminal einfach eine weitere Automation aus dem Blueprint anlegen.

## Versionierung

Der Blueprint folgt [Semantic Versioning](https://semver.org/lang/de/). Die Version steht in der Blueprint-Beschreibung und im [CHANGELOG](CHANGELOG.md). Sie ist bewusst **nicht** Teil des Blueprint-Namens oder des Dateinamens, damit sich Automationen, Entitäten und Namen bei Updates nicht ändern.

## Lizenz

Lizenz nach Wahl ergänzen (z. B. MIT).
