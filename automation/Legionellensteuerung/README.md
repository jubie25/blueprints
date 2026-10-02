# Changelog – Warmwasser Legionellenschaltung

Blueprint: [`legionella_heater_control.yaml`](legionella_heater_control.yaml)

Die aktuelle Version steht im Blueprint-Namen, in der Beschreibung und am Ende der
Benachrichtigungen ("Blueprint vX.Y.Z"). Einträge beginnen jeweils mit der neuesten Version.
Unter "Upgrade" steht, ob in einer bestehenden Instanz Eingabefelder neu gesetzt werden müssen.

## 1.6.1 – 2026-10-02

### Geändert
- Changelog aus der Blueprint-Beschreibung in diese Datei ausgelagert; Beschreibung gekürzt und
  mit Link versehen. Keine funktionale Änderung.

**Upgrade:** keine Änderung an den Eingabefeldern.

## 1.6.0 – 2026-10-02

### Behoben
- **Heizstab startete zu früh**, noch während die Wärmepumpe lief. Höchstwert und Stabilitäts-Timer
  stammten aus der langen Wartezeit vor dem Wärmepumpenlauf (der Speicher war z. B. mittags wärmer
  und kühlte bis zum Abend ab) und galten bei Erkennung des Anstiegs sofort als "stabil". Sie zählen
  jetzt erst ab der Erkennung.
- Ein kurzer Temperaturausschlag (z. B. warmer Rücklauf nach einer Zapfung) rastete die Erkennung ein,
  sodass später ohne Wärmepumpenlauf der Heizstab gestartet werden konnte. Die Erkennung wird jetzt
  zurückgesetzt, wenn die Temperatur wieder unter das halbe Delta über den Tiefstwert fällt.
- Ein nicht lesbarer Temperatursensor (`unknown` / `unavailable`) führt nicht mehr zu Scheinwerten
  (zuvor Startwert 0, der sofort als Anstieg gewertet wurde).

### Hinzugefügt
- Logbuch-Einträge bei Erkennung des Anstiegs und beim Zurücksetzen der Erkennung.

**Upgrade:** keine Änderung an den Eingabefeldern.

## 1.5.0 – 2026-10-02

### Behoben
- Die Umrechnung der Stabil-Zeit in Sekunden versteht jetzt Dictionary, Text (`HH:MM:SS`, `MM:SS`)
  und Zahl. Zuvor wurde ein Text still zu 0 s.
- Ist die Stabil-Zeit 0 oder ungültig, wird abgebrochen und benachrichtigt, statt den Heizstab
  zu starten.

### Hinzugefügt
- Logbuch-Einträge zum Start von Phase 1 (Parameter) und zur Entscheidung vor dem Einschalten
  des Heizstabs.

### Geändert
- Mindestversion Home Assistant 2025.4 (geändertes Variablen-Scoping in verschachtelten Blöcken,
  von der Schleife in Phase 1 benötigt).

**Upgrade:** keine Änderung an den Eingabefeldern.

## 1.4.0 – 2026-09-27

### Behoben
- Ein Tages-Timeout in Phase 1 wurde als abgeschlossener Wärmepumpenlauf gewertet, sobald irgendwann
  ein Anstieg erkannt worden war, auch wenn die Stabil-Zeit nie erreicht wurde. Der Heizstab startet
  jetzt nur noch bei erreichter Stabilität.
- Startete Home Assistant neu, kurz nachdem der Heizstab eingeschaltet wurde (Leistung noch unter der
  Schwelle), schaltete die Automation ihn sofort wieder aus. Die 5-Minuten-Anlaufkulanz gilt jetzt
  auch nach einem Neustart.

**Upgrade:** keine Änderung an den Eingabefeldern.

## 1.3.0 – 2026-09-27

### Geändert
- Statusspeicher und Startzeitpunkt-Speicher zu einem einzigen `input_datetime`-Helfer
  zusammengelegt. Der gespeicherte Wert ist zugleich Status (Platzhalter `1970-01-01 00:00:00` =
  geschlossen) und echter Startzeitpunkt. Der `input_boolean` entfällt.

### Behoben
- Die Neustart-Erkennung stützte sich auf `last_changed`. Dieser Zeitstempel wird bei einem
  HA-Neustart auf den Neustart-Zeitpunkt zurückgesetzt, auch ohne Wertänderung. Jetzt wird der selbst
  gesetzte Wert ausgewertet.

**Upgrade:** Das Feld "Statusspeicher (input_boolean)" entfällt. Das Feld "Prozess-Speicher
(input_datetime)" in der Instanz neu auswählen.

## 1.2.0 – 2026-09-26

### Behoben
- Zeitmessung der Stabilitätsprüfung auf Unix-Zeitstempel umgestellt (robuster gegen
  Datentyp-Probleme bei Datum/Zeit-Vergleichen).
- Der Vergleich für "neuer Höchstwert" wurde von `>=` auf `>` korrigiert, damit ein unveränderter
  Messwert als stabil zählt.

**Upgrade:** keine Änderung an den Eingabefeldern.

## 1.1.0 – 2026-09-24

### Behoben
- `TypeError` bei der Zeitdifferenzberechnung (`now() - stabil_seit`).

**Upgrade:** keine Änderung an den Eingabefeldern.

## 1.0.0 – 2026-09-23

### Geändert
- Die Lauferkennung der Wärmepumpe wurde von der Leistungsmessung auf die Speichertemperatur
  umgestellt: Ein Anstieg um das Delta gilt als laufende Warmwasseraufheizung, das Ausbleiben neuer
  Höchstwerte über die Stabil-Zeit als deren Abschluss. Grund: Die Leistungsaufnahme der Wärmepumpe
  unterscheidet Warmwasser- und Raumheizungsbetrieb nicht.

**Upgrade:** Das Feld "Leistungssensor Wärmepumpe" entfällt. Neu sind "Temperatur-Delta",
"Prüfintervall Speichertemperatur" und "Stabil-Zeit nach letztem Höchstwert".

## Vorversion (unversioniert)

- Erste Fassung: Der Heizstab startet, nachdem die Leistung der Wärmepumpe nach dem Startzeitpunkt
  wieder unter die Leistungsschwelle (500 W) gefallen ist.
