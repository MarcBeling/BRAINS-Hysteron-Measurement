import numpy as np
from pathlib import Path

import matplotlib.pyplot as plt

def plot_input(xdata, ylabel):
    plt.figure(figsize=(5, 5))
    plt.title("Input Data")
    plt.xlabel("Time in s")
    plt.plot(xdata, color='b')
    plt.xticks(np.arange(0, len(xdata), 2))
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.axvline(0, alpha=0.4)
    plt.tick_params(direction='in')
    plt.show()

def plot_vi_curve(folder_name, xdataf, ydataf):
    folder_path = Path(folder_name)
    
    input_file = folder_path / xdataf
    output_file = folder_path / ydataf
    
    if not input_file.exists() or not output_file.exists():
        print(f"Error: CSV files not found in {folder_name}")
        return
    
    input_data = np.loadtxt(input_file, delimiter=',')
    output_data = np.loadtxt(output_file, delimiter=',')

    plot_input(input_data, "Voltages in V")
    input_data = input_data[60:-60] 
    plt.figure(figsize=(5, 5))

    # plt.axhline(0, color='k', alpha=0.4)
    # plt.axvline(0, color='k', alpha=0.4)
    # plt.yticks(np.arange(-1.5, 1.5, 0.5))
    # plt.xticks(np.arange(-25, 21, 5))
    plt.tick_params(direction='in')

    plt.plot(input_data[60:-60], output_data, color='r', linewidth=3)

    # Find x-offset (voltage at zero current)
    zero_current_idx = np.argmin(np.abs(output_data))
    x_offset = input_data[zero_current_idx]

    min_idx = np.argmin(output_data)
    max_idx = np.argmax(output_data)
    
    plt.plot(input_data[min_idx], output_data[min_idx], 'g.', markersize=0, label=f'Min: ({input_data[min_idx]:.3f}V, {output_data[min_idx]:.3f}nA)')
    plt.plot(input_data[max_idx], output_data[max_idx], 'b.', markersize=0, label=f'Max: ({input_data[max_idx]:.3f}V, {output_data[max_idx]:.3f}nA)')
    plt.xlabel("Input Current on $e_{i}$ in nA")
    plt.ylabel("Output Voltage at $e_{o}$ in V")
    plt.title("VI Curve 3 Terminal RNPU with control voltages")
    plt.grid()
    plt.tight_layout() 
    plt.savefig(f'{folder_name}/output.png')
    plt.show()

def plot_iv_curve(folder_name, xdataf, ydataf):
    folder_path = Path(folder_name)
    
    input_file = folder_path / xdataf
    output_file = folder_path / ydataf
    
    if not input_file.exists() or not output_file.exists():
        print(f"Error: CSV files not found in {folder_name}")
        return
    
    input_data = np.loadtxt(input_file, delimiter=',')
    output_data = np.loadtxt(output_file, delimiter=',')

    plot_input(input_data, "Voltages in V")
    input_data = input_data[60:-60]
    # Get unique input values and average corresponding output values
    unique_input, indices = np.unique(input_data, return_inverse=True)
    unique_output = np.array([output_data[indices == i].mean() for i in range(len(unique_input))])

    input_data = unique_input
    output_data = unique_output

    # Average every three consecutive values
    input_data = np.array([input_data[i:i+3].mean() for i in range(0, len(input_data), 3)])
    output_data = np.array([output_data[i:i+3].mean() for i in range(0, len(output_data), 3)])

    output_data = output_data/(2*10**(6))
    output_data = output_data * 1e9  # Convert to nA

    plt.figure(figsize=(5, 5))

    # plt.axhline(0, color='k', alpha=0.4)
    # plt.axvline(0, color='k', alpha=0.4)
    # plt.yticks(np.arange(-1.5, 1.5, 0.5))
    # plt.xticks(np.arange(-25, 21, 5))
    plt.tick_params(direction='in')

    plt.plot(input_data, output_data, color='r', linewidth=3)

    # Find x-offset (voltage at zero current)
    zero_current_idx = np.argmin(np.abs(output_data))
    x_offset = input_data[zero_current_idx]

    min_idx = np.argmin(output_data)
    max_idx = np.argmax(output_data)
    
    plt.plot(input_data[min_idx], output_data[min_idx], 'r.', markersize=0, label=f'Min: ({input_data[min_idx]:.3f}V, {output_data[min_idx]:.3f}nA)')
    plt.plot(input_data[max_idx], output_data[max_idx], 'r.', markersize=0, label=f'Max: ({input_data[max_idx]:.3f}V, {output_data[max_idx]:.3f}nA)')
    plt.legend()
    plt.xlabel("Input Voltage on $e_{i}$ in V")
    plt.ylabel("Output Current at $e_{o}$ in nA")
    plt.title("IV Curve 3 Terminal RNPU")

    plt.grid()
    plt.tight_layout() 
    plt.savefig(f'{folder_name}/output.png')
    plt.show()


    # plot_iv_curve("DNPU_3T_240mV", 'input_current.csv', 'output_current.csv')
    # plot_vi_curve("DNPU_3T_HYSTERON_240mV", 'input_current.csv', 'output_voltage.csv')