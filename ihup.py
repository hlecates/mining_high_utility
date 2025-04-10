def parse_dataset_lines(lines):
    """
    Parses lines in the dataset format:
      item1 item2 ... itemN : total_utility : util1 util2 ... utilN
    Returns a list of parsed transactions where each transaction is a tuple:
      (trans_dict, ordered_items, ordered_utilities, total_utility)
    - trans_dict: dictionary mapping item -> utility (float) for that transaction.
    - ordered_items: list of items in the order they appear.
    - ordered_utilities: list of corresponding utility values (floats).
    - total_utility: provided total utility for the transaction.
    """
    parsed_transactions = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(':')
        if len(parts) != 3:
            print("Skipping line (format error):", line)
            continue
        items_part = parts[0].strip()
        total_util_str = parts[1].strip()
        item_utils_part = parts[2].strip()

        # Parse items (convert to int for simplicity)
        item_tokens = items_part.split()
        ordered_items = [int(token) for token in item_tokens]
        # Parse total utility (float)
        total_util = float(total_util_str)
        # Parse item-level utilities
        util_tokens = item_utils_part.split()
        ordered_utilities = [float(tok) for tok in util_tokens]
        if len(ordered_items) != len(ordered_utilities):
            print("Warning: Number of items does not match number of utility values in line:", line)
            continue
        # Build dictionary for quick lookup (item -> utility) for this transaction.
        trans_dict = {item: util for item, util in zip(ordered_items, ordered_utilities)}
        parsed_transactions.append((trans_dict, ordered_items, ordered_utilities, total_util))
    return parsed_transactions


def ihup_two_phase_from_parsed(parsed_transactions, min_utility):
    """
    Two-Phase IHUP algorithm for high utility itemset mining.
    Operates on parsed transactions in which each transaction is represented as:
      (trans_dict, ordered_items, ordered_utilities, total_utility)
    Here:
      - trans_dict is a dict mapping each item (int) to its utility (float) in that transaction.
      - total_utility is the provided total utility of the transaction.
      
    Phase 1: Generate candidate itemsets based on Transaction-Weighted Utility (TWU).
    Phase 2: For each candidate, compute its exact utility (summing provided utility values)
             and report it if it meets min_utility.
    """
    # Build simpler structures: list of transaction dictionaries and the provided transaction utilities.
    transactions = []
    transaction_utils = []
    for (trans_dict, _, _, total_util) in parsed_transactions:
        transactions.append(trans_dict)
        transaction_utils.append(total_util)

    # --- Phase 1: Candidate Generation using TWU ---
    # Create mapping: item -> set of transaction indices in which the item appears.
    item_tidset = {}
    for tid, trans in enumerate(transactions):
        for item in trans:
            item_tidset.setdefault(item, set()).add(tid)
    # Compute TWU for each item (sum of total_utility for transactions where item appears)
    item_twu = {item: sum(transaction_utils[tid] for tid in tids)
                for item, tids in item_tidset.items()}
    # Initialize candidate list with single items meeting TWU threshold.
    prev_level = [ (item,) for item, twu in item_twu.items() if twu >= min_utility ]
    prev_level.sort()  # sort for consistent order
    # For each candidate itemset, record its tidset (the set of transaction indices where it appears)
    cand_tidsets = { (item,): item_tidset[item] for (item,) in prev_level }
    phase1_candidates = prev_level[:]  # all candidates at all levels
    k = 2

    # Candidate generation in a breadth-first style (join step)
    while prev_level:
        next_level = []
        next_tidsets = {}
        n = len(prev_level)
        for i in range(n):
            for j in range(i+1, n):
                itemset1 = prev_level[i]
                itemset2 = prev_level[j]
                # For k > 2, require first k-2 items to be equal (Apriori join condition)
                if k > 2 and itemset1[:-1] != itemset2[:-1]:
                    continue
                new_itemset = tuple(sorted(set(itemset1) | set(itemset2)))
                if new_itemset in next_tidsets:
                    continue  # already generated
                # Compute tidset of new_itemset as intersection of tidsets
                tidset_new = cand_tidsets[itemset1] & cand_tidsets[itemset2]
                if not tidset_new:
                    continue
                # Calculate TWU for new_itemset
                twu_new = sum(transaction_utils[tid] for tid in tidset_new)
                if twu_new >= min_utility:
                    next_level.append(new_itemset)
                    next_tidsets[new_itemset] = tidset_new
                    phase1_candidates.append(new_itemset)
        prev_level = sorted(next_level)
        cand_tidsets.update(next_tidsets)
        k += 1

    # --- Phase 2: Exact Utility Computation ---
    high_utility_itemsets = []
    for itemset in phase1_candidates:
        total_util = 0.0
        for tid in cand_tidsets[itemset]:
            # In each transaction, sum the provided utility values for items in the itemset.
            trans = transactions[tid]
            util = sum(trans[item] for item in itemset)
            total_util += util
        if total_util >= min_utility:
            high_utility_itemsets.append((itemset, total_util))
    return high_utility_itemsets
