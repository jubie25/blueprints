# Wallterminal-Display bei Präsenz einschalten

Home-Assistant-Blueprint, der das Display eines Wallterminals (z. B. Tablet/Panel mit Display-Schalter) einschaltet, sobald ein Präsenzsensor Anwesenheit meldet, und es wach hält, solange die Präsenz anhält.

[![Blueprint in Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2F%3CGITHUB-USER%3E%2F%3CREPOSITORY%3E%2Fblob%2Fmain%2Fpresence_wallterminal_display.yaml)

> Hinweis: `<GITHUB-USER>` und `<REPOSITORY>` im Badge-Link und in der `source_url` der Blueprint-Datei vor der Veröffentlichung ersetzen.

## Funktionsweise

1. Der Präsenzsensor wechselt von `aus` auf `an`.
2. Der Display-Schalter wird ausgeschaltet, kurz gewartet und wieder eingeschaltet (Reset des Displays).
3. Solange der Präsenzsensor `an` ist, wird in Zyklen der Button „Bewegung/Aktivität auslösen“ mehrfach gedrückt, damit das Terminal nicht in den Standby geht.
4. Sobald keine Präsenz mehr erkannt wird, endet die Schleife. Das Ausschalten des Displays übernimmt das Terminal selbst (z. B. per Timeout).

Der Modus ist `restart`: Ein erneuter Trigger startet den Ablauf neu.

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

### Zeiten & Wiederholungen (optional, eingeklappt)

| Eingabe | Standard | Beschreibung |
|---|---|---|
| Pause zwischen Aus und Ein | 300 ms | Wartezeit beim Display-Reset |
| Anzahl Button-Betätigungen je Zyklus | 2 | Drücke pro Zyklus |
| Pause zwischen Button-Betätigungen | 2 s | Abstand der Drücke |
| Wartezeit zwischen den Zyklen | 51 s | Sollte kleiner als der Display-Timeout des Terminals sein |

## Installation

**Per Import-Button:** Badge oben anklicken und den Import bestätigen.

**Manuell:**
1. Datei `presence_wallterminal_display.yaml` nach
   `config/blueprints/automation/<GITHUB-USER>/` kopieren.
2. In Home Assistant: *Einstellungen → Automationen & Szenen → Blueprints* → ggf. neu laden.

## Verwendung

*Einstellungen → Automationen & Szenen → Blueprints → „Wallterminal-Display bei Präsenz einschalten“ → Automation erstellen.*
Entitäten auswählen, der Automation einen eigenen Namen geben (z. B. „EGEZ Wallterminal an bei Präsenz“) und speichern. Für jedes weitere Terminal einfach eine weitere Automation aus dem Blueprint anlegen.

## Versionierung

Der Blueprint folgt [Semantic Versioning](https://semver.org/lang/de/). Die Version steht in der Blueprint-Beschreibung und im [CHANGELOG](CHANGELOG.md). Sie ist bewusst **nicht** Teil des Blueprint-Namens oder des Dateinamens, damit sich Automationen, Entitäten und Namen bei Updates nicht ändern.

## Lizenz

Lizenz nach Wahl ergänzen (z. B. MIT).
