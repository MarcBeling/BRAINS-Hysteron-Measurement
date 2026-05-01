from equipment._voltmeter import Voltmeter
from util.errors import DeviceNotFoundError, ModeMismatchError
from pymeasure.instruments.hp.hp34401A import HP34401A as hp #type: ignore
from util.setupmanager import SetupManager
from typing import Union
import numpy as np

class HP34401A(Voltmeter):

    def __init__(self, config_id: str = "HP34401A") -> None:
        self.setupManager = SetupManager()
        self.config = self.setupManager.get_config()[config_id]
        self._read_config()
        self.device: hp = self._get_device()
        self._configure_device()

    def _read_config(self):
        self.device_id = self.config['device_id']
        self.timeout = self.config['timeout']
        self.range = self.config["range"]
        self.trigger_count = self.config["trigger_count"]
        self.nplc = self.config['nplc']

    def _get_device(self) -> hp:
        device: Union[hp, None] = None
        try:
            device = hp(self.device_id)
            self.setupManager.log_info(device.name)
        except Exception as e:
            self.setupManager.log_warning(f"{e}") 
        if device == None:
            self.setupManager.log_error('Could not locate a voltmeter device.') 
            raise DeviceNotFoundError('Voltmeter')
        return device
    
    def _configure_device(self):
        self.device.range = self.range
        self.device.trigger_count = self.trigger_count
        self.device.nplc = self.nplc

    def measure_voltage(self) -> float:
        voltage: float = 0
        self.device.function_ = 'DCV'
        voltage = np.average(np.asarray(self.device.reading)) # type: ignore
        return voltage
    
    def measure_current(self):
        current: float = 0
        self.device.function_ = 'DCI'
        current = np.average(np.asarray(self.device.reading)) # type: ignore
        return current
        
    def shutdown(self):
        self.device.shutdown()
        self.setupManager.log_info("(Voltmeter) Shutdown.")    