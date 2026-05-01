from typing import List, Dict


class Solution():
    """
    A solution is a class that wraps the control voltage configuration of an RNPU in a more handable way. The word solution was used for this class as it is involved in the AI_GENETIC experiment, where a genetic algorithm has to find correct solutions for certain machine learning problems.
    """    

    def __init__(self, list_control_electrodes: List[int]) -> None:
        self._control_voltages = dict.fromkeys(list_control_electrodes, 0.0)

    def __getitem__(self, key):
        return self._control_voltages[key]
    
    def __iter__(self):
        return iter(self._control_voltages)
    
    def __repr__(self):
        return repr(self._control_voltages)
    
    def get_values(self):
        return self._control_voltages
    
    def set_values_by_list(self, control_voltages: List[float]):
        """
        Set a control voltage configuration solution via a list.
        It is assumed the order of the control voltages in the list were not changed, so that every element represents the control electrode given by configuration file in the correct order.

        Args:
            control_voltages (List[float]): List of ordered control voltages. 
        """        
        for index, electrode in enumerate(self._control_voltages.keys()):
            self._control_voltages[electrode] = control_voltages[index]
    
    @staticmethod
    def convert_list_to_solution(control_electrodes: List[int],
                                 control_voltages: List[float]):
        """
        Returns the 

        Args:
            control_electrodes (List[int]): _description_
            control_voltages (List[float]): _description_

        Returns:
            _type_: _description_
        """        
        solution = Solution(control_electrodes)
        solution.set_values_by_list(control_voltages)
        return solution

    @staticmethod
    def convert_dict_to_solution(control_voltage_dict: Dict[int, float]):
        solution = Solution(list(control_voltage_dict.keys()))
        return solution
    
