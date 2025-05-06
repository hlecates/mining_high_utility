FILE_PATH = "../data/Chicago_Crimes_2001_to_2017_utility.txt"
MIN_UTIL = 500000

class Node:
    def __init__(self, item, twu, tf=1, parent=None):
        self.item = item
        self.twu = twu
        self.tf = tf # unused, an optional way to order 
        self.parent = parent
        self.children = {}
        self.node_link = None

    def increment_vals(self, twu, tf=1):
        self.twu += twu
        self.tf += tf

class IHUPTree:
    def __init__(self):
        self.root = Node(item=None, twu=0, tf=0)
        self.header_table = {}

    def update_header(self, node):
        if node.item in self.header_table:
            current = self.header_table[node.item]
            while current.node_link:
                current = current.node_link
            current.node_link = node
        else:
            self.header_table[node.item] = node

    def insert_transaction(self, transaction, transaction_utility):
        current = self.root
        for item in transaction:
            if item in current.children:
                child = current.children[item]
                child.increment_vals(transaction_utility)
            else:
                child = Node(item, transaction_utility, parent=current)
                current.children[item] = child
                self.update_header(child)
            current = child

def get_prefix_path(node):
    path = []
    current = node.parent
    while current and current.item is not None:
        path.insert(0, current.item)
        current = current.parent
    return path

def get_projected_tree(full_tree, item):
    proj = IHUPTree()
    current = full_tree.header_table.get(item)
    while current:
        prefix = get_prefix_path(current)
        if prefix:
            proj.insert_transaction(prefix, current.twu)
        current = current.node_link
    return proj

def get_candidates(tree, minutil, prefix, candidates):
    for item in sorted(tree.header_table.keys(), key=int):
        new_cand = prefix + [item]
        # sum TWU over all occurrences
        twu_sum = 0
        node = tree.header_table[item]
        while node:
            twu_sum += node.twu
            node = node.node_link
        if twu_sum < minutil:
            continue
        key = tuple(sorted(new_cand, key=int))
        candidates[key] = twu_sum
        proj = get_projected_tree(tree, item)
        if proj.root.children:
            get_candidates(proj, minutil, new_cand, candidates)

def exact_high_utils(candidates, transactions, minutil):
    trans_map = [dict(zip(items, utils)) for items, utils in transactions]
    high_utils = {}
    for cand in candidates:
        cand_set = set(cand)
        util = 0.0
        for map in trans_map:
            if cand_set <= map.keys():
                util += sum(map[i] for i in cand)
        if util >= minutil:
            high_utils[cand] = util

    return high_utils


def get_high_utility_itemsets(file_path, minutil):
    transactions = [] 
    tree = IHUPTree()
    with open(file_path, 'r') as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            parts = line.split(':')
            raw_items = parts[0].split()
            total_util = float(parts[1])
            raw_utils = list(map(float, parts[2].split()))
            paired = sorted(zip(raw_items, raw_utils), key=lambda x: int(x[0]))
            items = [item for item, _ in paired]
            utils = [utility for _, utility in paired]        
            items, utils = list(items), list(utils)

            transactions.append((items, utils))

            tree.insert_transaction(items, total_util) 

    candidates = {}
    get_candidates(tree, minutil, [], candidates)

    print(f"IHUP cands @{minutil}: {len(candidates)}")

    results = exact_high_utils(candidates, transactions, minutil)
    return results


def run():
    results = get_high_utility_itemsets(FILE_PATH, MIN_UTIL)
    print(f"Run complete: found {len(results)} HUIs @ {MIN_UTIL}")
    return results

if __name__ == '__main__':
    run()