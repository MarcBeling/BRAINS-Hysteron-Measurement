from abc import ABC, abstractmethod

class Experiment(ABC):
    """
    Abstract class to unifying Experiment implementation.
    Requires an implementation of a setup manager, and a run function.
    """
    def __init__(self) -> None:
        super().__init__()


    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def plot(self) -> None:
        pass

    @abstractmethod
    def close(self) -> None:
        pass

    def voltage_to_current(self, voltage: float, electrode_id: int) -> float:
        if electrode_id != 0:
            current = voltage/(2e6)
        else:
            current = voltage/(2e7)
        current_nA = current * 1e9
        return current_nA
    
    def current_to_nA(self, current) -> float:
        return current * 1e9