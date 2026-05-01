import numpy as np
from typing import Dict, List

from util.errors import NoMeasurementError
from util.configreader import Config
from itertools import repeat

import nidaqmx
from nidaqmx.constants import VoltageUnits, AcquisitionType
from nidaqmx.errors import DaqError
from nidaqmx.system import System

from util.setupmanager import SetupManager


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
    """

    def __init__(self,
                 id: int,
                 activation_module: str,
                 readout_module: str,
                 config_id: str = "nidaq") -> None:
        self.config_id = config_id
        self.setupManager: SetupManager = SetupManager() # type: ignore
        self.config = self.setupManager.get_config()
        self.id: int = id
        self.activation_module: str = activation_module
        self.readout_module: str = readout_module
        self.sample_frequency = self.config[config_id]['sample_frequency']
        self.averaging = self.config[config_id]['samples_per_measurement'] 
        self.min_voltage = self.setupManager.get_voltage_range()[0]
        self.max_voltage = self.setupManager.get_voltage_range()[1]
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
                            num=self.setupManager.get_config()[self.config_id]['ramp_points']) 
        try:
            with nidaqmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(
                    f"{self.activation_module}/ao{self.id}",
                    min_val=self.min_voltage,
                    max_val=self.max_voltage,
                    units=VoltageUnits.VOLTS,
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

    def __init__(self) -> None:
        self.setupManager: SetupManager = SetupManager() # type: ignore
        self.config = self.setupManager.get_config()["nidaq"]
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
                                                        self.activation_module.name,
                                                        self.readout_module.name)
            self.activation_voltages[i] = self.config['control_voltages'][i]
        for i in self.config['readout_channels']:
            self.readout_channels[i] = NIDAQ_channel(i,
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
                self.activation_channels[channel].ramp_to_voltage(voltage)

    def set_voltage(self, id: int, target_voltage, ramp: bool = False, verbose: bool = False):
        if ramp:
            self.activation_channels[id].ramp_to_voltage(target_voltage)
        else:
            self.activation_channels[id].set_voltage(target_voltage)
        if verbose:
            self.setupManager.log_info(f"(NIDAQ Channel {id}) Voltage set to: {target_voltage}V")

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
    
    def get_currents_bulk(self, list_readout_channels: List[int]) -> Dict[int, float]:
        voltages: Dict[int, float] = {}
        voltages_raw = None
        readout_string = ""
        for i, id in enumerate(list_readout_channels):
            readout_string = readout_string + f"{self.readout_module.name}/ai{id}"
            if i+1 != len(list_readout_channels):
                readout_string = readout_string + ","
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(readout_string)
            task.timing.cfg_samp_clk_timing(rate=self.config["sample_frequency"],
                                            sample_mode=AcquisitionType.FINITE,
                                            samps_per_chan=self.config["samples_per_measurement"])
            voltages_raw = task.read(number_of_samples_per_channel=self.config["samples_per_measurement"])
        if voltages_raw != None:
            for i, voltage_per_channel in enumerate(voltages_raw):
                voltages[list_readout_channels[i]] = np.average(voltage_per_channel) # type:ignore
        else:
            raise NoMeasurementError(f"(NIDAQ {readout_string})")
        return voltages
    
    def set_voltage_configuration_all(self, voltage, list_activation_channels: List[int]):
        
        voltages = list(repeat(voltage, len(list_activation_channels)))
        activation_string = ""
        for i, id in enumerate(list_activation_channels):
            activation_string = activation_string + f"{self.activation_module.name}/ao{id}"
            if i+1 != len(list_activation_channels):
                activation_string = activation_string + ","
        
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(activation_string)
            task.write(voltages, auto_start=True) #type: ignore
        

    def set_voltage_configuration(self, control_voltages: Dict[int, float]):
        voltages = control_voltages.values()
        list_activation_channels = control_voltages.keys()

        activation_string = ""
        for i, id in enumerate(list_activation_channels):
            activation_string = activation_string + f"{self.activation_module.name}/ao{id}"
            if i+1 != len(list_activation_channels):
                activation_string = activation_string + ","
        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(activation_string)
            task.write(voltages, auto_start=True) #type: ignore

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