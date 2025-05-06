import matplotlib.pyplot as plt

# To preserve the general structure of .py algos codebases, these values where retrieved through 
# print statements when runing the runtime experiments, and recorded
#up_cands = [3869, 1937, 1232, 905, 701, 573, 474, 413, 362, 315]
#tp_cands = [4022, 2031, 1306, 963, 752, 614, 514, 454, 391, 346]
#ihup_cands = [4022, 2031, 1306, 963, 752, 614, 514, 454, 391, 346]

up_cands = [15276, 5043, 2663, 1655, 1144, 836, 661, 513, 429, 359]
tp_cands = [16722, 5721, 3127, 2010, 1419, 1077, 832, 688, 576, 486]
ihup_cands = [16722, 5721, 3127, 2010, 1419, 1077, 832, 688, 576, 486]

PERCENT_THRESHOLDS = [i / 1000 for i in range(1, 11)]
[7941.285, 15882.57, 23823.855, 31765.14, 39706.425, 47647.71, 55588.995, 63530.28, 71471.56499999999, 79412.85]

def main():
    plt.figure()
    plt.plot(PERCENT_THRESHOLDS, up_cands, marker='d', label='UP-Growth')
    plt.plot(PERCENT_THRESHOLDS, tp_cands, marker='o', label='Two-Phase (TWU)')
    plt.plot(PERCENT_THRESHOLDS, ihup_cands, marker='s', label='IHUP-tree')

    plt.xlabel('Minimum Utility Threshold')
    plt.ylabel('Number of Candidate Itemsets Generated')
    plt.title('Candidates vs. min_util for Two-Phase HUI Algorithms')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plt.savefig('results/cand_experiments.png')
    plt.show()

if __name__ == '__main__':
    main()

