# Tests

Automatisierte Tests für den Blueprint. Sie führen die Aktionen des Blueprints in einer **echten
Home-Assistant-Engine** aus, nicht gegen Attrappen. Damit lässt sich prüfen, ob eine Änderung etwas
kaputt macht, ohne auf den nächsten Wärmepumpenlauf zu warten.

## Voraussetzungen

- **Python 3.14** (aktuelle Home-Assistant-Versionen verlangen es)
- Linux (so getestet)

Das Testpaket bringt die passende Home-Assistant-Version und pytest selbst mit.

## Einrichten

Im Ordner des Blueprints (dem Elternordner von `tests/`):

```bash
uv venv --python 3.14 .venv        # oder: python3.14 -m venv .venv
. .venv/bin/activate
uv pip install -r tests/requirements.txt   # oder: pip install -r tests/requirements.txt
```

## Ausführen

```bash
pytest tests -m "not slow"   # 12 Tests in etwa 3 Sekunden
pytest tests                 # alle 24 Tests in etwa 2 bis 3 Minuten
```

Die Tests suchen `legionella_heater_control.yaml` im Elternordner von `tests/`. Mit
`LEGIONELLA_BLUEPRINT=/pfad/zur/datei.yaml pytest tests` lässt sich eine andere Datei prüfen,
zum Beispiel eine ältere Version.

## Was geprüft wird

| Datei | Anzahl | Inhalt |
|---|---|---|
| `test_blueprint_konsistenz.py` | 7 | Gültig nach dem HA-Blueprint-Schema; jede Eingabe ist definiert und wird benutzt; die Version steht in Beschreibung, `blueprint_version` und `CHANGELOG.md` gleich; **der Blueprint-Name enthält keine Versionsnummer** (daraus entstehen Entitätsnamen); das Changelog steht nicht in der Beschreibung; Mindestversion; Neustart und Neuladen lösen denselben Zweig aus |
| `test_resume_reload.py` | 5 | **Echte Automations-Komponente.** Verhalten beim Neuladen der Automationen: verwaister Vorgang (Heizstab aus, Helfer zurück, Meldung), Neuladen per ID, geschlossener Vorgang (nichts wird angefasst), Vorgang von heute (wird fortgesetzt), Neuladen einer fremden Automation (keine Störung, keine Log-Warnung) |
| `test_ablauflogik.py` | 12 | **Script-Engine mit simulierter Temperaturkurve** (als `slow` markiert). Normalfall mit der Stabil-Zeit als Dictionary, Teil-Dictionary, Text und Zahl; kompletter Lauf bis zum Abschluss; warmer Start mit langer Abkühlung; Sensor beim Start nicht verfügbar; kurzer Ausschlag ohne Wärmepumpenlauf; Stabil-Zeit 0; Fortsetzen in Phase 1 und Phase 2; die bekannte Einschränkung |

## Wie die Ablauflogik-Tests arbeiten

Der Blueprint wird mit Home Assistants eigenem Blueprint-Mechanismus eingelesen, die Eingaben werden
eingesetzt, und die Aktionen laufen unverändert. Nur die Zeit ist gerafft: Prüfintervall 0,5 s,
Stabil-Zeit 3 s. Eine Simulation gibt die Speichertemperatur in 0,5-Sekunden-Schritten vor, der
Heizstab ist ein Mock-Schalter. Geprüft wird jeweils, **wann** der Heizstab eingeschaltet wird, im
Verhältnis zum simulierten Ende des Wärmepumpenlaufs.

Die Tests zu den drei Fehlern, die in der Praxis aufgetreten sind, schlagen bei der fehlerhaften
Version 1.4.0 an. Aufruf zur Gegenprobe:

```bash
LEGIONELLA_BLUEPRINT=/pfad/zur/v1.4.0.yaml pytest tests/test_ablauflogik.py -k "warmer_start or ausschlag"
```

## Grenzen

- Die Tests prüfen die **Logik** gegen die Home-Assistant-Engine. Echte Sensoren und Geräte gehören
  nicht dazu. Reale Temperaturkurven können von den simulierten abweichen.
- Die Zeitfenster in `test_ablauflogik.py` haben Toleranzen. Wackelt ein Test auf einem sehr
  langsamen Rechner, die Grenzen oder `TICK` vergrößern.
- Mit einem neuen Home-Assistant-Release die Tests erneut laufen lassen:
  `pip install -U pytest-homeassistant-custom-component`.

## Beim Ändern des Blueprints

1. Version in der Beschreibung und in `blueprint_version` hochzählen (**nicht** im Blueprint-Namen) und einen Eintrag in
   `CHANGELOG.md` ergänzen. `test_version_steht_ueberall_gleich` meldet, wenn etwas vergessen wurde.
2. Für jeden behobenen Fehler einen Test ergänzen, der **vorher fehlschlägt**.
3. `pytest tests` ausführen.
