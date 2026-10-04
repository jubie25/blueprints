"""Gemeinsame Pfade und Hilfsfunktionen der Tests."""
import os
from pathlib import Path

# Der Blueprint liegt im Elternordner von tests/. Mit LEGIONELLA_BLUEPRINT lässt sich ein
# anderer Pfad angeben, z. B. um eine ältere Version zu prüfen.
BLUEPRINT = Path(
    os.environ.get(
        "LEGIONELLA_BLUEPRINT",
        Path(__file__).resolve().parents[1] / "legionella_heater_control.yaml",
    )
)
CHANGELOG = BLUEPRINT.parent / "CHANGELOG.md"

SENTINEL = "1970-01-01 00:00:00"


def fmt(dt) -> str:
    """Zeitstempel im Format des input_datetime-Helfers."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")
