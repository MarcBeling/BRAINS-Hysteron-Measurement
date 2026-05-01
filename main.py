import sys

from experiments.AI_JAN import AI_JAN
from experiments._experiment import Experiment
from experiments.AI_GENETIC import AI_GENETIC
from experiments.IV_MATRIX import IV_MATRIX
from experiments.IV_NI import IV_NI
from experiments.IV_HYST import IV_HYST
from experiments.VI_HYST import VI_HYST
from experiments.IV_NI_SMU import IV_NI_SMU
from experiments.IV_NI_SMU_REVERSE import IV_NI_SMU_REVERSE
from experiments.IV_DYNAMIC import IV_DYNAMIC
from experiments.IV_PULL_PUSH import IV_PULL_PUSH
from experiments.IV_MARTIN import IV_MARTIN
from experiments.IV_MARTIN_SMU import IV_MARTIN_SMU

from util.global_states import global_variables
import winsound

AVAILABLE_MODES = {
    "AI_GENETIC": AI_GENETIC,
    "AI_JAN": AI_JAN,
    "IV_NI": IV_NI,
    "IV_NI_SMU": IV_NI_SMU,
    "IV_HYST": IV_HYST,
    "VI_HYST": VI_HYST,
    "IV_MATRIX": IV_MATRIX,
    "IV_NI_SMU_REVERSE": IV_NI_SMU_REVERSE,
    "IV_DYNAMIC": IV_DYNAMIC,
    "IV_PULL_PUSH": IV_PULL_PUSH,
    "IV_MARTIN": IV_MARTIN,
    "IV_MARTIN_SMU": IV_MARTIN_SMU
}

if __name__=="__main__":

    if len(sys.argv) < 2:
        print("Usage: python main.py <ExperimentName>")
        sys.exit(1)

    global_variables.EXPERIMENT_NAME = sys.argv[1]
    experiment_class: type[Experiment] = AVAILABLE_MODES[global_variables.EXPERIMENT_NAME]
    experiment: Experiment = experiment_class()

    try:
        experiment.run()
        experiment.plot()
        winsound.Beep(100, 1000)
    except KeyboardInterrupt:
        print("Measurement interrupted by user.")
        experiment.close()
