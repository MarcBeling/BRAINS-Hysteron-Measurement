
from equipment.NIDAQ import NIDAQ_chassis
from equipment.K2400 import K2400
from util.setupmanager import SetupManager
from util.solution import Solution
from util.response import Response
from typing import Dict, List
import numpy as np


class Singleton(type):
    """Metaclass to enforce Singleton behavior."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    
class HardwareInterface(metaclass=Singleton):

    def __init__(self) -> None:
        self.setupManager: SetupManager = SetupManager()
        self.nidaq = NIDAQ_chassis()
        self.smu = K2400()
        self.rnpu = PhysicalRNPU(self.nidaq, self.smu)

    def apply_and_calc_fit(self, control_voltages: List[float], solution_idx):
        solution: Solution = Solution.convert_list_to_solution(
            self.rnpu.get_control_electrodes(), control_voltages)
        response = self.rnpu.get_response(solution, solution_idx)
        fittness = self.compute_fittness(response)
        return fittness
    
    def compute_fittness(self, response: Response):
        return np.sum(np.pow((response.get_up_sweep() - response.get_down_sweep()), 2))
    
    def close(self):
        self.smu.shutdown()
        self.nidaq.shutdown()


class PhysicalRNPU():

    def __init__(self, nidaq: NIDAQ_chassis, smu: K2400) -> None:
        self.sm: SetupManager = SetupManager()
        self.config = self.sm.get_config()['RNPU']
        self.nidaq = nidaq
        self.smu = smu
        self.input = self.config['input_electrodes']
        self.control: List = self.config['control_electrodes']
        self.output: str = self.config['output_electrodes']

        self.all_electrodes = []
        self.all_electrodes.append(self.input)
        self.all_electrodes = self.all_electrodes + self.control
        self.all_electrodes.append(self.output)

        self.cv_dict: Dict[int, float] = dict.fromkeys(self.control, 0)

    def set_control_voltage_configuration(self, control_voltages: Dict[int, float]):
        self.cv_dict = control_voltages
        self.nidaq.set_voltage_configuration(control_voltages)

    def set_input(self, input_values: Dict[int, float]):
        self.nidaq.set_voltage(list(input_values.keys())[0], list(input_values.values())[0])

    def get_output_current_all(self, include_smu: bool = True):
        currents_out = self.nidaq.get_currents_bulk(list(self.nidaq.readout_channels.keys()))
        currents_out = {key: value for key, value in currents_out.items()}
        if include_smu:
            currents_out[self.output] = self.smu.measure_current() # type: ignore
        return currents_out
    
    def get_output_current(self):
        return self.smu.measure_current()
    
    def sweep_all(self, solution_idx: int):
        input_data = self.sm.get_input_data()
        current_dict = {key: [] for key in self.all_electrodes}
        for voltage in input_data:
            self.set_input({self.input: voltage})
            result = self.get_output_current_all()
            for key in result.keys():
                current_dict[key].append(result[key])
        self.sm.create_subfolder(f"data/solution_{solution_idx}")
        self.sm.create_subfolder(f"plots/solution_{solution_idx}")
        self.sm.write_dict(f"solution_{solution_idx}/currents", current_dict)
        self.sm.plot_dict(current_dict, f"/solution_{solution_idx}/")
        return current_dict
            
    def sweep(self, solution_idx: int):
        input_data = self.sm.get_input_data()
        current_list = []
        for voltage in input_data:
            self.set_input({self.input: voltage})
            current_list.append(self.get_output_current())
        self.sm.create_subfolder(f"data/solution_{solution_idx}")
        self.sm.create_subfolder(f"plots/solution_{solution_idx}")
        self.sm.write_1d_array(f"solution_{solution_idx}/currents_{self.output}.csv",current_list)
        self.sm.plot_list(current_list, f"/solution_{solution_idx}/")
        return current_list
    
    def get_response(self, solution: Solution, solution_idx: int):
        self.set_control_voltage_configuration(solution.get_values())
        if self.config['sweep_all']:
            result = self.sweep_all(solution_idx)
            return Response(result[self.output])
        else:
            result = self.sweep(solution_idx)
            return Response(result)
        
    def get_control_electrodes(self):
        return self.control
    
