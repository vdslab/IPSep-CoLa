import argparse
import json
import os

import networkx as nx


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dest", default=".")
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()
    print(args.input)
    print("test")

    for filepath in args.input:
        graph = nx.node_link_graph(json.load(open(filepath)), link="links")
        x_constraints = [
            c for c in graph.graph["constraints"] if c.get("axis", "") == "x"
        ]
        x_constraints.extend(
            [
                {
                    "axis": c["axis"],
                    "gap": -c["gap"],
                    "left": c["right"],
                    "right": c["left"],
                }
                for c in graph.graph["constraints"]
                if c.get("axis", "") == "x"
            ]
        )
        y_constraints = [
            c for c in graph.graph["constraints"] if c.get("axis", "") == "y"
        ]
        y_constraints.extend(
            [
                {
                    "axis": c["axis"],
                    "gap": -c["gap"],
                    "left": c["right"],
                    "right": c["left"],
                }
                for c in graph.graph["constraints"]
                if c.get("axis", "") == "y"
            ]
        )
        constraint = x_constraints + y_constraints
        graph.graph["constraints"] = constraint

        basename = os.path.basename(filepath)
        os.makedirs(args.dest, exist_ok=True)
        filepath = os.path.join(args.dest, basename)
        with open(filepath, "w") as f:
            json.dump(nx.node_link_data(graph), f)


if __name__ == "__main__":
    main()
