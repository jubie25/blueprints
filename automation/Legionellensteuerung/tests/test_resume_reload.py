"""Integrationstests mit der echten Automations-Komponente.

Der Blueprint wird als Automation geladen. Geprüft wird, wie er nach dem Neuladen der
Automationen (Ereignis automation_reloaded) reagiert, abhängig vom Wert des Prozess-Speichers.
Der HA-Neustart (Trigger homeassistant/start) nutzt denselben Zweig (id: resume).
"""
import asyncio
import logging
import os
import shutil
from datetime import timedelta

import yaml
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_mock_service

from common import BLUEPRINT, SENTINEL, fmt

INPUTS = {
    "speicher": "sensor.ww",
    "heizstab": "switch.heater",
    "heizstab_leistung": "sensor.heater_power",
    "flag_start": "input_datetime.flag",
    "startzeit": "03:00:00",
    "wochentag": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
    # Meldung wird als Logbuch-Eintrag mitgeschrieben, damit der Text prüfbar ist
    "benachrichtigung": [
        {"action": "logbook.log",
         "data": {"name": "NOTIFY", "message": "{{ titel }} | {{ nachricht }}"}}
    ],
}


async def _aufbau(hass, flag_wert, heizstab, extra=None):
    """Blueprint ablegen, Helfer und Automation anlegen. Gibt (aus, an, logbuch) zurück."""
    os.makedirs(hass.config.path("blueprints/automation/test"), exist_ok=True)
    shutil.copy(BLUEPRINT, hass.config.path("blueprints/automation/test/legionella.yaml"))

    assert await async_setup_component(
        hass, "input_datetime", {"input_datetime": {"flag": {"has_date": True, "has_time": True}}})
    await hass.async_block_till_done()
    await hass.services.async_call(
        "input_datetime", "set_datetime",
        {"entity_id": "input_datetime.flag", "datetime": flag_wert}, blocking=True)

    hass.states.async_set("sensor.ww", "41.4")
    hass.states.async_set("sensor.heater_power", "2000" if heizstab == "on" else "0")
    hass.states.async_set("switch.heater", heizstab)
    aus = async_mock_service(hass, "switch", "turn_off")
    an = async_mock_service(hass, "switch", "turn_on")
    logbuch = async_mock_service(hass, "logbook", "log")

    automation = {"id": "legionella1", "alias": "legionella",
                  "use_blueprint": {"path": "test/legionella.yaml", "input": INPUTS}}
    alle = [automation] + (extra or [])
    # automation.reload liest die Konfiguration von der Platte, wie bei einer echten Instanz
    with open(hass.config.path("configuration.yaml"), "w") as f:
        yaml.safe_dump({"input_datetime": {"flag": {"has_date": True, "has_time": True}},
                        "automation": alle}, f, allow_unicode=True)
    assert await async_setup_component(hass, "automation", {"automation": alle})
    await hass.async_block_till_done()
    assert hass.states.get("automation.legionella") is not None
    return aus, an, logbuch


async def _abbrechen(hass):
    await hass.services.async_call(
        "automation", "turn_off",
        {"entity_id": "automation.legionella", "stop_actions": True}, blocking=True)


async def test_verwaister_vorgang_wird_beim_neuladen_zurueckgesetzt(hass):
    aus, an, logbuch = await _aufbau(hass, fmt(dt_util.now() - timedelta(days=1)), "on")
    assert aus == [] and an == [], "beim Anlegen darf nichts passieren"

    await hass.services.async_call("automation", "reload", {}, blocking=True)
    await hass.async_block_till_done()

    assert len(aus) == 1, "Heizstab muss ausgeschaltet werden"
    assert hass.states.get("input_datetime.flag").state.startswith("1970-01-01")
    texte = [c.data["message"] for c in logbuch]
    assert any("Verwaister Vorgang" in t for t in texte), texte
    assert any(t.startswith("Legionellenschaltung |") and "nicht abgeschlossen" in t for t in texte), texte


async def test_neuladen_nur_dieser_automation_per_id(hass):
    aus, an, logbuch = await _aufbau(hass, fmt(dt_util.now() - timedelta(days=1)), "on")
    await hass.services.async_call("automation", "reload", {"id": "legionella1"}, blocking=True)
    await hass.async_block_till_done()
    assert len(aus) == 1
    assert hass.states.get("input_datetime.flag").state.startswith("1970-01-01")


async def test_geschlossener_vorgang_wird_nicht_angefasst(hass):
    aus, an, logbuch = await _aufbau(hass, SENTINEL, "on")
    await hass.services.async_call("automation", "reload", {}, blocking=True)
    await hass.async_block_till_done()
    assert aus == [] and an == [] and logbuch == [], (aus, an, [c.data for c in logbuch])
    assert hass.states.get("switch.heater").state == "on"


async def test_vorgang_von_heute_wird_fortgesetzt(hass):
    aus, an, logbuch = await _aufbau(hass, fmt(dt_util.now() - timedelta(minutes=30)), "on")
    await hass.services.async_call("automation", "reload", {}, blocking=True)
    # nicht async_block_till_done: der fortgesetzte Lauf wartet in Phase 2 auf den Heizstab
    await asyncio.sleep(0.5)
    assert aus == [], "darf nicht abgeschaltet werden"
    assert not hass.states.get("input_datetime.flag").state.startswith("1970-01-01")
    assert hass.states.get("automation.legionella").attributes.get("current") == 1, "Lauf soll aktiv sein"
    await _abbrechen(hass)


async def test_neuladen_einer_fremden_automation_stoert_nicht(hass, caplog):
    fremd = {"id": "fremd1", "alias": "fremd",
             "triggers": [{"trigger": "event", "event_type": "nie"}], "actions": []}
    aus, an, logbuch = await _aufbau(hass, fmt(dt_util.now() - timedelta(minutes=30)), "on", extra=[fremd])
    await hass.services.async_call("automation", "reload", {}, blocking=True)
    await asyncio.sleep(0.5)
    assert hass.states.get("automation.legionella").attributes.get("current") == 1

    caplog.clear()
    caplog.set_level(logging.DEBUG)
    await hass.services.async_call("automation", "reload", {"id": "fremd1"}, blocking=True)
    await asyncio.sleep(0.5)

    assert hass.states.get("automation.legionella").attributes.get("current") == 1, "Lauf darf nicht gestört werden"
    assert aus == [], "Heizstab darf nicht angefasst werden"
    warnungen = [r.getMessage() for r in caplog.records
                 if r.levelno >= logging.WARNING and "legionella" in r.name.lower()]
    assert warnungen == [], f"keine Log-Warnungen erwartet: {warnungen}"
    await _abbrechen(hass)
