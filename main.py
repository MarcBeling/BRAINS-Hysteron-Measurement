from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep
CONFIG_SETUP = Config(str(Path('configs')/'IV_NIDAQ_8ALL.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.IV_NIDAQ_8ALL = ep.IV_NIDAQ_8ALL(setupManager)
    try:
        experiment.run()
        experiment.plot()
    except KeyboardInterrupt:
        pass
        