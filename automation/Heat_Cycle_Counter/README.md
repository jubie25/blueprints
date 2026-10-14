# Wärmepumpe – Heizzyklenzähler (HT/NT, pro Tag)

Home-Assistant-Blueprint, der die **Heizzyklen einer Wärmepumpe** zählt und dabei zwischen **Haupttarif (HT)** und **Nebentarif (NT)** unterscheidet. Gezählt wird pro Tag, die Tageszähler werden zur Rückstellzeit (Standard Mitternacht) auf 0 gesetzt.

[![Blueprint in Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fjubie25%2Fblueprints%2Fmain%2Fautomation%2FHeat_Cycle_Counter%2Fheat_cycle_counter.yaml)

Aktuelle Version: **1.0.0** · Änderungen: [CHANGELOG.md](CHANGELOG.md)

## Funktionsumfang

- Erkennung von Beginn und Ende eines Zyklus über einen **Leistungssensor** (Schwellen mit Hysterese, jeweils mit Verzögerung).
- Getrennte Zähler für **HT** und **NT**.
- Ein Zyklus wird **bei Beginn** gezählt und dem Tarif zugeordnet, der in diesem Moment aktiv ist. Läuft er über einen HT/NT-Wechsel hinweg, bleibt er **ein** Zyklus im Tarif des Starts.
- Optionale **Vortag-Zähler**: kurz vor Mitternacht wird der Tagesendstand hineingeschrieben. Sie liefern also einen Wert pro Tag und keine kumulierende Summe.
- Alle Sensoren, Helfer, Schwellen und Zeiten sind in der Blueprint-Maske einstellbar, nichts ist fest verdrahtet.
- Robust gegen Neustarts: Der Zyklus-Merker ist ein Helfer und bleibt erhalten.

## Voraussetzungen

- Home Assistant **2024.10** oder neuer.
- Ein Leistungssensor der Wärmepumpe (`sensor`, Geräteklasse `power`, Einheit W).
- Ein `binary_sensor`, der den Tarif liefert: **`on` = HT, `off` = NT**.

## Installation

1. Blueprint importieren: den Import-Button oben verwenden oder unter *Einstellungen → Automatisierungen & Szenen → Blueprints → Blueprint importieren* diese URL einfügen:
   `https://raw.githubusercontent.com/jubie25/blueprints/main/automation/Heat_Cycle_Counter/heat_cycle_counter.yaml`
   Alternativ `heat_cycle_counter.yaml` nach `config/blueprints/automation/<ordner>/` kopieren.
2. Helfer anlegen (siehe unten).
3. Automation aus dem Blueprint erstellen und in der Maske ausfüllen.

## Benötigte Helfer

Anlegen unter *Einstellungen → Geräte & Dienste → Helfer → Helfer hinzufügen*.

| Zweck | Typ | Hinweis |
|---|---|---|
| Tageszähler HT | Zähler (`counter`) | Startwert 0, Schrittweite 1 |
| Tageszähler NT | Zähler (`counter`) | Startwert 0, Schrittweite 1 |
| Zyklus-Merker | Schalter (`input_boolean`) | Anfangszustand aus |
| Vortag HT *(optional)* | Zähler (`counter`) | Startwert 0 |
| Vortag NT *(optional)* | Zähler (`counter`) | Startwert 0 |

Den Zähler-Helfern **keinen Maximalwert** setzen und im Zähler-Helfer **nicht** „Wiederherstellen“ abschalten.

## Eingaben in der Maske

| Eingabe | Standard | Bedeutung |
|---|---|---|
| Leistungssensor | – | Sensor, der Start und Ende erkennt |
| Tarif-Sensor | – | `on` = HT, `off` = NT |
| Zyklus-Merker | – | `input_boolean`, verhindert Doppelzählung |
| Start-Schwelle | 300 W | Leistung, die überschritten werden muss |
| Start-Verzögerung | 2 min | So lange muss sie darüber liegen |
| Ende-Schwelle | 100 W | Leistung, die unterschritten werden muss |
| Ende-Verzögerung | 5 min | So lange muss sie darunter liegen (überbrückt z. B. Abtauung) |
| Tageszähler HT / NT | – | Zähler, die pro Zyklus hochzählen |
| Vortag-Zähler HT / NT | leer | Optional, erhalten den Tagesendstand |
| Übernahmezeit | 23:59:59 | Wann der Tagesstand in die Vortag-Zähler geschrieben wird |
| Rückstellzeit | 00:00:00 | Wann die Tageszähler auf 0 gehen |

**Tipp zur Einstellung:** Ende-Schwelle kleiner oder gleich Start-Schwelle wählen. Die Schwelle so legen, dass Umwälzpumpe und Standby darunter liegen, der Verdichter aber deutlich darüber.

## Funktionsweise im Detail

- **Start:** Leistung länger als die Start-Verzögerung über der Start-Schwelle **und** Zyklus-Merker aus → Merker an, Zähler des aktuellen Tarifs +1.
- **Ende:** Leistung länger als die Ende-Verzögerung unter der Ende-Schwelle → Merker aus.
- **Übernahme (23:59:59):** Tagesstände werden per `counter.set_value` in die Vortag-Zähler kopiert.
- **Rückstellung (00:00:00):** Tageszähler werden auf 0 gesetzt.
- **Home-Assistant-Neustart:** Liegt die Leistung dann unter der Ende-Schwelle, wird ein hängender Merker gelöscht.

## Tagessummen und Langzeitstatistik

`counter`-Helfer haben keine Zustandsklasse und erzeugen **keine Langzeitstatistik**. Ihre Zustände behält der Recorder nur für `purge_keep_days` (Standard 10 Tage). Für dauerhaft abrufbare Tagessummen legst du Template-Sensoren an, die die Tageszähler spiegeln (*Helfer → Template → Sensor*):

- Zustandsvorlage: `{{ states('counter.wp_zyklen_ht_tag') | int(0) }}`
- Maßeinheit: `Zyklen`
- Zustandsklasse: `Messung`
- Verfügbarkeitsvorlage (erweitert): `{{ states('counter.wp_zyklen_ht_tag') | is_number }}`

Dasselbe für NT. Die Tagessumme ist dann das **Maximum pro Tag** in der Statistik, z. B. in der Statistik-Grafik-Karte mit `stat_types: max` und `period: day`. Die Statistik wird ab Anlage der Sensoren aufgezeichnet, nicht rückwirkend.

## Bekannte Einschränkungen

- Der Tarif wird zum Zeitpunkt nach der Start-Verzögerung bestimmt. Ein Zyklus, der kurz vor einem Tarifwechsel anläuft, kann daher dem neuen Tarif zugeschlagen werden.
- Ein Zyklus, der exakt in der Sekunde zwischen Übernahmezeit und Rückstellzeit beginnt, fehlt im Vortag-Wert, wird aber im neuen Tageszähler gezählt.
- Nach einem Neustart während eines Zyklus wird dieser nicht erneut gezählt, ein Start während des Neustarts kann verpasst werden.

## Updates

Neue Versionen stehen im [CHANGELOG](CHANGELOG.md). Zum Aktualisieren den Blueprint erneut importieren (gleiche URL, bestehende Automationen bleiben verbunden) oder die Datei `heat_cycle_counter.yaml` ersetzen. Der Blueprint-Name, der Dateiname und alle Entitäten bleiben über Versionen hinweg gleich. Bei neuen Eingaben erscheinen sie mit Standardwert in der Maske. Inkompatible Änderungen gibt es nur bei einer neuen Hauptversion und sind im CHANGELOG markiert.

## Versionierung

[Semantische Versionierung](https://semver.org/lang/de/): `HAUPT.NEBEN.PATCH`.
Die Version steht nur im Header-Kommentar und in der Beschreibung der YAML-Datei, im README und im CHANGELOG, nicht im Blueprint-Namen oder Dateinamen.

## Lizenz

<!-- Lizenz hier eintragen, z. B. MIT -->
