"""Ablauflogik des Blueprints in der echten Script-Engine von Home Assistant.

Die Aktionen des Blueprints laufen unverändert. Nur die Eingaben werden substituiert, und die Zeit
ist gerafft: Prüfintervall 0,5 s, Stabil-Zeit 3 s. Die Speichertemperatur wird von einer
Simulation in 0,5-s-Schritten vorgegeben, der Heizstab ist ein Mock-Schalter.

Alle Tests sind als "slow" markiert (zusammen etwa 2 bis 3 Minuten).
"""
import asyncio
import time
from datetime import timedelta

import pytest
from homeassistant.components.blueprint import models, schemas
from homeassistant.core import Context
from homeassistant.helpers import config_validation as cv, script as ha_script
from homeassistant.util import dt as dt_util, yaml as hayaml

from common import BLUEPRINT, SENTINEL, fmt

pytestmark = pytest.mark.slow

TICK = 0.5  # Sekunden pro Simulationsschritt (= Prüfintervall)

BASIS_EINGABEN = {
    "speicher": "sensor.ww",
    "heizstab": "switch.heater",
    "heizstab_leistung": "sensor.heater_power",
    "flag_start": "input_datetime.flag",
    "startzeit": "17:30:00",
    "wochentag": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
    "ww_delta_start": 0.8,
    "ww_pruef_intervall": {"hours": 0, "minutes": 0, "seconds": TICK},
    "ww_stabil_zeit": {"hours": 0, "minutes": 0, "seconds": 3},
    "hs_start_schwelle": 100,
    "hs_ende_schwelle": 10,
    "hs_ende_zeit": {"hours": 0, "minutes": 0, "seconds": 1},
    "hs_max_dauer": {"hours": 0, "minutes": 0, "seconds": 15},
    "ziel_temp": 60,
    "benachrichtigung": [],
}

# Startwert des Temperatursensors je Szenario (Standard 41,4)
STARTWERT = {"stale": "45.375", "unavail": "unavailable", "flat43": "43.8"}


class Sim:
    """Mock-Umgebung: zeichnet Dienstaufrufe mit Zeitstempel auf und simuliert Sensor und Heizstab."""

    def __init__(self, hass, heizstab="off", flag=SENTINEL, regelung_nach=None):
        self.hass = hass
        self.heizstab = heizstab
        self.flag = flag
        self.regelung_nach = regelung_nach  # Sekunden, nach denen die Heizstab-Regelung abschaltet
        self.calls = []
        self.marks = {}
        self.tasks = []
        self.t0 = time.monotonic()

    def jetzt(self):
        return time.monotonic() - self.t0

    def mark(self, name):
        self.marks[name] = self.jetzt()

    def erstes(self, name):
        for t, n, _ in self.calls:
            if n == name:
                return t
        return None

    def aufrufe(self, name):
        return [(t, d) for t, n, d in self.calls if n == name]

    async def _dienst(self, call):
        h = self.hass
        self.calls.append((self.jetzt(), f"{call.domain}.{call.service}", dict(call.data)))
        if call.domain == "switch" and call.service == "turn_on":
            h.states.async_set("switch.heater", "on")

            async def anlauf():
                await asyncio.sleep(TICK)
                h.states.async_set("sensor.heater_power", "2000")

            self.tasks.append(asyncio.create_task(anlauf()))
        elif call.domain == "switch" and call.service == "turn_off":
            h.states.async_set("switch.heater", "off")
            h.states.async_set("sensor.heater_power", "0")
        elif call.domain == "input_datetime":
            h.states.async_set("input_datetime.flag", call.data["datetime"])

    def vorbereiten(self, szenario):
        h = self.hass
        for domain, dienst in [("switch", "turn_on"), ("switch", "turn_off"),
                               ("input_datetime", "set_datetime"), ("logbook", "log")]:
            h.services.async_register(domain, dienst, self._dienst)
        h.states.async_set("sensor.ww", STARTWERT.get(szenario, "41.4"))
        h.states.async_set("switch.heater", self.heizstab)
        h.states.async_set("sensor.heater_power", "2000" if self.heizstab == "on" else "0")
        h.states.async_set("input_datetime.flag", self.flag)

    async def szenario(self, name):
        h = self.hass
        t = 41.4

        def setze(v):
            h.states.async_set("sensor.ww", str(v))

        if name == "flat43":  # Wärmepumpenlauf ist schon vorbei: Temperatur bleibt flach
            await asyncio.sleep(120)
            return
        if name == "stale":  # warmer Start, kurzer Höchstwert, Abkühlung, flach, dann Wärmepumpenlauf
            await asyncio.sleep(TICK)
            setze("45.4375")
            v = 45.4375
            while v > 41.4:
                await asyncio.sleep(TICK)
                v = max(41.4, round(v - 0.5, 4))
                setze(v)
            await asyncio.sleep(7 * TICK)
        elif name == "blip":  # nur ein kurzer Ausschlag (warmer Rücklauf), KEIN Wärmepumpenlauf
            await asyncio.sleep(3 * TICK)
            for v in (42.4, 42.4, 41.8, 41.6, 41.4):
                setze(v)
                await asyncio.sleep(TICK)
            self.mark("ausschlag_vorbei")
            await asyncio.sleep(120)
            return
        elif name == "unavail":  # Sensor beim Start nicht verfügbar
            await asyncio.sleep(3 * TICK)
            setze(41.4)
            await asyncio.sleep(4 * TICK)
        else:  # plain: flach, dann Wärmepumpenlauf
            await asyncio.sleep(4 * TICK)

        self.mark("wp_start")
        for _ in range(12):
            t = round(t + 0.2, 1)
            setze(t)
            await asyncio.sleep(TICK)
        self.mark("wp_ende")  # Plateau beginnt
        while True:  # danach heizt nur noch der Heizstab, bis seine Regelung abschaltet
            await asyncio.sleep(TICK)
            if h.states.get("switch.heater").state == "on":
                t = round(t + 0.1, 1)
                setze(t)
                if t >= 45.0:
                    h.states.async_set("sensor.heater_power", "0")
                    return

    async def regelung(self):
        if self.regelung_nach is not None:
            await asyncio.sleep(self.regelung_nach)
            self.hass.states.async_set("sensor.heater_power", "0")
            self.mark("regelung_aus")


def _konfiguration(ueberschreibungen):
    daten = hayaml.load_yaml(str(BLUEPRINT))
    bp = models.Blueprint(daten, expected_domain="automation", path="x.yaml",
                          schema=schemas.BLUEPRINT_SCHEMA)
    eingaben = {**BASIS_EINGABEN, **(ueberschreibungen or {})}
    return models.BlueprintInputs(
        bp, {"use_blueprint": {"path": "x.yaml", "input": eingaben}}).async_substitute()


async def ausfuehren(hass, sim, szenario, ausloeser="start", ueberschreibungen=None,
                     bis=None, timeout=40):
    """Führt die Blueprint-Aktionen aus, bis `bis(sim)` wahr wird, der Lauf endet oder `timeout` abläuft."""
    cfg = _konfiguration(ueberschreibungen)
    sequenz = await ha_script.async_validate_actions_config(hass, cv.SCRIPT_SCHEMA(cfg["actions"]))
    skript = ha_script.Script(hass, sequenz, "test", "automation",
                              variables=cv.SCRIPT_VARIABLES_SCHEMA(cfg["variables"]))
    sim.vorbereiten(szenario)
    sim.t0 = time.monotonic()
    sim.tasks.append(asyncio.create_task(sim.szenario(szenario)))
    sim.tasks.append(asyncio.create_task(sim.regelung()))
    lauf = hass.async_create_task(
        skript.async_run({"trigger": {"id": ausloeser, "platform": "time"}}, Context()))
    try:
        while not lauf.done() and sim.jetzt() < timeout and not (bis and bis(sim)):
            await asyncio.sleep(0.05)
        beendet = lauf.done()
        if not beendet:
            await skript.async_stop()
        await asyncio.gather(lauf, return_exceptions=True)
    finally:
        for task in sim.tasks:
            task.cancel()
        await asyncio.gather(*sim.tasks, return_exceptions=True)
    return beendet


def _heizstab_an(sim):
    return sim.erstes("switch.turn_on") is not None


def _logbuch(sim):
    return [d.get("message", "") for _, d in sim.aufrufe("logbook.log")]


# --------------------------------------------------------------------------------------
# Normalfall
# --------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "stabil",
    [{"hours": 0, "minutes": 0, "seconds": 3}, {"seconds": 3}, "00:00:03", 3],
    ids=["dictionary", "teil-dictionary", "text", "zahl"],
)
async def test_heizstab_startet_erst_nach_dem_plateau(hass, stabil):
    """Egal in welcher Form die Stabil-Zeit ankommt: Start frühestens nach Ende des Wärmepumpenlaufs."""
    sim = Sim(hass)
    await ausfuehren(hass, sim, "plain", ueberschreibungen={"ww_stabil_zeit": stabil},
                     bis=_heizstab_an, timeout=30)
    t_an = sim.erstes("switch.turn_on")
    assert t_an is not None, "Heizstab wurde nie eingeschaltet"
    ende = sim.marks["wp_ende"]
    assert ende + 2.0 <= t_an <= ende + 5.0, (
        f"Heizstab um {t_an:.1f}s, Wärmepumpenlauf endete bei {ende:.1f}s (Stabil-Zeit 3 s)")


async def test_vollstaendiger_lauf_bis_zum_abschluss(hass):
    """Start, Phase 1, Heizstab ein, Phase 2 bis zur Regelabschaltung, Heizstab aus, Helfer zurück."""
    sim = Sim(hass)
    beendet = await ausfuehren(hass, sim, "plain", timeout=45)
    assert beendet, "Lauf wurde nicht fertig"
    setzen = sim.aufrufe("input_datetime.set_datetime")
    assert setzen[0][1]["datetime"].startswith(fmt(dt_util.now())[:10]), "Start muss den heutigen Zeitpunkt setzen"
    assert setzen[-1][1]["datetime"] == SENTINEL, "Helfer muss am Ende zurückgesetzt sein"
    t_an, t_aus = sim.erstes("switch.turn_on"), sim.erstes("switch.turn_off")
    assert sim.marks["wp_ende"] < t_an < t_aus
    assert hass.states.get("switch.heater").state == "off"


# --------------------------------------------------------------------------------------
# Fehlerursachen, die in der Praxis aufgetreten sind
# --------------------------------------------------------------------------------------

async def test_warmer_start_mit_langer_abkuehlung_startet_nicht_zu_frueh(hass):
    """Regression v1.6.0: Höchstwert und Timer stammten aus der Wartezeit vor dem Wärmepumpenlauf."""
    sim = Sim(hass)
    await ausfuehren(hass, sim, "stale", bis=_heizstab_an, timeout=40)
    t_an = sim.erstes("switch.turn_on")
    assert t_an is not None
    assert t_an >= sim.marks["wp_ende"] + 2.0, (
        f"Heizstab um {t_an:.1f}s, Wärmepumpenlauf endete bei {sim.marks['wp_ende']:.1f}s")


async def test_sensor_beim_start_nicht_verfuegbar_loest_keinen_fehlalarm_aus(hass):
    sim = Sim(hass)
    await ausfuehren(hass, sim, "unavail", bis=_heizstab_an, timeout=35)
    t_an = sim.erstes("switch.turn_on")
    assert t_an is not None
    assert t_an >= sim.marks["wp_ende"] + 2.0


async def test_kurzer_ausschlag_ohne_waermepumpenlauf_startet_nichts(hass):
    """Warmer Rücklauf nach einer Zapfung: Erkennung wird zurückgesetzt, Heizstab bleibt aus."""
    sim = Sim(hass)
    await ausfuehren(hass, sim, "blip", timeout=14)
    assert not _heizstab_an(sim), "Heizstab darf nach einem bloßen Ausschlag nicht starten"
    assert any("Erkennung zurückgesetzt" in m for m in _logbuch(sim)), _logbuch(sim)


async def test_stabil_zeit_null_bricht_ab_statt_den_heizstab_zu_starten(hass):
    sim = Sim(hass)
    beendet = await ausfuehren(hass, sim, "plain",
                               ueberschreibungen={"ww_stabil_zeit": {"seconds": 0}}, timeout=10)
    assert beendet
    assert not _heizstab_an(sim)
    assert sim.aufrufe("input_datetime.set_datetime")[-1][1]["datetime"] == SENTINEL


# --------------------------------------------------------------------------------------
# Fortsetzen nach Neustart / Neuladen (Auslöser "resume", Helfer von heute)
# --------------------------------------------------------------------------------------

async def test_fortsetzen_in_phase_1_erkennt_den_folgenden_lauf(hass):
    sim = Sim(hass, flag=fmt(dt_util.now() - timedelta(minutes=30)))
    await ausfuehren(hass, sim, "plain", ausloeser="resume", bis=_heizstab_an, timeout=30)
    t_an = sim.erstes("switch.turn_on")
    assert t_an is not None
    assert t_an >= sim.marks["wp_ende"] + 2.0


async def test_fortsetzen_in_phase_2_wartet_auf_die_regelabschaltung(hass):
    sim = Sim(hass, heizstab="on", flag=fmt(dt_util.now() - timedelta(minutes=30)), regelung_nach=2.0)
    beendet = await ausfuehren(hass, sim, "flat43", ausloeser="resume", timeout=20)
    assert beendet
    assert not _heizstab_an(sim), "Heizstab läuft schon, darf nicht erneut eingeschaltet werden"
    t_aus = sim.erstes("switch.turn_off")
    assert t_aus is not None and t_aus >= sim.marks["regelung_aus"] + 0.8, (
        f"abgeschaltet bei {t_aus}, Regelung endete bei {sim.marks.get('regelung_aus')}")
    assert sim.aufrufe("input_datetime.set_datetime")[-1][1]["datetime"] == SENTINEL


async def test_bekannte_einschraenkung_beendeter_lauf_wird_nach_neustart_nicht_erkannt(hass):
    """Dokumentiert die Einschränkung aus dem README: Ist der Wärmepumpenlauf beim Neustart schon
    beendet, bleibt die Temperatur flach, es wird nichts erkannt, und der Heizstab startet nicht."""
    sim = Sim(hass, flag=fmt(dt_util.now() - timedelta(minutes=30)))
    await ausfuehren(hass, sim, "flat43", ausloeser="resume", timeout=8)
    assert not _heizstab_an(sim)
    assert not any("Aufheizung erkannt" in m for m in _logbuch(sim))
