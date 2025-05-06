from collections import defaultdict
from itertools import combinations


FILE_PATH = "../data/Chicago_Crimes_2001_to_2017_utility.txt"
MIN_UTIL = 500000.0


def parse_file(file_path):
    parsed_trans = []
    TWU = defaultdict(float)
    with open(file_path, 'r') as f:
        for tid, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            items = list(map(int, parts[0].split()))
            total_util = float(parts[1])
            item_utils = list(map(float, parts[2].split()))
            parsed_trans.append((tid, items, item_utils, total_util))
            for item in items:
                TWU[item] += total_util
    return parsed_trans, TWU


def generate_candidates(prev_freq, k):
    all_items = {i for subset in prev_freq for i in subset}
    candidates = set()
    for combo in combinations(sorted(all_items), k):
        if all(tuple(s) in prev_freq for s in combinations(combo, k-1)):
            candidates.add(combo)
    return candidates


def filter_by_twu(candidates, parsed_trans, minutil):
    twu_map = defaultdict(float)
    for _, items, _, tot in parsed_trans:
        for cand in candidates:
            if set(cand).issubset(items):
                twu_map[cand] += tot
    return {cand for cand, twu in twu_map.items() if twu >= minutil}


def compute_exact_utils(candidates, parsed_trans, minutil):
    util_map = {cand: 0.0 for cand in candidates}
    for _, items, item_utils, _ in parsed_trans:
        item2util = dict(zip(items, item_utils))
        for cand in candidates:
            if set(cand).issubset(items):
                util_map[cand] += sum(item2util[i] for i in cand)
    return {c: u for c, u in util_map.items() if u >= minutil}


def get_high_utility_itemsets(file_path, minutil):
    parsed_trans, TWU = parse_file(file_path)

    freq = {(item,) for item, twu in TWU.items() if twu >= minutil}
    all_cands = set(freq)
    k = 2
    prev_freq = freq
    while prev_freq:
        cands_k = generate_candidates(prev_freq, k)
        prev_freq = filter_by_twu(cands_k, parsed_trans, minutil)
        all_cands |= prev_freq
        k += 1

    print(f"Two Phase cands @{minutil}: {len(all_cands)}")

    huis = compute_exact_utils(all_cands, parsed_trans, minutil)
    return huis


def run():
    huis = get_high_utility_itemsets(FILE_PATH, MIN_UTIL)
    print(f"Run complete: found {len(huis)} HUIs @ {MIN_UTIL}")
    return huis


if __name__ == '__main__':
    run()