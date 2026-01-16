from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep
CONFIG_SETUP = Config(str(Path('configs')/'TEST_VOLTMETER.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.TEST_VOLTMETER = ep.TEST_VOLTMETER(setupManager)
    try:
        experiment.run()
    except KeyboardInterrupt:
        pass
        