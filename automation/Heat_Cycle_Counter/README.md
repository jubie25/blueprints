# Wärmepumpe – Heizzyklenzähler (HT/NT)

Home-Assistant-Blueprint, der die **Heizzyklen einer Wärmepumpe** zählt und dabei zwischen **Haupttarif (HT)** und **Nebentarif (NT)** unterscheidet. Es gibt zwei Zählarten, die einzeln oder gemeinsam genutzt werden können:

- **Tageszähler:** werden zur Rückstellzeit (Standard Mitternacht) auf 0 gesetzt.
- **Gesamtzähler:** zählen dauerhaft hoch und werden nie zurückgesetzt. Damit lassen sich beliebige Zeiträume summieren, z. B. über die Datumsauswahl des Energie-Dashboards.

[![Blueprint in Home Assistant importieren](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fjubie25%2Fblueprints%2Fmain%2Fautomation%2FHeat_Cycle_Counter%2Fheat_cycle_counter.yaml)

Aktuelle Version: **1.1.0** · Änderungen: [CHANGELOG.md](CHANGELOG.md)

## Funktionsumfang

- Erkennung von Beginn und Ende eines Zyklus über einen **Leistungssensor** (Schwellen mit Hysterese, jeweils mit Verzögerung).
- Getrennte Zähler für **HT** und **NT**.
- Ein Zyklus wird **bei Beginn** gezählt und dem Tarif zugeordnet, der in diesem Moment aktiv ist. Läuft er über einen HT/NT-Wechsel hinweg, bleibt er **ein** Zyklus im Tarif des Starts.
- **Tageszähler** (optional) mit täglicher Rückstellung und optionalen **Vortag-Zählern**: kurz vor Mitternacht wird der Tagesendstand hineingeschrieben. Sie liefern also einen Wert pro Tag und keine kumulierende Summe.
- **Gesamtzähler** (optional) ohne Rückstellung als Grundlage für Langzeitstatistik und frei wählbare Zeiträume.
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

Anlegen unter *Einstellungen → Geräte & Dienste → Helfer → Helfer hinzufügen*. Die Zähler lassen sich auch direkt im Auswahlfeld der Maske über „Neuen Helfer anlegen“ erstellen.

| Zweck | Typ | Pflicht? | Hinweis |
|---|---|---|---|
| Zyklus-Merker | Schalter (`input_boolean`) | ja | Anfangszustand aus |
| Tageszähler HT / NT | Zähler (`counter`) | optional | Startwert 0, Schrittweite 1 |
| Gesamtzähler HT / NT | Zähler (`counter`) | optional | Startwert 0, Schrittweite 1 |
| Vortag HT / NT | Zähler (`counter`) | optional | Startwert 0, setzt Tageszähler voraus |

**Mindestens ein Zählerpaar (HT und NT) muss gesetzt sein**, entweder Tages- oder Gesamtzähler oder beide. Den Zähler-Helfern **keinen Maximalwert** setzen und „Wiederherstellen“ nicht abschalten.

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
| Tageszähler HT / NT | leer | Optional, wird zur Rückstellzeit auf 0 gesetzt |
| Gesamtzähler HT / NT | leer | Optional, wird nie zurückgesetzt |
| Vortag-Zähler HT / NT | leer | Optional, erhalten den Tagesendstand des Tageszählers |
| Übernahmezeit | 23:59:59 | Wann der Tagesstand in die Vortag-Zähler geschrieben wird |
| Rückstellzeit | 00:00:00 | Wann die Tageszähler auf 0 gehen |

**Tipp zur Einstellung:** Ende-Schwelle kleiner oder gleich Start-Schwelle wählen. Die Schwelle so legen, dass Umwälzpumpe und Standby darunter liegen, der Verdichter aber deutlich darüber.

## Funktionsweise im Detail

- **Start:** Leistung länger als die Start-Verzögerung über der Start-Schwelle **und** Zyklus-Merker aus → Merker an, Tages- und Gesamtzähler des aktuellen Tarifs +1.
- **Ende:** Leistung länger als die Ende-Verzögerung unter der Ende-Schwelle → Merker aus.
- **Übernahme (23:59:59):** Tageszähler-Stände werden per `counter.set_value` in die Vortag-Zähler kopiert.
- **Rückstellung (00:00:00):** Nur die Tageszähler werden auf 0 gesetzt. Gesamtzähler bleiben unberührt.
- **Home-Assistant-Neustart:** Liegt die Leistung dann unter der Ende-Schwelle, wird ein hängender Merker gelöscht.

## Langzeitstatistik und frei wählbare Zeiträume

`counter`-Helfer haben keine Zustandsklasse und erzeugen **keine Langzeitstatistik**. Ihre Zustände behält der Recorder nur für `purge_keep_days` (Standard 10 Tage). Ein Blueprint kann außerdem keine Sensorwerte setzen. Deshalb gibt es einen kleinen Umweg: Ein Template-Sensor spiegelt den **Gesamtzähler** und erhält die Zustandsklasse `total_increasing`. Dafür erstellt Home Assistant dauerhaft stündliche Statistiken, und die Datumsauswahl des Energie-Dashboards kann darüber beliebige Zeiträume summieren.

### 1. Template-Sensor anlegen

*Helfer → Helfer hinzufügen → Template → Sensor*, je einmal für HT und NT:

- Name: z. B. `WP Zyklen HT gesamt`
- Zustandsvorlage: `{{ states('counter.wp_zyklen_ht_gesamt') | int }}`
- Maßeinheit: z. B. `Zyklen` (frei vergebene Einheit, ohne Umrechnung; einmal festlegen und beibehalten)
- Zustandsklasse: `Gesamt, ansteigend` (`total_increasing`)
- Geräteklasse: leer lassen
- **Verfügbarkeitsvorlage** (erweiterte Optionen, wichtig): `{{ states('counter.wp_zyklen_ht_gesamt') | is_number }}`

Die Verfügbarkeitsvorlage ist bei `total_increasing` Pflicht. Fällt der Wert kurz auf 0 (z. B. `unknown` nach einem Neustart), wertet Home Assistant das als Zählerrücksetzung und würde beim nächsten gültigen Wert einen großen Sprung addieren. Mit der Vorlage bleibt der Sensor dann `unavailable` und wird ignoriert. Deshalb hier bewusst **kein** `int(0)`.

Die Entity-IDs der Zähler sind Beispiele und müssen angepasst werden. Die Statistik wird ab Anlage der Sensoren aufgezeichnet, nicht rückwirkend.

### 2. Dashboard mit Datumsauswahl

```yaml
type: energy-date-selection
```

```yaml
type: statistics-graph
title: Heizzyklen
entities:
  - sensor.wp_zyklen_ht_gesamt
  - sensor.wp_zyklen_nt_gesamt
stat_types:
  - change
chart_type: bar
period: day
energy_date_selection: true
```

Summe über den gewählten Zeitraum als Einzelwert:

```yaml
type: statistic
entity: sensor.wp_zyklen_ht_gesamt
stat_type: change
period: energy_date_selection
```

Die Karten folgen dem Zeitraum der Datumsauswahl auf derselben Ansicht. Bei mehreren Datumsauswahlen kann man über `collection_key` zuordnen.

### Tageszähler und Vortag-Zähler

Wer nur den aktuellen Tageswert oder den Vortag braucht, kommt ohne Template-Sensor aus. Für eine dauerhaft abrufbare Tagesstatistik reicht aber der Gesamtzähler mit `change` und `period: day`.

## Bekannte Einschränkungen

- Der Tarif wird zum Zeitpunkt nach der Start-Verzögerung bestimmt. Ein Zyklus, der kurz vor einem Tarifwechsel anläuft, kann daher dem neuen Tarif zugeschlagen werden.
- Ein Zyklus, der exakt in der Sekunde zwischen Übernahmezeit und Rückstellzeit beginnt, fehlt im Vortag-Wert, wird aber im neuen Tageszähler gezählt.
- Nach einem Neustart während eines Zyklus wird dieser nicht erneut gezählt, ein Start während des Neustarts kann verpasst werden.
- Setzt man den Gesamtzähler von Hand zurück oder verringert ihn, behandelt Home Assistant das beim Template-Sensor als Rücksetzung.

## Updates

Neue Versionen stehen im [CHANGELOG](CHANGELOG.md). Zum Aktualisieren den Blueprint erneut importieren (gleiche URL, bestehende Automationen bleiben verbunden) oder die Datei `heat_cycle_counter.yaml` ersetzen. Der Blueprint-Name, der Dateiname und alle Entitäten bleiben über Versionen hinweg gleich. Bei neuen Eingaben erscheinen sie mit Standardwert in der Maske. Inkompatible Änderungen gibt es nur bei einer neuen Hauptversion und sind im CHANGELOG markiert.

## Versionierung

[Semantische Versionierung](https://semver.org/lang/de/): `HAUPT.NEBEN.PATCH`.
Die Version steht nur im Header-Kommentar und in der Beschreibung der YAML-Datei, im README und im CHANGELOG, nicht im Blueprint-Namen oder Dateinamen.

## Lizenz

<!-- Lizenz hier eintragen, z. B. MIT -->
