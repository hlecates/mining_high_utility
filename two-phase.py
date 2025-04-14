def standard_two_phase(transactions, profits, min_utility):
    """
    Standard two-phase high utility itemset mining.
    Phase 1: Generate candidates level-by-level using TWU by scanning the database for each candidate.
    Phase 2: Re-scan the database for each candidate to compute its exact utility.
    
    This implementation is intentionally naive (and slow) for demonstration purposes.
    
    Args:
        transactions (list of dict): Each transaction is a dict of {item: quantity}.
        profits (dict): Profit (utility) for each item.
        min_utility (numeric): The minimum utility threshold.
        
    Returns:
        List of tuples (itemset, actual_utility) for each high utility itemset.
    """
    # Precompute the total utility of each transaction.
    transaction_utils = [sum(profits[item] * qty for item, qty in trans.items())
                         for trans in transactions]
    # For faster membership tests later, create a list of sets of items per transaction.
    trans_itemsets = [set(trans.keys()) for trans in transactions]
    
    # --- Phase 1: Generate candidate itemsets using TWU ---
    # Start with 1-itemset candidates.
    unique_items = set()
    for trans in transactions:
        unique_items.update(trans.keys())
    candidate_level = []
    for item in sorted(unique_items):
        # Compute TWU: if the item is in the transaction, add that transaction's total utility.
        twu = 0
        for tid, items in enumerate(trans_itemsets):
            if item in items:
                twu += transaction_utils[tid]
        if twu >= min_utility:
            candidate_level.append((item,))
    all_candidates = candidate_level[:]
    
    # Generate candidates of length >= 2.
    k = 2
    while candidate_level:
        next_level = []
        n = len(candidate_level)
        # Join two candidates from the current level if they share the first k-1 items.
        for i in range(n):
            for j in range(i + 1, n):
                a = candidate_level[i]
                b = candidate_level[j]
                if a[:-1] == b[:-1]:
                    new_candidate = tuple(sorted(set(a) | set(b)))
                    if len(new_candidate) == k:
                        # Compute TWU for the new candidate by scanning every transaction.
                        twu = 0
                        for tid, items in enumerate(trans_itemsets):
                            if set(new_candidate).issubset(items):
                                twu += transaction_utils[tid]
                        if twu >= min_utility and new_candidate not in next_level:
                            next_level.append(new_candidate)
        candidate_level = sorted(next_level)
        all_candidates.extend(candidate_level)
        k += 1

    # --- Phase 2: Exact utility computation ---
    high_utility_itemsets = []
    for candidate in all_candidates:
        actual_util = 0
        for tid, trans in enumerate(transactions):
            if set(candidate).issubset(trans.keys()):
                # Compute the actual utility in this transaction.
                actual_util += sum(profits[item] * trans[item] for item in candidate)
        if actual_util >= min_utility:
            high_utility_itemsets.append((candidate, actual_util))
    
    return high_utility_itemsets
