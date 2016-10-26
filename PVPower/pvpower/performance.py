"""
PV power performance simulation
"""

from carousel.core.outputs import Output
from carousel.core.calculations import Calc
from carousel.core.formulas import Formula
from carousel.core.data_sources import DataSource
from carousel.core.simulations import Simulation
from carousel.core.models import Model
from carousel.core import UREG
from datetime import datetime
import pvlib
PROJ_PATH = '/Users/bennetmeyers/Devel/carousel/Carousel/PVPower'


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


class UtilityFormulas(Formula):
    """
    Formulas for PV Power demo
    """
    module = ".utils"
    package = "formulas"
    formulas = {
        "f_energy": {
            "args": ["ac_power", "times"],
            "units": [["watt_hour", None], ["W", None]]
        },
        "f_rollup": {
            "args": ["items", "times", "freq"],
            "units": ["=A", ["=A", None, None]]
        }
    }


class PVPowerData(DataSource):
    """
    Data sources for PV Power demo.
    """
    latitude = {"units": "degrees", "uncertainty": 1.0}
    longitude = {"units": "degrees", "uncertainty": 1.0}
    elevation = {"units": "meters", "uncertainty": 1.0}
    timestamp_start = {}
    timestamp_count = {}
    module = {}
    inverter = {}
    module_database = {}
    inverter_database = {}
    Tamb = {"units": "degC", "uncertainty": 1.0}
    Uwind = {"units": "m/s", "uncertainty": 1.0}
    surface_azimuth = {"units": "degrees", "uncertainty": 1.0}
    timezone = {}

    def __prepare_data__(self):
        # set frequencies
        for k in ('HOURLY', 'MONTHLY', 'YEARLY'):
            self.data[k] = k
            self.isconstant[k] = True
        # apply metadata
        for k, v in self.parameters.iteritems():
            # TODO: this should be applied in data reader using _meta_names from
            # data registry which should use a meta class and all parameter
            # files should have same layout even xlrd and numpy readers, etc.
            self.isconstant[k] = True  # set all data "isconstant" True
            # uncertainty is dictionary
            if 'uncertainty' in v:
                self.uncertainty[k] = {k: v['uncertainty'] * UREG.percent}
        # convert initial timestamp to datetime
        self.data['timestamp_start'] = datetime(*self.data['timestamp_start'])
        # get module and inverter databases
        self.data['module_database'] = pvlib.pvsystem.retrieve_sam(
            self.data['module_database'], path=SANDIA_MODULES
        )
        self.data['inverter_database'] = pvlib.pvsystem.retrieve_sam(
            self.data['inverter_database'], path=CEC_INVERTERS
        )
        # get module and inverter
        self.data['module'] = self.data['module_database'][self.data['module']]
        self.data['inverter'] = (
            self.data['inverter_database'][self.data['inverter']]
        )


class PVPowerSim(Simulation):
    """
    PV Power Demo Simulations
    """
    ID = "Tuscon_SAPM"
    path = "~/Carousel_Simulations"
    thresholds = None
    interval = [1, "hour"]
    sim_length = [0, "hours"]
    write_frequency = 0
    write_fields = {
        "data": ["latitude", "longitude", "Tamb", "Uwind"],
        "outputs": [
            "monthly_energy", "annual_energy"
        ]
    }
    display_frequency = 12
    display_fields = {
        "data": ["latitude", "longitude", "Tamb", "Uwind"],
        "outputs": [
            "monthly_energy", "annual_energy"
        ]
    }
    commands = ['start', 'pause', 'run', 'load']


class NewSAPM(Model):
    """
    PV Power Demo model
    """
    modelpath = PROJ_PATH  # folder containing project, not model
    data = [PVPowerData]
    outputs = [PVPowerOutputs, PerformanceOutputs, IrradianceOutputs]
    formulas = [UtilityFormulas, PerformanceFormulas, IrradianceFormulas]
    calculations = [UtilityCalcs, PerformanceCalcs, IrradianceCalcs]
    simulations = [PVPowerSim]
