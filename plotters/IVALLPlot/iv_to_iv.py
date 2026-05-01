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
FOLDER_RESISTOR_REGEX = r"IV_RNPU_3T_R_([+-]?[0-9\.]+)mV-"
FOLDER_REGEX = r"IV_RNPU_([+-]?[0-9\.]+)mV-"

def extract_bias_resistor(foldername):
    match = re.search(FOLDER_RESISTOR_REGEX, foldername)
    if match:
        return float(match.group(1))
    return None

def extract_bias_noRes(foldername):
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

    bias_folder_pairs_noRes = []

    for folder_res in os.listdir(IVCURVES_DIR):
        full_path = os.path.join(IVCURVES_DIR, folder_res)
        if not os.path.isdir(full_path):
            continue

        bias = extract_bias_noRes(folder_res)
        if bias is not None:
            bias_folder_pairs_noRes.append((bias, folder_res))

    bias_folder_pairs_noRes.sort(key=lambda x: x[0], reverse=True)


    bias_folder_pairs_resistor = []

    for folder_res in os.listdir(IVCURVES_DIR):
        full_path = os.path.join(IVCURVES_DIR, folder_res)
        if not os.path.isdir(full_path):
            continue

        bias = extract_bias_resistor(folder_res)
        if bias is not None:
            bias_folder_pairs_resistor.append((bias, folder_res))

    bias_folder_pairs_resistor.sort(key=lambda x: x[0], reverse=True)


    folders_res = [folder for bias, folder in bias_folder_pairs_resistor]

    folders_noRes = [folder for bias, folder in bias_folder_pairs_noRes]

    for folder_res, folder_noRes in zip(folders_res, folders_noRes):
        
        plt.figure(figsize=(5, 4))

        full_path = os.path.join(IVCURVES_DIR, folder_res)
        bias = extract_bias_resistor(folder_res)
        data_dir = os.path.join(full_path, "data")
        voltages_res, currents_res = load_iv_data(data_dir)

        full_path = os.path.join(IVCURVES_DIR, folder_noRes)
        bias = extract_bias_noRes(folder_noRes)
        data_dir = os.path.join(full_path, "data")
        voltages_noRes, currents_noRes = load_iv_data(data_dir)
        
        plt.plot(voltages_res[60:-60], currents_res[60:-60], label=f"With 10MOhm Resistor") # type: ignore
        plt.plot(voltages_noRes[60:-60], currents_noRes[60:-60], label=f"No Resistor") # type: ignore

        plt.xlabel("Voltage (V)")
        plt.ylabel("Current (nA)")
        plt.title(f"IV Curves for 3T RNPU + Resistor for {bias}mV")
        plt.legend()
        plt.axhline(0, color='k', alpha=0.4)
        plt.axvline(0, color='k', alpha=0.4)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"output/25-02-2026/PLOT_IV_BIAS_{bias}mV.png")


if __name__ == "__main__":
    main()
