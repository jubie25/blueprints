# Changelog

Alle Änderungen an diesem Blueprint. Das Format folgt [Keep a Changelog](https://keepachangelog.com/de/1.1.0/), die Versionierung [SemVer](https://semver.org/lang/de/).

## [1.0.1] - 2026-10-18

### Behoben
- Fehlermeldung „invalid time_pattern value at 'seconds'": Das Intervall wird jetzt direkt als Wert an den `time_pattern`-Trigger übergeben statt über ein Template. Das Verhalten und die Auswahlwerte bleiben unverändert.

## [1.0.0] - 2026-10-18

### Hinzugefügt
- Erstveröffentlichung
- Initialer Trigger beim Erkennen der Präsenz
- Periodischer Trigger per `time_pattern` mit Zustandsbedingung auf den Präsenzsensor
- Konfigurierbar: Präsenzsensor, Trigger-Entität (button, input_button, script, scene) und Intervall (Teiler von 60 Sekunden)
