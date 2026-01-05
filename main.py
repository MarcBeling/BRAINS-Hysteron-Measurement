from configreader import Config
from pathlib import Path
from setupmanager import SetupManager
import experiment as ep
import plotter as pt

CONFIG_SETUP = Config(str(Path('configs')/'Setup.yaml'))

if __name__=="__main__":

    setupManager: SetupManager = SetupManager(CONFIG_SETUP)
    experiment: ep.RNPU_Experiment = ep.RNPU_Experiment(setupManager)
    try:
        experiment.run()
        # pt.plot_iv_curve(setupManager.save_name,'input_current.csv', 'output_current.csv')
    except KeyboardInterrupt:
        pass
        