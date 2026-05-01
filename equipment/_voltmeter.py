from abc import ABC, abstractmethod
from typing import Union, Any

class Voltmeter(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def _read_config(self) -> None:
        pass

    @abstractmethod
    def _get_device(self) -> Any:
        pass

    @abstractmethod
    def _configure_device(self) -> None:
        pass

    @abstractmethod
    def measure_voltage(self) -> Union[Any, None, float]:
        pass

    @abstractmethod
    def measure_current(self) -> Union[Any, None, float]:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass