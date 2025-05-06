from collections import defaultdict

FILE_PATH = "../data/test.txt"
MIN_UTIL = 10

def parse_transactions(lines, TWU, parsed_trans):
    for tid, line in enumerate(lines):
        parts = line.split(':')
        items = list(map(int, parts[0].split()))
        total_util = float(parts[1])
        item_utils = list(map(float, parts[2].split()))
        parsed_trans.append((tid, items, item_utils, total_util))
        for item in items:
            TWU[item] += total_util


def revise(parsed_trans, TWU, minutil):
    revised = []
    # keep items meeting TWU
    kept = {item for item, tw in TWU.items() if tw >= minutil}
    # order by (TWU, item)
    order = {item: idx for idx, item in enumerate(sorted(kept, key=lambda i: (TWU[i], i)))}
    for tid, items, utils, _ in parsed_trans:
        filtered = [(item, util) for item, util in zip(items, utils) if item in kept]
        filtered.sort(key=lambda x: order[x[0]])
        if filtered:
            revised.append((tid, filtered))
    return revised


def build_utility_lists(revised_trans):
    ULs = {}
    for tid, seq in revised_trans:
        items, utils = zip(*seq)
        n = len(items)
        for idx, item in enumerate(items):
            iu = utils[idx]
            ru = sum(utils[idx+1:])
            ULs.setdefault(item, []).append((tid, iu, ru))
    return ULs


def construct(prefix_ul, x_ul, y_ul):
    new_ul = []
    mapY = {tid: (tid, iu, ru) for tid, iu, ru in y_ul}
    mapP = {tid: (tid, iu, ru) for tid, iu, ru in prefix_ul} if prefix_ul else {}
    for tid, iu_x, ru_x in x_ul:
        y_entry = mapY.get(tid)
        if not y_entry:
            continue
        _, iu_y, ru_y = y_entry
        if prefix_ul:
            _, iu_p, _ = mapP[tid]
            new_iu = iu_x + iu_y - iu_p
        else:
            new_iu = iu_x + iu_y
        if new_iu + ru_y >= 0:  # keep entry; ru bound applied later
            new_ul.append((tid, new_iu, ru_y))
    return new_ul


def huiMiner(prefix, ULs, minutil, prefix_ul=None, results=None):
    if results is None:
        results = []
    for i, (item, xUL) in enumerate(ULs):
        new_pref = prefix + (item,)
        sumIU = sum(iu for _, iu, _ in xUL)
        sumIU_RU = sum(iu + ru for _, iu, ru in xUL)
        if sumIU >= minutil:
            results.append((new_pref, sumIU))
        if sumIU_RU >= minutil:
            exts = []
            for y_item, yUL in ULs[i+1:]:
                newUL = construct(prefix_ul or [], xUL, yUL)
                if newUL:
                    exts.append((y_item, newUL))
            if exts:
                huiMiner(new_pref, exts, minutil, xUL, results)
    return results


def get_high_utility_itemsets(file_path, minutil):
    TWU = defaultdict(float)
    parsed_trans = []  # will hold (tid, items, item_utils, total_util)
    with open(file_path, 'r') as f:
        for tid, raw in enumerate(f):
            line = raw.strip()
            if not line:
                continue
            items_s, tot_s, utils_s = line.split(':')
            items = list(map(int, items_s.split()))
            total_util = float(tot_s)
            item_utils = list(map(float, utils_s.split()))

            parsed_trans.append((tid, items, item_utils, total_util))
            for i in items:
                TWU[i] += total_util

    revised = revise(parsed_trans, TWU, minutil)

    UL_map = build_utility_lists(revised)

    sorted_ULs = sorted(UL_map.items(), key=lambda x: TWU[x[0]])
    huis = huiMiner(tuple(), sorted_ULs, minutil)

    return huis


def run():
    results = get_high_utility_itemsets(FILE_PATH, MIN_UTIL)
    print(f"Run complete: found {len(results)} HUIs @ {MIN_UTIL}")
    print(results)
    return results


if __name__ == '__main__':
    run()