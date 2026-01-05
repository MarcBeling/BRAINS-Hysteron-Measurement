import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

def plot():


    xdata_file: Path = Path("VI_RNPU_3T-2026-01-05_11-37-11")/"currents_ei.csv"
    ydata_file: Path = Path("VI_RNPU_3T-2026-01-05_11-37-11")/"voltages_ei.csv"
    xdata_file_range: Path = Path("VI_RNPU_3T_FullRange-2026-01-05_11-47-23")/"currents_ei.csv"    
    ydata_file_range: Path = Path("VI_RNPU_3T_FullRange-2026-01-05_11-47-23")/"voltages_ei.csv"

    xdata = np.loadtxt(xdata_file, delimiter=",")[60:-60]
    ydata = np.loadtxt(ydata_file, delimiter=",")
    xdata_range = np.loadtxt(xdata_file_range, delimiter=",")[60:-60]
    ydata_range = np.loadtxt(ydata_file_range, delimiter=",")

    fig, ax = plt.subplots()
        
    ax.set_xlabel("Current in nA")
    ax.set_ylabel("Voltage in V")

    ax.plot(xdata, ydata, label="Current Sweep between -60nA to -30nA", linewidth=3)
    ax.plot(xdata_range, ydata_range, label="Current Sweep between -150nA to 150nA")
    ax.set_title("VI Curve Comparison between different current sweeps.")
    ax.tick_params(direction='in')
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    plt.show()

plot()