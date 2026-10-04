"""Gemeinsame Test-Einstellungen."""
import pytest


@pytest.fixture
def expected_lingering_timers() -> bool:
    # Der Blueprint plant einen Zeit-Trigger (Startzeit); das Test-Framework soll das
    # beim Aufräumen nicht als Fehler werten.
    return True


@pytest.fixture
def expected_lingering_tasks() -> bool:
    return True
