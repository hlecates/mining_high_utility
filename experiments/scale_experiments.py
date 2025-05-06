import os
import time

import matplotlib.pyplot as plt

from two_phase import get_high_utility_itemsets as two_phase
from ihup import get_high_utility_itemsets as ihup_tree
from hui import get_high_utility_itemsets as huiminer
from up_growth import get_high_utility_itemsets as up_growth

FILE_PATH = "../data/liquor_11.txt"
#FILE_PATH = "../data/Chicago_Crimes_2001_to_2017_utility.txt"
SIZE_FRACTIONS = [0.1, 0.25, 0.5, 0.75, 1.0]  # 10%, 25%, 50%, 75%, 100%
FIXED_UTIL_THRESH = 0.005 
WORK_DIR = "subsamples" 

def compute_total_utility(path):
    total = 0.0
    with open(path) as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) < 2:
                continue
            total += float(parts[1])
    return total

def create_subsample(input_path, fraction, work_dir):
    os.makedirs(work_dir, exist_ok=True)
    subsample_path = os.path.join(work_dir, f"sub_{int(fraction*100)}.txt")
    with open(input_path) as src, open(subsample_path, 'w') as dst:
        all_lines = src.readlines()
        cutoff = int(len(all_lines) * fraction)
        dst.writelines(all_lines[:cutoff])
    return subsample_path

def measure_runtime_once(func, path, minutil):
    start = time.perf_counter()
    func(path, minutil)
    return time.perf_counter() - start

def main():
    total_util = compute_total_utility(FILE_PATH)
    minutil = FIXED_UTIL_THRESH * total_util

    subsamples = [(frac, create_subsample(FILE_PATH, frac, WORK_DIR)) for frac in SIZE_FRACTIONS]

    times = {'UP-Growth': [], 'Two-Phase': [], 'IHUP-tree': [], 'HUI-Miner': []}

    for frac, path in subsamples:
        print(f"Running on {int(frac*100)}%")
        times['UP-Growth'].append(measure_runtime_once(up_growth, path, minutil))
        times['Two-Phase'].append(measure_runtime_once(two_phase, path, minutil))
        times['IHUP-tree'].append(measure_runtime_once(ihup_tree, path, minutil))
        times['HUI-Miner'].append(measure_runtime_once(huiminer, path, minutil))

    labels = [f"{int(frac*100)}%" for frac in SIZE_FRACTIONS]
    
    plt.figure()
    for name, runtimes in times.items():
        plt.plot(labels, runtimes, marker='o', label=name)
    plt.xlabel("Dataset Size (% of full DB)")
    plt.ylabel("Runtime (seconds)")
    plt.title(f"Scalability (@ {FIXED_UTIL_THRESH*100:.1f}% threshold)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("results/scalability_experiments.png")
    plt.show()


if __name__ == '__main__':
    main()

