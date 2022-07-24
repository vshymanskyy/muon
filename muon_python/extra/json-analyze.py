#!/usr/bin/env python3

from collections import Counter
from collections.abc import Mapping, Sequence

class JsonStats:
    def __init__(self):
        self._count = Counter()

    def add(self, val):
        if val is None:
            self._count.update(["null"])
        elif isinstance(val, float):
            self._count.update(["float"])
        elif isinstance(val, bool):
            self._count.update(["bool"])
        elif isinstance(val, int):
            self._count.update(["int"])
        elif isinstance(val, str):
            self._count.update(["string"])
        elif isinstance(val, Sequence):
            self._count.update(["list"])
            for v in val:
                self._count.update(["list-item"])
                self.add(v)
        elif isinstance(val, Mapping):
            self._count.update(["dict"])
            for k, v in val.items():
                self._count.update(["key"])
                self.add(v)
        else:
            raise Exception(f"Unknown type: {type(val)}")

    def most_common(self):
        return self._count.most_common()

if __name__ == '__main__':

    import sys, os
    import json
    import csv

    from tabulate import tabulate
    from collections import OrderedDict

    with open('./results/json-analyze.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'key', 'string', 'int', 'float', 'list-item', 'dict', 'list', 'bool', 'null', 'size']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        hdrs = OrderedDict()
        for i in fieldnames:
            hdrs[i] = i.capitalize()
        hdrs['size'] = "Size (Kb)"
        hdrs.move_to_end('size', last=False)
        hdrs.move_to_end('name', last=False)
        rows = [hdrs]

        for ifn in sys.argv[1:]:
            with open(ifn) as f:
                data = json.load(f)
                stats = JsonStats()
                stats.add(data)

                res = dict(stats.most_common())
                res["name"] = ifn.replace(".json", "").replace(".min", "")
                res["size"] = f'{(os.path.getsize(ifn)/1024):.2f}'

                writer.writerow(res)
                rows.append(res)

        print(tabulate(rows, headers="firstrow", tablefmt="github"))
