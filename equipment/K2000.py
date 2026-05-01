from equipment._voltmeter import Voltmeter
from pymeasure.instruments.keithley import Keithley2000
from util.setupmanager import SetupManager
from typing import Union
from util.errors import DeviceNotFoundError, BadConfigError

class K2000(Voltmeter):

    def __init__(self, config_id: str = "K2000") -> None:
        self.setupManager = SetupManager()
        self.config = self.setupManager.get_config()[config_id]
        self._read_config()
        self.device: Keithley2000 = self._get_device()
        self.device.reset()
        self._configure_device()

    def _read_config(self):
        self.device_id = self.config['device_id']
        self.timeout = self.config['timeout']
        self.measurement_mode = self.config['measurement_mode']
        self.range = self.config["range"]
        self.trigger_count = self.config["trigger_count"]
        self.nplc = self.config['nplc']

    def _get_device(self) -> Keithley2000:
        device: Union[Keithley2000, None] = None
        try:
            device = Keithley2000(self.device_id, timeout=self.timeout)
            self.setupManager.log_info(device.name)
        except Exception as e:
            self.setupManager.log_warning(f"Failed to load GPIB library. Continuing without GPIB support.") 
        if device == None:
            self.setupManager.log_error('Could not locate a voltmeter device.') 
            raise DeviceNotFoundError('Voltmeter')
        return device
    
    def _configure_device(self):
        self.device.voltage_range = self.range
        self.device.trigger_count = self.trigger_count

        if self.measurement_mode == 'voltage':
            self.device.voltage_nplc = self.nplc
        elif self.measurement_mode == 'current':
            self.device.current_nplc = self.nplc
        else:
            raise BadConfigError(f"(Voltmeter) {self.measurement_mode} is not supported by this script.")
        self.device.mode = self.measurement_mode

    def measure_voltage(self):
        if self.measurement_mode != 'voltage':
            self.setupManager.log_warning(f"(Voltmeter) Cannot measure voltage when in {self.measurement_mode} mode.")
            return None
        else:
            self.device.measure_voltage(max_voltage=1)
            return self.device.voltage
    
    def measure_current(self):
        if self.measurement_mode != "current":
            self.setupManager.log_warning(f"(Voltmeter) Cannot measure current when in {self.measurement_mode} mode.")
            return None
        else:
            self.device.measure_current()
            return self.device.current
        
    def shutdown(self):
        self.device.shutdown()
        self.setupManager.log_info("(Voltmeter) Shutdown.")
            