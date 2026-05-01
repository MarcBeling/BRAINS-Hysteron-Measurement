import matplotlib.pyplot as plt
import numpy as np

def plot_vi_curve(voltage_file, current_file):
    """
    Plot a VI curve from two files: one with voltage values and one with current values.
    
    Parameters
    ----------
    voltage_file : str
        Path to the file containing voltage values (one per line).
    current_file : str
        Path to the file containing current values (one per line).
    """
    
    # Load data (assuming a simple one-column file)
    voltage = np.loadtxt(voltage_file)
    current = np.loadtxt(current_file)

    # Basic consistency check
    if len(voltage) != len(current):
        raise ValueError("Voltage and current files must contain the same number of data points.")
    
    # Plot VI curve
    plt.figure(figsize=(5, 4))
    plt.plot(current[60:-60] * (1e9/2e6), voltage[60:-60])

    plt.title("VI Curve")
    plt.xlabel("Current (A)")
    plt.ylabel("Voltage (V)")
    plt.grid(True)

    plt.show()


if __name__=="__main__":
    plot_vi_curve("plotters/VIPlot/RAW_voltages_pad_IV.csv", "plotters/VIPlot/RAW_currents_pad_7.csv",)