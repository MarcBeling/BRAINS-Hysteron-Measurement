
import matplotlib.pyplot as plt
import numpy as np
from itertools import product

cv_list_1 = [1.5, 1.4, 1.3, 1.2, 1.1]
cv_list_2 = [1.5, 1.4, 1.3, 1.2, 1.1]
cv_list_3 = [-1.5, -1.4, -1.3, -1.2, -1.1]

for CV1, CV2, CV3 in product(cv_list_1, cv_list_2, cv_list_3):
    foldername = "IV_RNPU_MATRIX_FullRange_Resistor-09-03-2026_08-17-44"

    U = np.loadtxt(f"output/09-03-2026/{foldername}/data/{CV1}V_{CV2}V_{CV3}V/voltage_IV.csv")
    I = np.loadtxt(f"output/09-03-2026/{foldername}/data/{CV1}V_{CV2}V_{CV3}V/current_IV.csv")*1e9
    I_t = np.loadtxt(f"output/09-03-2026/{foldername}/data/{CV1}V_{CV2}V_{CV3}V/current_RNPU_all.csv")

    plt.figure(figsize=(5,4))
    plt.plot(U[60:-60], I[60:-60], label="Current @ SMU")
    plt.plot(U[60:-60], I_t[60:-60], label="Sum of Current @ RNPU")
    plt.title(f"IV Curve @ {CV1}V & {CV2}V & {CV3}V")
    plt.axhline(0, color='k', alpha=0.4)
    plt.axvline(0, color='k', alpha=0.4)
    plt.grid()
    plt.xlabel("Voltage in V")
    plt.ylabel("Current in nA @ Pad IV")
    plt.legend()
    #plt.show()
    plt.savefig(f"output/09-03-2026/{foldername}/plots/{CV1}V_{CV2}V_{CV3}V/{CV1}V_{CV2}V_{CV3}V.png")
    plt.close()