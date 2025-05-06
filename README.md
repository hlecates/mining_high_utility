## High Utility Itemset Mining
High-utility itemset mining seeks to find itemsets in transactional data whose total **utility** (e.g., profit, weight, or importance) exceeds a user-defined threshold. Unlike frequency-based mining, high-utility itemset mining must handle non-monotonicity and the lack of the downward-closure property, which requires specialized algorithms for efficiency and scalability.

This repository included four distinct high utility itemset mining algorithm implementations, alongside experiment scripts and empirical results.

# Algorithms
All standalone implementations are provided as interactive Jupyter notebooks for ease of exploration, comparison, and modularity:
- **Two-Phase TWU/Apriori**: The classic two-phase approach using transaction-weighted utility (TWU).  
- **IHUP**: The Improved High-Utility Pattern mining tree algorithm.  
- **UP-Growth**: A single-phase, pattern-growth method with global and local pruning (DGU, DGN, DLU, DLM).  
- **HUI-Miner**: Utility-list based mining via remaining utility estimates.  

# Experiments
Individual Python files of each algorithm and experiment scripts are housed in the experiments directory. Within each individual Python file, changes were made to the structure of the implmentations in order to improve modularity, paramter passing and logging. Furthermore, the experiment scripts include runtime, scalability, candidate comparisons and recursion tests/comparisons, as well as the associated plot generation. Contained in experiments directory are several generated plots showing empirical results, aligning with the current high-utility itemset mining literature.
