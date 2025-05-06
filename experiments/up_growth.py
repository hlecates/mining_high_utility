FILE_PATH = "../../data/Chicago_Crimes_2001_to_2017_utility.txt"
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

class UPTree:
    def __init__(self):
        self.root = Node(item=None, twu=0, tf=0)
        self.header_table = {}   # item -> first node
        self.header_list = []    # populated once TWU known
        self.min_item_util = {}  # global min-item-utility map for DLU

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
        for idx, (item, ut) in enumerate(transaction):
            # DGN, subtract minimal utility of descendants
            rem_min = 0
            for j, _ in transaction[idx+1:]:
                rem_min += self.min_item_util.get(j, 0)
            node_util = transaction_utility - rem_min

            # If Node exists add and increment values, if not create a new one
            if item in current.children:
                child = current.children[item]
                child.increment_vals(node_util)
            else:
                child = Node(item, node_util, parent=current)
                current.children[item] = child
                self.update_header(child)
            current = child

    def insert_local_transaction(self, path, path_util, count):
        current = self.root
        for idx, item in enumerate(path):
            # DLN: remove contributions of later items in this path
            rem_min = 0
            for j in path[idx+1:]:
                rem_min += self.min_item_util.get(j, 0) * count
            node_util = path_util - rem_min
            
            # Continue creating the tre exactly as above
            if item in current.children:
                child = current.children[item]
                child.increment_vals(node_util)
            else:
                child = Node(item, node_util, parent=current)
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
    proj = UPTree()
    
    # Collect all prefix paths
    prefix_paths = []
    item_path_util = {}
    current = full_tree.header_table.get(item)
    while current:
        path = get_prefix_path(current)
        if path:
            prefix_paths.append((path, current.twu, current.tf))
            for p in path:
                if p not in item_path_util:
                    item_path_util[p] = 0
                item_path_util[p] += current.twu
        current = current.node_link

    # Build local tree with Discard local unpromising
    for path, path_util, count in prefix_paths:
        filtered = []
        adj_path_util = path_util
        for p in path:
            if item_path_util[p] >= MIN_UTIL:
                filtered.append(p)
            else:
                adj_path_util -= full_tree.min_item_util[p] * count
        filtered.sort(key=lambda x: (-item_path_util[x], int(x)))
        if filtered:
            proj.min_item_util = full_tree.min_item_util
            proj.insert_local_transaction(filtered, adj_path_util, count)

    proj.header_list = sorted(proj.header_table.keys(), key=lambda x: (-item_path_util[x], int(x)))
    return proj


def get_candidates(tree, minutil, prefix, candidates):
    for item in reversed(tree.header_list):
        path_util = 0
        current = tree.header_table[item]
        while current:
            path_util += current.twu
            current = current.node_link
        if path_util < minutil:
            continue
        key = tuple(prefix + [item])
        candidates[key] = path_util
        proj = get_projected_tree(tree, item)
        if proj.header_list:
            get_candidates(proj, minutil, prefix + [item], candidates)


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
    twu = {}
    transactions = []
    with open(file_path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line[0] in '#%@':
                continue
            parts = line.split(':')
            ids = parts[0].split()
            tu = float(parts[1])
            utils = list(map(float, parts[2].split()))
            transactions.append((ids, utils))
            for i in ids:
                if i not in twu:
                    twu[i] = 0
                twu[i] += tu


    # DGU pruning and create tree
    tree = UPTree()
    for ids, utils in transactions:
        filtered_items = []
        filtered_items_util = 0
        # Discard Global Unpromising, only items with TWU > min util
        for i, u in zip(ids, utils):
            if twu[i] >= minutil:
                filtered_items.append((i, u))
                filtered_items_util += u
                prev = tree.min_item_util.get(i)
                if prev is None or u < prev:
                    tree.min_item_util[i] = u
        filtered_items.sort(key=lambda x: (-twu[x[0]], int(x[0])))
        if filtered_items:
            tree.insert_transaction(filtered_items, filtered_items_util)

    # Create and sort the header_list, denoting which order items should be processed
    tree.header_list = sorted(tree.header_table.keys(),key=lambda x: (-twu[x], int(x)))

    candidates = {}
    get_candidates(tree, minutil, [], candidates)
    print(f"UPGrowth candidates @{minutil}: {len(candidates)}")

    results = exact_high_utils(candidates, transactions, minutil)
    return results

def run():
    results = get_high_utility_itemsets(FILE_PATH, MIN_UTIL)
    print(f"Run complete: found {len(results)} HUIs @ {MIN_UTIL}")
    return results

if __name__ == '__main__':
    run()
