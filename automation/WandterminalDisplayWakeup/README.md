# Wandterminal – Display-Wakeup bei Präsenz

**Version:** 1.0.1

Hält das Display eines Wandterminals (Fully Browser) an, solange sich Personen im Raum aufhalten. Der Blueprint löst bei erkannter Präsenz sofort und danach periodisch eine Entität aus, z. B. den Motion-Trigger des Fully Browsers. Bleibt der Trigger aus, läuft im Fully Browser der eigene Timeout an und das Display wird nach der dortigen Wartezeit abgeschaltet.

## Funktionsweise

- **Initialer Trigger:** Sobald der Präsenzsensor auf `on` wechselt, wird die Trigger-Entität sofort ausgelöst.
- **Periodischer Trigger:** Ein Zeitmuster-Trigger (`time_pattern`) wacht im gewählten Intervall kurz auf und löst die Entität aus, wenn der Präsenzsensor noch `on` ist.
- **Keine Dauerschleife:** Es läuft kein Automations-Run im Hintergrund. Nach einem Neustart von Home Assistant arbeitet der Blueprint ohne Zusatzmaßnahmen sofort korrekt weiter, weil der Sensorzustand die Grundlage ist.

## Eingaben

| Eingabe | Beschreibung |
|---|---|
| Präsenzsensor | `binary_sensor`, aktiv (`on`) bei Anwesenheit |
| Trigger-Entität | `button`, `input_button`, `script` oder `scene`. Buttons werden gedrückt, Skripte und Szenen gestartet |
| Trigger-Intervall | 5, 10, 12, 15, 20, 30 oder 60 Sekunden (Standard: 30) |

Das Intervall ist auf Teiler von 60 beschränkt, weil das Zeitmuster an festen Sekunden der Minute feuert. Ein Wert wie 50 Sekunden würde ein ungleichmäßiges Raster ergeben (:00, :50, :00, ...).

Der Intervallabstand sollte deutlich unter dem Timeout des Fully Browsers liegen, damit das Display zuverlässig anbleibt.

## Einrichtung

1. Datei `wandterminal_display_wakeup.yaml` nach `config/blueprints/automation/<autor>/` kopieren.
2. In Home Assistant unter *Einstellungen → Automatisierungen & Szenen → Blueprints* den Blueprint prüfen und eine Automation daraus erstellen.
3. Pro Wandterminal eine eigene Automation mit dem jeweiligen Präsenzsensor und der Trigger-Entität anlegen.

## Hinweise

- Existiert für den Motion-Trigger des Fully Browsers keine Entität, lässt sich der Aufruf über ein Skript kapseln (z. B. mit `rest_command` gegen die Fully-REST-Schnittstelle) und dieses Skript als Trigger-Entität wählen.
- Der Blueprint-Name, der Dateiname und alle Entity-IDs enthalten bewusst keine Versionsnummer, damit sie sich bei Updates nicht ändern. Die Version steht nur in Beschreibung, Header-Kommentar, README und CHANGELOG.
