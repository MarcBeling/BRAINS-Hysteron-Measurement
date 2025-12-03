
from setupmanager import SetupManager

class DeviceNotFoundError(Exception):
    """
    Error when a measurement device was not found.
    """
    def __init__(self, device_name) -> None:
        super().__init__(f'{device_name} was not found or could not be connected to.')

class ModeMismatchError(Exception):
    """
    Certain measurement units have different modes.
    For example the Keithley 2401 has a current driven and a voltage driven mode.
    This error is thrown when the user wants to drive current in voltage driven mode and vice versa.
    """
    def __init__(self, smu):
        self.drive_mode = smu.drive_mode
        if self.drive_mode == 'CURENT_DRIVEN':
            message = 'SMU {0} is in current mode. Voltage sourcing is not allowed. Please verify your configuration.'.format(smu.device)
        else:
            message = 'SMU {0} is in voltage mode. Current sourcing is not allowed. Please verify your configuration.'.format(smu.device)
        super().__init__(message)
        SetupManager().log_error(message)# type: ignore
        del smu

class NoMeasurementError(Exception):
     """
     When despite a lack of errors from the hardware side, a device could not provide measurement data.
     """
     def __init__(self, device_name):
        message = f"The {device_name} could not make a measurement."
        super().__init__(message)
        SetupManager().log_error(message)# type: ignore

class BadConfigError(Exception):
    """
    When the config is badly formatted for a measruement device.
    """
    def __init__(self, reason: str) -> None:
        message = 'The config has been badly formatted. ' + reason
        super().__init__(message)
        SetupManager().log_error(message)# type: ignore

class InvalidChannel(Exception):
    """
    Certain devices like the NIDAQ are further structured into channels.
    Trying to address a channel that does not exist or is not used as intended will throw this error.
    """
    def __init__(self) -> None:
        message = 'Invalid channel usage: input used as output or vice versa.'
        super().__init__(message)
        SetupManager().log_error(message)# type: ignore