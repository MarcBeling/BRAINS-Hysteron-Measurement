import numpy as np
from pathlib import Path

import matplotlib.pyplot as plt

def plot_input(xdata, ylabel):
    plt.figure(figsize=(5, 5))
    plt.title("Input Data")
    plt.xlabel("Time in s")
    plt.plot(xdata, color='b')
    plt.xticks(np.arange(0, len(xdata), 20))
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.axvline(0, alpha=0.4)
    plt.grid()
    plt.tick_params(direction='in')
    plt.show()

def plot_vi_curve(folder_name, xdataf, ydataf, average=True):
    folder_path = Path(folder_name)
    
    input_file = folder_path / xdataf
    output_file = folder_path / ydataf
    
    if not input_file.exists() or not output_file.exists():
        print(f"Error: CSV files not found in {folder_name}")
        return
    
    input_data = np.loadtxt(input_file, delimiter=',')
    output_data = np.loadtxt(output_file, delimiter=',')

    plot_xdata(input_data)
    input_data = input_data[60:-60]


    # Assume input_data and output_data are 1D numpy arrays of same length

    fig, ax = plt.subplots(figsize=(5, 5))

    # Optional axis lines:
    # ax.axhline(0, color='k', alpha=0.4)
    # ax.axvline(0, color='k', alpha=0.4)

    # Ticks and tick params
    ax.set_xticks(np.arange(-100e-9, 10e-9, 10e-9))
    # If you also want custom y ticks, uncomment and adjust:
    # ax.set_yticks(np.arange(-0.15, -0.0875, 0.025))
    ax.tick_params(direction='in')

    # Find x-offset (voltage at zero current)
    zero_current_idx = np.argmin(np.abs(output_data))
    x_offset = input_data[zero_current_idx]

    # Min/Max points
    min_idx = np.argmin(output_data)
    max_idx = np.argmax(output_data)

    ax.axvspan(-70e-9, -52e-9, color='r', alpha=0.1)
    # Markers for min/max
    ax.plot(input_data[min_idx], output_data[min_idx], 'g.', markersize=5,
            label=f'Min: ({input_data[min_idx]:.3g}A, {output_data[min_idx]:.3g}V)')
    ax.plot(input_data[max_idx], output_data[max_idx], 'b.', markersize=5,
            label=f'Max: ({input_data[max_idx]:.3g}A, {output_data[max_idx]:.3g}V)')

    # Labels, title, grid, legend
    ax.set_xlabel(r"Input Current on $e_{i}$ in nA")
    ax.set_ylabel(r"Output Voltage at $e_{o}$ in V")
    ax.set_title("VI Curve 3 Terminal RNPU with control voltages")
    ax.grid(True)
    ax.legend()

    fig.tight_layout()

    if average:
        input_data = np.array([input_data[i:i+3].mean() for i in range(0, len(input_data), 3)])
        output_data = np.array([output_data[i:i+3].mean() for i in range(0, len(output_data), 3)])

    # --- (Optional) animated drawing of the VI curve ---
    plt.ion()  # interactive mode on (still via plt, but the drawing is on ax)
    line, = ax.plot([], [], color='r', linewidth=1)  # reusable line for speed

    for i in range(1, len(input_data), 30):
        line.set_data(input_data[:i], output_data[:i])
        fig.canvas.draw_idle()
        plt.pause(0.00005)

    plt.ioff()
    plt.show() 

def plot_xdata(xdata):
    plt.title("Input Waveform")
    plt.ylabel("Values")
    plt.plot(xdata, 'r-')
    plt.tight_layout()
    plt.grid()
    plt.tick_params(direction='in')
    plt.axhline(0, color='k', alpha=0.4)
    plt.show()

def plot_iv_curve(folder_name, xdataf, ydataf, average=True):

    folder_path = Path(folder_name)

    input_file = folder_path / xdataf
    output_file = folder_path / ydataf

    if not input_file.exists() or not output_file.exists():
        print(f"Error: CSV files not found in {folder_name}")
        return

    input_data = np.loadtxt(input_file, delimiter=',')
    output_data = np.loadtxt(output_file, delimiter=',')

    plot_xdata(input_data)  # if you have this helper

    # Trim ends
    input_data = input_data[60:-60]

    if average:
        # Average outputs for duplicate x values
        unique_input, indices = np.unique(input_data, return_inverse=True)
        unique_output = np.array([output_data[indices == i].mean() for i in range(len(unique_input))])

        input_data = unique_input
        output_data = unique_output

        # Average every three consecutive points
        input_data = np.array([input_data[i:i+3].mean() for i in range(0, len(input_data), 3)])
        output_data = np.array([output_data[i:i+3].mean() for i in range(0, len(output_data), 3)])

    # Scaling: convert output_data to nA (starting from A)
    output_data = output_data / (2 * 10**6)
    output_data = output_data * 1e9  # A -> nA

    # ---- Plot with ax instead of plt ----
    fig, ax = plt.subplots(figsize=(5, 5))

    ax.axvline(0, color='k', alpha=0.4)
    ax.set_xticks(np.arange(-1.5, 1.5, 0.5))
    # ax.set_xticks(np.arange(-25, 21, 5))  # alternative ticks if needed
    ax.tick_params(direction='in')

    ax.plot(input_data, output_data, color='r', linewidth=3)

    # x-offset (voltage at zero current)
    zero_current_idx = np.argmin(np.abs(output_data))
    x_offset = input_data[zero_current_idx]

    # Min/Max markers (markersize 0 is effectively invisible; keeping for label consistency)
    min_idx = np.argmin(output_data)
    max_idx = np.argmax(output_data)
    ax.plot(input_data[min_idx], output_data[min_idx], 'r.', markersize=0,
            label=f'Min: ({input_data[min_idx]:.3f}V, {output_data[min_idx]:.3f}nA)')
    ax.plot(input_data[max_idx], output_data[max_idx], 'r.', markersize=0,
            label=f'Max: ({input_data[max_idx]:.3f}V, {output_data[max_idx]:.3f}nA)')

    ax.legend()
    ax.set_xlabel(r"Input Voltage on $e_{i}$ in V")
    ax.set_ylabel(r"Output Current at $e_{o}$ in nA")
    ax.set_title("IV Curve 3 Terminal RNPU (240mV Control)")

    ax.grid(True)
    
    ax.axhspan(-70, -52, color='r', alpha=0.1)
    fig.tight_layout()
    plt.show()