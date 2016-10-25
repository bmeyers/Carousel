"""
PV power performance simulation
"""

from carousel.core.outputs import Output
from carousel.core.calculations import Calc


class PVPowerOutputs(Output):
    """
    Outputs for PV Power demo
    """
    timestamps = {"isconstant": True, "size": 8761}
    hourly_energy = {
        "isconstant": True, "timeseries": "hourly_timeseries",
        "units": "W*h",
        "size": 8760
    }
    hourly_timeseries = {"isconstant": True, "units": "W*h", "size": 8760}
    monthly_energy = {"isconstant": True, "units": "W*h", "size": 12}
    annual_energy = {"isconstant": True, "units": "W*h"}


class UtilityCalcs(Calc):
    """
    Calculations for PV Power demo
    """
    dependencies = ["PerformanceCalcs"]
    static = [
        {
            "formula": "f_energy",
            "args": {
                "outputs": {"ac_power": "Pac", "times": "timestamps"}
            },
            "returns": ["hourly_energy", "hourly_timeseries"]
        },
        {
            "formula": "f_rollup",
            "args": {
                "data": {"freq": "MONTHLY"},
                "outputs": {"items": "hourly_energy",
                            "times": "hourly_timeseries"}
            },
            "returns": ["monthly_energy"]
        },
        {
            "formula": "f_rollup",
            "args": {
                "data": {"freq": "YEARLY"},
                "outputs": {"items": "hourly_energy",
                            "times": "hourly_timeseries"}
            },
            "returns": ["annual_energy"]
        },
        {
            "formula": "f_encapsulant_browning",
            "args": {
                "data": {"encapsulant": "encapsulant"},
                "outputs": {
                    "prev_encapsulant_browning": ["encapsulant_browning", -1],
                    "prev_day_cell_temp": ["Tcell", -1, "day"]
                }
            },
            "returns": ["encapsulant_browning"]
        }
    ]
