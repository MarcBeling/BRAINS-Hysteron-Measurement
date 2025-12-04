import numpy as np
from typing import Dict, Union

from errors import NoMeasurementError, \
BadConfigError, DeviceNotFoundError
from setupmanager import SetupManager

import nidaqmx
from nidaqmx.constants import VoltageUnits, AcquisitionType
from nidaqmx.errors import DaqError
from nidaqmx.system import System

from pymeasure.instruments.keithley import Keithley2400

class SMU():
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

    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager = setupManager
        self.config = self.setupManager.get_setup_config()['smu']
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
        elif drive_mode == 'VOLTAGE_DRIVEN':
            self.drive_mode = self.VOLTAGE
            self.device.apply_voltage()
        else:
            raise BadConfigError(f'Invalid SMU drive mode {drive_mode}. Only "CURRENT_DRIVEN and "VOLTAGE_DRIVEN" are allowed.')         

        self.device.compliance_voltage = np.min(np.abs(self.setupManager.get_voltage_range()))  
        self.device.compliance_current = np.min(np.abs(self.setupManager.get_current_range())) 
        
        self.setupManager.log_info(f" --- INSTRUMENT: SMU --- ") 
        self.setupManager.log_info(self.device.id) 
        self.setupManager.log_info(f"Compliance voltage: {self.compliance_voltage}") 
        self.setupManager.log_info(f"Compliance current: {self.compliance_current}") 
        self.setupManager.wait_for_user_input()


        self.device.enable_source()

        self.device.use_front_terminals()
        self.device.current_nplc = 1
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
        if voltage != None:
            return voltage #type: ignore
        else:
            raise NoMeasurementError("SMU")

    def measure_current(self) -> float:
        """
        Measure a single current.
        
        :param self: Instance of the SMU
        :return: Current in A
        :rtype: float
        """
        self.device.measure_current()
        current = self.device.current
        if current != None:
            return current # type: ignore
        else:
            raise NoMeasurementError("SMU")


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
            self.device.ramp_to_voltage(target_voltage = voltage,
                                        steps=self.setupManager.get_setup_config()['ramp_points'],  #type: ignore
                                        pause=self.config['pause_between_set'])
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
            self.device.ramp_to_current(target_current=current,
                                        steps=self.setupManager.get_setup_config()['ramp_points'],
                                        pause=self.config['pause_between_set'])
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


class NIDAQ_channel():
    """
    Represents the activation and readout channel for a singular channel id.
    The NIDAQ has two modules, an activation and readout module.
    Both have the same amount of channels (16x), which can be used to drive a voltage or measure current.
    Attributes:
        setupManager (SetupManager): The setup manager of the current experiment.
        id (int): The channel id. Can take values from 0 to 15.
        activation_module (str): The string identifying the activation module address. Usually `cDAQ1Mod1`.
        readout_module (str): The string identifying the readout module address. Usually `cDAQ1Mod2`.
        sample_frequency (float): The rate at which the channel is taking measurements. Not useful when making distinct measurements with no averaging.
        update_frequqncy (float): The rate at which the channel is updating the voltage applied. Not useful when making continous activation.
        averaging (int): How many points should the channel average over to output a single value.
        min_voltage (float): Minimum voltage that should be driven at a channel.
        max_voltage (float): Maximum voltage that should be driven at a channel.
        current_amplification (float): By how much the current readout must be divided by to get accurate measurements.
    """

    def __init__(self,
                 id: int,
                 setupManager: SetupManager,
                 activation_module: str,
                 readout_module: str) -> None:
        self.setupManager: SetupManager = setupManager
        self.id: int = id
        self.activation_module: str = activation_module
        self.readout_module: str = readout_module
        self.sample_frequency = self.setupManager.get_setup_config()['nidaq']['sample_frequency']
        self.update_period = 1/(self.setupManager.get_setup_config()['nidaq']['update_frequency'])
        self.averaging = self.setupManager.get_setup_config()['nidaq']['samples_per_measurement'] 
        self.min_voltage = self.setupManager.get_voltage_range()[0]
        self.max_voltage = self.setupManager.get_voltage_range()[1]
        self.current_amplification = self.setupManager.get_setup_config()['amplification']
        self.voltage = 0

    def set_voltage(self, target_voltage: float):
        """
        Set the voltage output of the analog output channel.
        Args:
            target_voltage (float): The desired voltage value to set on the output channel.
            continous (bool): If True, continuously applies the target voltage in a separate thread.
                              If False, applies the voltage once and blocks until complete.
        Raises:
            DaqError: If the NI-DAQmx operation fails (e.g., invalid voltage range, device disconnected).
        Notes:
            - When continous=True, any existing voltage thread is stopped and replaced with a new one.
            - When continous=False, the voltage is applied synchronously using a temporary task.
            - The target_voltage must be within the min_voltage and max_voltage range of the channel.
            - The channel must be properly initialized before calling this method.
        """
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(
                f"{self.activation_module}/ao{self.id}",
                min_val=self.min_voltage,
                max_val=self.max_voltage,
                units=VoltageUnits.VOLTS
            )
            task.write(target_voltage, auto_start=True) # type: ignore
            self.voltage = target_voltage 

    def measure_voltage(self) -> float:
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(f"{self.readout_module}/ai{self.id}")
            task.timing.cfg_samp_clk_timing(rate=self.sample_frequency,
                                            sample_mode=AcquisitionType.FINITE,
                                            samps_per_chan=self.averaging)
            voltage = task.read(number_of_samples_per_channel=self.averaging)
        if voltage != None:
            return np.average(voltage) #type: ignore
        else:
            raise NoMeasurementError(f"(NIDAQ {self.readout_module}/ai{self.id})")

    def measure_current(self) -> float:
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_current_chan(f"{self.readout_module}/ai{self.id}")
            task.timing.cfg_samp_clk_timing(rate=self.sample_frequency,
                                            sample_mode=AcquisitionType.FINITE,
                                            samps_per_chan=self.averaging)
            current = task.read(number_of_samples_per_channel=self.averaging)
        if current != None:
            return np.average(current) # type: ignore
        else:
            raise NoMeasurementError(f"(NIDAQ {self.readout_module}/ai{self.id})")

    def ramp_to_voltage(self, target_voltage: float):
        voltages = np.linspace(start=self.voltage,
                            stop=target_voltage,
                            num=self.setupManager.get_setup_config()['ramp_points']) 
        try:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(
                    f"{self.activation_module}/ao{self.id}",
                    min_val=self.min_voltage,
                    max_val=self.max_voltage,
                    units=VoltageUnits.VOLTS
                )
                task.write(voltages, auto_start=True) # type: ignore
            self.voltage = target_voltage
        except DaqError as e:
            self.setupManager.log_error(f"(NIDAQ Channel {self.activation_module}/ao{self.id}) Failed to set voltage: {e}")
          
    def __str__(self) -> str:
        return str(self.id)

    def shutdown(self):
        self.ramp_to_voltage(0)
        # self.set_voltage(0, continous=False)
        self.setupManager.log_info(f"(NIDAQ Channel {self.id}) shutdown.")


class NIDAQ_chassis():
    """
    Wrapper class for the NIDAQ chassis.
    In the NIDAQ chassis are two modules, an activation and readout module.
    Each of them has a set of 16 channels, which is represented by the class `NIDAQ_channel`.
    Attributes:
        setupManager (SetupManager): The setup manager for the current setup.
        config (Config): The part of the setup config that describes the NIDAQ behaviour.
        activation_channels (Dict[int, NIDAQ_channel]): Dictionary listing all activation channelsused in this setup described by the setup config.
        readout_channels (Dict[int, NIDAQ_channel]): Dictionary listing all readout channels used in this setup described by the setup config.
        activation_voltages (Dict[int, float]): Dictionary mapping the activation channels ids to the static voltages that are meant to be applied for each activation channel.
        system (System): Class representing the NIDAQ_chassis.
    """

    def __init__(self, setupManager: SetupManager) -> None:
        self.setupManager = setupManager
        self.config = self.setupManager.get_setup_config()['nidaq'] 
        self.activation_channels: Dict[int, NIDAQ_channel] = {}
        self.readout_channels: Dict[int, NIDAQ_channel] = {}
        self.activation_voltages: Dict[int, float] = {}
        self.system = System.local()
        for module in self.system.devices:
            if module.name == self.config["activation_module_id"]:
                self.activation_module = module
                self.activation_module.reset_device()
            elif module.name == self.config["readout_module_id"]:
                self.readout_module = module
                self.readout_module.reset_device()
            else:
                continue

        for i in self.config['control_voltages'].keys():
            self.activation_channels[i] = NIDAQ_channel(i,
                                                        self.setupManager,
                                                        self.activation_module.name,
                                                        self.readout_module.name)
            self.activation_voltages[i] = self.config['control_voltages'][i]
        for i in self.config['readout_channels']:
            self.readout_channels[i] = NIDAQ_channel(i,
                                                     self.setupManager,
                                                     self.activation_module.name,
                                                     self.readout_module.name)
        self.setupManager.log_info(f" --- INSTRUMENT: NIDAQ --- ") 
        self.setupManager.log_info(f'Following voltages will be applied: {",".join(map(str, self.activation_voltages.values()))} on channels {",".join(map(str, self.activation_channels.keys()))} respectively')
        # self.setupManager.wait_for_user_input()
        self._calibrate_to_zero_all()

    def start_active_all_channels(self):
        """
        Activates all channels with the voltages provided in `self.activation_voltages`.
        
        :param self: Instance of NIDAQ_chassis
        """
        for channel, voltage in self.activation_voltages.items():
                self.setupManager.log_info(f"(NIDAQ Channel {channel}) Voltage {voltage}V applied.")
                self.activation_channels[channel].set_voltage(voltage)

    def set_voltage(self, id: int, target_voltage, ramp: bool = False):
        if ramp:
            self.activation_channels[id].ramp_to_voltage(target_voltage)
        else:
            self.activation_channels[id].set_voltage(target_voltage)

    def measure_current(self, id: int) -> float:
        return self.readout_channels[id].measure_current()

    def measure_voltage(self, id: int) -> float:
        return self.readout_channels[id].measure_voltage()
        
    def _calibrate_to_zero_all(self):
        """
        Puts all channels to 0V.
        
        :param self: Instance of NIDAQ_chassis
        """
        for channel in self.activation_channels.values():
            channel.ramp_to_voltage(0)

    def measure_voltage_all_channels(self) -> Dict[int, float]:
        """
        Retrieves voltages measured at all channels.
        
        :param self: Instance of NIDAQ_chassis
        :return: Dictionary of voltage values, where each key represents the id of the channel.
        :rtype: Dict[int, float]
        """
        voltages: Dict[int, float] = {}
        for id, channel in self.readout_channels.items():
            voltages[id] = channel.measure_voltage()
        return voltages

    def measure_current_all_channels(self) -> Dict[int, float]:
        """
        Retrieves currents measured at all channels.
        
        :param self: Instance of NIDAQ_chassis
        :return: Dictionary of current values, where each key represents the id of the channel.
        :rtype: Dict[int, float]
        """
        currents: Dict[int, float] = {}
        for id, channel in self.readout_channels.items():
            currents[id] = (channel.measure_voltage())
        return currents


    def shutdown(self):
        """
        Shutsdown all channels in the NIDAQ_chassis.
        See `NIDAQ_channel.shutdown()`
        
        :param self: Instance of NIDAQ_chassis
        """
        for channel in self.activation_channels.values():
            channel.shutdown()

