import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re

# Path to THIS script's folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IVCURVES_DIR = os.path.join(BASE_DIR, "IVCurves")

# Regex to extract the bias value from folder name
# Example folder: IV_3T_R_15mV-20250225
FOLDER_REGEX = r"IV_RNPU_3T_R_([+-]?[0-9\.]+)mV-"

def extract_bias(foldername):
    match = re.search(FOLDER_REGEX, foldername)
    if match:
        return float(match.group(1))
    return None

def load_iv_data(data_folder):
    """Loads voltage and current CSVs from the given folder."""

    voltage_path = os.path.join(data_folder, "RAW_voltages_pad_IV.csv")
    current_path = os.path.join(data_folder, "RAW_currents_pad_7.csv")

    if not (os.path.exists(voltage_path) and os.path.exists(current_path)):
        return None, None

    voltages = pd.read_csv(voltage_path, header=None).squeeze()
    currents = pd.read_csv(current_path, header=None).squeeze()

    return voltages, currents


def main():

    bias_folder_pairs = []

    for folder in os.listdir(IVCURVES_DIR):
        full_path = os.path.join(IVCURVES_DIR, folder)
        if not os.path.isdir(full_path):
            continue

        bias = extract_bias(folder)
        if bias is not None:
            bias_folder_pairs.append((bias, folder))

    bias_folder_pairs.sort(key=lambda x: x[0], reverse=True)

    cmap = plt.get_cmap('rainbow')
    colors = cmap(np.linspace(1, 0, len(bias_folder_pairs)))

    plt.figure(figsize=(10, 6))
    folders = [folder for bias, folder in bias_folder_pairs]
    for folder, color in zip(folders, colors):
        
        
        full_path = os.path.join(IVCURVES_DIR, folder)
        bias = extract_bias(folder)

        if not os.path.isdir(full_path):
            continue

        bias = extract_bias(folder)
        if bias is None:
            continue  # skip unrelated folders

        data_dir = os.path.join(full_path, "data")
        voltages, currents = load_iv_data(data_dir)

        if voltages is None or currents is None:
            print(f"Skipping {folder}: missing CSV files")
            continue
        
        if extract_bias(folder) == 0:
            plt.plot(voltages[60:-60], currents[60:-60], label=f"{int(bias)} mV", color="k")
        else:
            plt.plot(voltages[60:-60], currents[60:-60], label=f"{int(bias)} mV", color=color) 

    plt.xlabel("Voltage (V)")
    plt.ylabel("Current (nA)")
    plt.title("IV Curves for 3T RNPU + Resistor for All Biases")
    plt.legend(title="Bias Voltage")
    plt.axhline(0, color='k', alpha=0.4)
    plt.axvline(0, color='k', alpha=0.4)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
