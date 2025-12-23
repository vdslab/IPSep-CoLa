import argparse
import csv
import itertools

import matplotlib.pyplot as plt

from dataclasses import dataclass

@dataclass
class OutputRow:
    graph_size_n : int
    baseline_name : str
    baseline_stress : float
    proposed_name : str
    proposed_stress : float
    reduction_rate : float


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_file")
    parser.add_argument("out")
    parser.add_argument("--methods", nargs=2, required=True)
    args = parser.parse_args()

    data = [row for row in csv.DictReader(open(args.csv_file))]
    data.sort(key=lambda row: (row["method"], int(row["n"])))
    labels = sorted({int(row["n"]) for row in data})
    values = {method: [] for method in args.methods}
    for method, method_rows in itertools.groupby(data, lambda row: row["method"]):
        if method not in args.methods:
            continue
        for _, rows in itertools.groupby(method_rows, lambda row: int(row["n"])):
            values[method].append([float(row["value"]) for row in list(rows)])
    # Compute stress ratios
    outputs:list[list[OutputRow]] = []
    baseline = args.methods[0]
    proposed = args.methods[1]
    for i in range(len(labels)):
        baseline_values = values[baseline][i]
        proposed_values = values[proposed][i]
        outs_by_n:list[OutputRow] = []
        for b, p in zip(baseline_values, proposed_values):
            outs_by_n.append(
                OutputRow(
                    graph_size_n=labels[i],
                    baseline_name=baseline,
                    baseline_stress=b,
                    proposed_name=proposed,
                    proposed_stress=p,
                    reduction_rate=(b - p) / b,
                )
            )

        outputs.append(outs_by_n)

    import os

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(
            [
                "graph_size_n",
                "baseline_name",
                "baseline_stress",
                "proposed_name",
                "proposed_stress",
                "reduction_rate",
            ]
        )
        for outs_by_n in outputs:
            for out in outs_by_n:
                writer.writerow(
                    [
                        out.graph_size_n,
                        out.baseline_name,
                        out.baseline_stress,
                        out.proposed_name,
                        out.proposed_stress,
                        out.reduction_rate,
                    ]
                )

if __name__ == "__main__":
    main()
