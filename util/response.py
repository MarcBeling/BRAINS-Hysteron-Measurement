
from typing import List
import numpy as np

class Response():
    """
    A response is the output of the RNPU after an input and control voltages have been applied.
    The data is split into two, representing up and down sweep.
    This class was made specifically for the genetic algorithm experiment class (`AI_GENETIC`),
    and expects the SWEEP Waveform to be used as the input waveform.

    @TODO: Expand the code so that any input waveform can be used.
    """

    def __init__(self, current_values: List[float]) -> None:
        self.data = np.asarray(current_values)
        self.up_sweep, self.down_sweep = np.array_split(self.data, 2)
    
    def __getitem__(self, key: int) -> float:
        return self.data[key]
    
    def get_up_sweep(self) -> np.ndarray:
        return self.up_sweep
    
    def get_down_sweep(self) -> np.ndarray:
        return self.down_sweep
