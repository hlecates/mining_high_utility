import time
import matplotlib.pyplot as plt

from two_phase import get_high_utility_itemsets as two_phase
from ihup import get_high_utility_itemsets as ihup_tree
from hui import get_high_utility_itemsets as huiminer
from up_growth import get_high_utility_itemsets as up_growth

#FILE_PATH = "../data/test.txt"
#FILE_PATH = "../data/Chicago_Crimes_2001_to_2017_utility.txt"
FILE_PATH = "../data/liquor_11.txt"
PERCENT_THRESHOLDS = [i / 1000 for i in range(1, 11)]  # [0.001, 0.002, ..., 0.010]

def compute_total_utility(file_path):
    total = 0.0
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            total += float(parts[1])
    return total


def measure_runtime(func, file_path, thresholds):
    runtimes = []
    for mu in thresholds:
        start = time.perf_counter()
        func(file_path, mu)
        end = time.perf_counter()
        runtimes.append(end - start)
        print(f"{func.__name__} @ {mu}: {end - start:.2f}s")
    return runtimes


def main():
    total_util = compute_total_utility(FILE_PATH)
    min_utils = [p * total_util for p in PERCENT_THRESHOLDS]
    print(min_utils)

    up_times = measure_runtime(up_growth, FILE_PATH, min_utils)
    tp_times = measure_runtime(two_phase, FILE_PATH, min_utils)
    ihup_times = measure_runtime(ihup_tree, FILE_PATH, min_utils)
    hui_times = measure_runtime(huiminer, FILE_PATH, min_utils)

    plt.figure()
    plt.plot(PERCENT_THRESHOLDS, up_times, marker='d', label='UP-Growth')
    plt.plot(PERCENT_THRESHOLDS, tp_times, marker='o', label='Two-Phase (TWU)')
    plt.plot(PERCENT_THRESHOLDS, ihup_times, marker='s', label='IHUP-tree')
    plt.plot(PERCENT_THRESHOLDS, hui_times, marker='^', label='HUI-Miner')
    plt.xlabel('Minimum Utility Threshold')
    plt.ylabel('Runtime (seconds)')
    plt.title('Runtime vs. min_util for HUI Algorithms')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig('results/runtime_experiments.png')
    plt.show()


if __name__ == '__main__':
    main()
