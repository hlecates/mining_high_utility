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


def huiminer_one_phase_from_parsed(parsed_transactions, min_utility):
    """
    One-phase HUI-Miner algorithm implementation that uses utility lists.
    Operates on parsed transactions where each transaction is represented as:
      (trans_dict, ordered_items, ordered_utilities, total_utility)
    In this adaptation, we use the provided item utility values directly.
    
    Steps:
      1. Compute TWU for each item and filter out items with TWU below min_utility.
      2. Order the promising items globally (by descending TWU).
      3. For each transaction, retain only promising items in the given order.
      4. Build initial utility lists for each single promising item.
      5. Recursively extend itemsets via intersection of utility lists, computing exact utilities,
         and prune using the (iutil + rutil) upper bound.
    """
    # --- Step 1: Compute TWU and filter items ---
    # TWU: sum of provided transaction total utility for transactions where the item appears.
    item_twu = {}
    for tid, (trans_dict, _, _, total_util) in enumerate(parsed_transactions):
        for item in trans_dict:
            item_twu[item] = item_twu.get(item, 0) + total_util
    promising_items = [item for item, twu in item_twu.items() if twu >= min_utility]
    if not promising_items:
        return []

    # --- Step 2: Order promising items globally by descending TWU (if equal, by item id) ---
    promising_items.sort(key=lambda x: (-item_twu[x], x))
    item_order_index = {item: idx for idx, item in enumerate(promising_items)}

    # --- Step 3: Revise transactions: keep only promising items in global order ---
    # We use the ordered_items from the parsed data.
    revised_transactions = []
    for tid, (trans_dict, ordered_items, ordered_utilities, _) in enumerate(parsed_transactions):
        # Filter items: keep only if item is promising.
        filtered_items = [item for item in ordered_items if item in item_order_index]
        if not filtered_items:
            continue
        # Sort by global order (as defined by item_order_index)
        filtered_items.sort(key=lambda x: item_order_index[x])
        # Build list of (item, utility) using the original utility info from trans_dict.
        items_with_util = [(item, trans_dict[item]) for item in filtered_items]
        revised_transactions.append((tid, items_with_util))

    # --- Step 4: Build initial utility lists for each single promising item ---
    # Utility list entry: (tid, iutil, rutil)
    # iutil: utility of the item in the transaction.
    # rutil: sum of utilities of items coming after it in the transaction.
    utility_lists = {}  # item -> list of utility list entries.
    for tid, items_with_util in revised_transactions:
        # Compute utilities list (simply the provided values) and compute a suffix sum for rutil.
        utilities = [util for _, util in items_with_util]
        suffix_sum = 0.0
        suffix_util = [0.0] * len(items_with_util)
        for idx in range(len(items_with_util) - 1, -1, -1):
            suffix_util[idx] = suffix_sum
            suffix_sum += utilities[idx]
        # For each item in the transaction, add an entry to its utility list.
        for idx, (item, util) in enumerate(items_with_util):
            entry = (tid, util, suffix_util[idx])
            utility_lists.setdefault(item, []).append(entry)
    # Sort each utility list by transaction id.
    for item in utility_lists:
        utility_lists[item].sort(key=lambda x: x[0])

    high_utility_itemsets = []

    def search(prefix, ul_prefix, start_index):
        """
        Recursive DFS to extend prefix using utility lists.
         - prefix: current itemset (tuple)
         - ul_prefix: utility list of current prefix.
         - start_index: index in promising_items from which to try extensions.
        """
        total_util = sum(entry[1] for entry in ul_prefix)
        # If current prefix is nonempty and qualifies, add it.
        if prefix and total_util >= min_utility:
            high_utility_itemsets.append((prefix, total_util))
        # Prune if even the upper bound (iutil + rutil) is less than min_utility.
        if sum(entry[1] + entry[2] for entry in ul_prefix) < min_utility:
            return
        # Try to extend with items from promising_items (in global order).
        for idx in range(start_index, len(promising_items)):
            item = promising_items[idx]
            ul_item = utility_lists.get(item, [])
            if not ul_item:
                continue
            # Construct the new utility list for prefix ∪ {item} by intersecting ul_prefix and ul_item.
            new_ul = []
            i, j = 0, 0
            while i < len(ul_prefix) and j < len(ul_item):
                tid_p, iutil_p, rutil_p = ul_prefix[i]
                tid_i, iutil_i, rutil_i = ul_item[j]
                if tid_p == tid_i:
                    # In the same transaction, combine utilities.
                    new_iutil = iutil_p + iutil_i
                    new_entry = (tid_p, new_iutil, rutil_i)
                    new_ul.append(new_entry)
                    i += 1
                    j += 1
                elif tid_p < tid_i:
                    i += 1
                else:
                    j += 1
            if not new_ul:
                continue
            search(prefix + (item,), new_ul, idx + 1)

    # --- Step 5: Start the recursive search for each single promising item ---
    for idx, item in enumerate(promising_items):
        ul_item = utility_lists.get(item, [])
        if not ul_item:
            continue
        # Prune if the maximum possible utility (iutil + rutil) is below threshold.
        if sum(entry[1] + entry[2] for entry in ul_item) < min_utility:
            continue
        search((item,), ul_item, idx + 1)
    return high_utility_itemsets