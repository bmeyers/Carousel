"""
PV power performance simulation
"""

from carousel.core.outputs import Output


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