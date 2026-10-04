"""Statische Prüfungen der Blueprint-Datei und der Versionierung (laufen in Sekunden)."""
import re

import yaml
from homeassistant.components.blueprint import schemas
from homeassistant.util import yaml as hayaml

from common import BLUEPRINT, CHANGELOG


class _Loader(yaml.SafeLoader):
    pass


_Loader.add_constructor("!input", lambda loader, node: {"__input__": loader.construct_scalar(node)})


def _laden():
    return yaml.load(BLUEPRINT.read_text(encoding="utf-8"), _Loader)


def test_blueprint_entspricht_dem_ha_schema():
    daten = hayaml.load_yaml(str(BLUEPRINT))
    schemas.BLUEPRINT_SCHEMA(daten)


def test_alle_inputs_sind_definiert_und_werden_genutzt():
    daten = _laden()
    definiert = {k for sektion in daten["blueprint"]["input"].values() for k in sektion["input"]}
    genutzt = set()

    def gehe(x):
        if isinstance(x, dict):
            if "__input__" in x:
                genutzt.add(x["__input__"])
                return
            for v in x.values():
                gehe(v)
        elif isinstance(x, list):
            for v in x:
                gehe(v)

    gehe({k: v for k, v in daten.items() if k != "blueprint"})
    assert definiert - genutzt == set(), f"definiert, aber nie benutzt: {definiert - genutzt}"
    assert genutzt - definiert == set(), f"benutzt, aber nicht definiert: {genutzt - definiert}"


def test_version_steht_ueberall_gleich():
    daten = _laden()
    version = str(daten["variables"]["blueprint_version"])
    assert re.fullmatch(r"\d+\.\d+\.\d+", version), version
    assert f"(v{version})" in daten["blueprint"]["name"]
    assert daten["blueprint"]["description"].startswith(f"**Version: {version} ")
    ersteszeile = re.search(r"^## (\d+\.\d+\.\d+)", CHANGELOG.read_text(encoding="utf-8"), re.M)
    assert ersteszeile and ersteszeile.group(1) == version, (
        f"CHANGELOG.md beginnt mit {ersteszeile and ersteszeile.group(1)}, Blueprint ist {version}"
    )


def test_changelog_ist_ausgelagert():
    beschreibung = _laden()["blueprint"]["description"]
    assert "CHANGELOG.md" in beschreibung
    assert "Änderungshistorie:" not in beschreibung


def test_mindestversion_ist_mindestens_2025_4():
    mv = _laden()["blueprint"]["homeassistant"]["min_version"]
    teile = tuple(int(x) for x in str(mv).split("."))
    assert teile >= (2025, 4, 0), mv


def test_neustart_und_neuladen_loesen_denselben_zweig_aus():
    daten = _laden()
    ids = {(t["trigger"], t.get("event") or t.get("event_type")): t["id"]
           for t in daten["triggers"] if t["trigger"] != "time"}
    assert ids[("homeassistant", "start")] == "resume"
    assert ids[("event", "automation_reloaded")] == "resume"
    assert daten.get("max_exceeded") == "silent"
