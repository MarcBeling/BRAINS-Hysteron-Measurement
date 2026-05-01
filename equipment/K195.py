from equipment._voltmeter import Voltmeter
from util.setupmanager import SetupManager
from typing import Any
from util.errors import DeviceNotFoundError
import instruments as ik
import pyvisa
import time

class K195(Voltmeter):

    def __init__(self, config_id: str = "K195") -> None:
        self.setupManager = SetupManager()
        self.config = self.setupManager.get_config()[config_id]
        self.rm = pyvisa.ResourceManager(r'C:\\Windows\\System32\\visa64.dll')  # force NI-VISA backend
        print(self.rm.list_resources())
        self._read_config()
        self.device: ik.keithley.Keithley195 = self._get_device()
        self._configure_device()

    def _read_config(self):
        self.device_id = self.config['device_id']
        self.measurement_mode = self.config['measurement_mode']
        self.range = self.config["range"]
        self.timeout = self.config["timeout"]

    def _get_device(self) -> Any:
        device = None
        try:
            device = self.rm.open_resource("GPIB1::11::INSTR")
            device.timeout = self.timeout

            self.setupManager.log_info("Keithley 195 found.")
        except Exception as e:
            self.setupManager.log_warning(f"{e}") 
        if device == None:
            self.setupManager.log_error('Could not locate a voltmeter device.') 
            raise DeviceNotFoundError('Voltmeter')
        return device
    
    def _configure_device(self):

        self.device.write('YX')       # remove CR/LF termination (195-side)
        self.device.write('G1DX')     # no prefix/suffix in readings

        if self.measurement_mode == 'voltage':
            self.device.write('F0DX') 
        elif self.measurement_mode == 'current':
            self.device.write('F3DX') 
        elif self.measurement_mode == 'voltage ac':
            self.device.write('F1DX') 
        elif self.measurement_mode == 'current ac':
            self.device.write('F4DX') 
        else:
            self.setupManager.log_warning(f"(K195) The {self.measurement_mode} mode is not supported.")
        time.sleep(2.0) 
        self.device.write('R0DX')     # range: auto (R1..R6 for fixed ranges in DCV)
        self.device.write('T1X')      # trigger mode: talk one-shot         

    def measure_voltage(self):
        if self.measurement_mode != 'voltage':
            self.setupManager.log_warning(f"(K195) Cannot measure voltage when in {self.measurement_mode} mode.")
            return None
        else:
            self.device.assert_trigger()
            voltage = float(self.device.read())
            return voltage
    
    def measure_current(self):
        if self.measurement_mode != "current":
            self.setupManager.log_warning(f"(K195) Cannot measure current when in {self.measurement_mode} mode.")
            return None
        else:
            self.device.assert_trigger()
            current = float(self.device.read())
            return current
        
    def shutdown(self):
        self.setupManager.log_info("(K195) Shutdown.")
