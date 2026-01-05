import numpy as np
from pathlib import Path
import sys
import matplotlib.pyplot as plt

def plot(xdata_name, ydata_name, folder_name='', type="IV", title=""):

    xdata_file: Path = Path(folder_name)/xdata_name
    ydata_file: Path = Path(folder_name)/ydata_name

    xdata = np.loadtxt(xdata_file, delimiter=",")[60:-60]
    ydata = np.loadtxt(ydata_file, delimiter=",")

    fig, ax = plt.subplots()

    if type == "IV":
        ydata = ydata / (2 * 10**6)
        ydata = ydata * 1e9  # A -> nA

        ax.set_xlabel("Voltage in V")
        ax.set_ylabel("Current in nA")

        ax.axvline(0, color='k', alpha=0.4)
        ax.set_xticks(np.arange(-1.5, 1.5, 0.5))

    elif type == "VI":
        
        ax.set_xlabel("Current in nA")
        ax.set_ylabel("Voltage in V")

    ax.plot(xdata, ydata)
    ax.set_title(title)
    ax.tick_params(direction='in')
    ax.grid(True)
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    
    if len(sys.argv) > 4:
        plot(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] if len(sys.argv) > 5 else "")