"""tools/catalogue.py: the config list and the command lines it builds (no simulation)."""
from tools import catalogue as C
from planet.tectonics import Params
from dataclasses import fields


def test_twelve_configs_with_known_levers_and_unique_seeds():
    known = {f.name for f in fields(Params)}
    assert [c["nn"] for c in C.CONFIGS] == [f"{k:02d}" for k in range(1, 13)]
    assert len({c["seed"] for c in C.CONFIGS}) == 12
    for c in C.CONFIGS:
        assert set(c["set"]) <= known
        assert c["what"] and c["risk"]


def test_pick_ranges_and_set_args_parse_as_planet_does():
    assert [c["nn"] for c in C.pick("01-03,07")] == ["01", "02", "03", "07"]
    import json
    for c in C.CONFIGS:
        for kv in C.set_args(c):
            k, v = kv.split("=", 1)
            try:
                got = json.loads(v)
            except json.JSONDecodeError:
                got = v
            assert got == c["set"][k]
    assert C.name_of(C.CONFIGS[0], 1) == "Catalogue 1-01"


def test_time_block_parse():
    t = "\tElapsed (wall clock) time (h:mm:ss or m:ss): 8:30.62\n\tMaximum resident set size (kbytes): 12946048\n"
    assert C._time_of(t) == {"wall": "8:30.62", "peak_gb": 12.3}
