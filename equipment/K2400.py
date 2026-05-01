from pymeasure.instruments.keithley import Keithley2400

from util.setupmanager import SetupManager
from typing import Union
from util.errors import DeviceNotFoundError, BadConfigError

import numpy as np

class K2400():
    """
    The class wraps the methods for driving a source measurement unit (SMU)
    like the Keithley 2401 and its object representation.
    Attributes:
        setupManager (SetupManager): The setup manager for the current setup.
        config (Config): The config describing the behaviour of the SMU.
        device_id (str): The string identifying the hardware address of the SMU. Usually `GPIB0::15::INSTR`.
        timeout (int): After how long the device is timing out.
        compliance_voltage (float): The maximum voltage that is driven when in current driven mode.
        compliance_current (float): The maximum current that is driven when in voltage driven mode.
        drive_mode (str): Defines the driven mode of the SMU. Only two are available: `CURRENT_DRIVEN` and `VOLTAGE_DRIVEN`.
        device (Keithley2400): The class wrapping the behaviour of the SMU.
    """
    CURRENT = 'CURRENT_DRIVEN'
    VOLTAGE = 'VOLTAGE_DRIVEN'

    def __init__(self, config_id: str = "K2400") -> None:
        self.setupManager = SetupManager()
        self.config = self.setupManager.get_config()[config_id]
        self.device_id: str = self.config['device_id']
        self.timeout: int = self.config['timeout']
        self.compliance_voltage: float = np.min(np.abs(self.setupManager.get_voltage_range()))  
        self.compliance_current: float = np.min(np.abs(self.setupManager.get_current_range()))  
        drive_mode = self.config['drive_mode'] 
        self.device = self._get_device()
        self.device.reset()
        self.device.clear()
        if drive_mode == 'CURRENT_DRIVEN':
            self.drive_mode = self.CURRENT
            self.device.apply_current()
            self.device.measure_voltage()
        elif drive_mode == 'VOLTAGE_DRIVEN':
            self.drive_mode = self.VOLTAGE
            self.device.apply_voltage()
            self.device.measure_current()
        else:
            raise BadConfigError(f'Invalid SMU drive mode {drive_mode}. Only "CURRENT_DRIVEN and "VOLTAGE_DRIVEN" are allowed.')         

        self.device.compliance_voltage = np.min(np.abs(self.setupManager.get_voltage_range()))  
        self.device.compliance_current = np.min(np.abs(self.setupManager.get_current_range())) 
        
        self.setupManager.log_info(f" --- INSTRUMENT: SMU --- ") 
        self.setupManager.log_info(self.device.id) 
        self.setupManager.log_info(f"Compliance voltage: {self.compliance_voltage}") 
        self.setupManager.log_info(f"Compliance current: {self.compliance_current}") 
        # self.setupManager.wait_for_user_input()


        self.device.use_front_terminals()
        self.device.enable_source()
        self.device.current_nplc = 1
        self.device.voltage_nplc = 1
        self.device.source_delay = 0.05
        self.device.trigger_count = 1


    def measure_voltage(self) -> float:
        """
        Measure a single voltage.
        
        :param self: Instance of the SMU
        :return: Voltage in V
        :rtype: float
        """
        self.device.measure_voltage()
        voltage = self.device.voltage
        return voltage #type: ignore

    def measure_current(self) -> float:
        """
        Measure a single current.
        
        :param self: Instance of the SMU
        :return: Current in A
        :rtype: float
        """
        self.device.measure_current()
        current = self.device.current
        return current # type: ignore


    def set_voltage(self, voltage: float):
        """
        Ramps to a voltage until the device is shut off or gets a new instruction.
        Device has to be in voltage driven mode.
        The ramp is defined by `ramp_points` and `pause_between_set` field in the setup config.

        
        :param self: Instance of the SMU
        :param voltage: Voltage in V
        :type voltage: float
        """
        if self.drive_mode == self.VOLTAGE:
            self.device.source_voltage = voltage
        else:
            self.setupManager.log_warning("(SMU) Tried applying voltage in current driven mode.") 
        pass

    def set_current(self, current: float):
        """
        Ramps to a current until the device is shut off or gets a new instruction.
        Device has to be in current driven mode.
        The ramp is defined by `ramp_points` and `pause_between_set` field in the setup config.

        
        :param self: Instance of the SMU
        :param voltage: Current in A
        :type voltage: float
        """
        if self.drive_mode == self.CURRENT:
            self.device.source_current = current
        else:
            self.setupManager.log_warning("(SMU) Tried applying current in voltage driven mode.") 


    def is_callibrated(self, voltage: float, current: float, tolerance_voltage: float, tolerance_current: float) -> bool:
        """
        Checks if the device measures a voltage or current within provided tolerances.
        
        :param self: Instance of the SMU
        :param voltage: Voltage that the SMU currently measures.
        :type voltage: float
        :param current: Current that the SMU currently measures.
        :type current: float
        :param tolerance_voltage: The user can set a tolerance for the voltage.
        If the voltage is above this tolerance, the device is considered not calibrated.
        :type tolerance_voltage: float
        :param tolerance_current: The user can set a tolerance for the current.
        If the current is above this tolerance, the device is considered not calibrated.
        :type tolerance_current: float
        :return: Returns true if the device is callibrated,
        i.e. both current and voltage are within the provided tolerances. If not, returns false.
        :rtype: bool
        """
        if np.abs(voltage) > tolerance_voltage or np.abs(current) > tolerance_current:
            return False
        else:
            return True

    def _get_device(self) -> Keithley2400:
        """
        Function responsible connecting the measurement device based on the device id in the setup config.
        The function returns the measurement device as an object.
        
        :param self: Instance of the SMU
        :return: Instanced object of the measurement device.
        :rtype: Keithley2400
        """
        device: Union[Keithley2400, None] = None
        try:
            device = Keithley2400(self.device_id, timeout=self.timeout)
        except Exception as e:
            self.setupManager.log_warning(f"Failed to load GPIB library. Continuing without GPIB support.") 
        if device == None:
            self.setupManager.log_error('Could not locate a SMU device.') 
            raise DeviceNotFoundError('SMU')
        return device
    
    def shutdown(self):
        """
        Shutsdown the SMU.
        Ramps voltage and current to 0 and shutsdown the connecting ports of the SMU.
        The SMU itself still remains on after calling this function.
        Call this function whenever the device is not in use anymore.
        The device will maintain the last current and voltage even after execution, unless this function is called.
        
        :param self: Instance of the SMU
        """
        self.device.shutdown()
        self.setupManager.log_info("SMU shutdown.")
