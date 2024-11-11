import datetime
import glob
import json
import os


def violation_constraints(
    position, constraints: list[list[int]], axis: int = 1
) -> list[float]:
    violations = []
    for l, r, g in constraints:
        yl = position[l][axis]
        yr = position[r][axis]
        # print(yr - yl, g - (yr - yl))
        # if yr - yl < g:
        violations.append(g - (yr - yl))
    return violations


def sgd():
    d_today = datetime.date.today()
    t_now = datetime.datetime.now().time()
    vilation_dir = "src/data/align/violation"
    os.makedirs(vilation_dir, exist_ok=True)

    position_dir = "src/data/align/sgd"
    graph_dir = "src/data/json/random_tree/2024-10-27/07:07:06.283826"
    "100/node_n=100_0.json"

    for node_n in range(100, 101, 100):
        with open(f"{position_dir}/stress_potition_{node_n}.json") as f:
            json_data = json.load(f)
            positions = json_data["positions"]
        violations = []
        for i, position in enumerate(positions):
            with open(f"{graph_dir}/{node_n}/node_n={node_n}_{i}.json") as f:
                json_data = json.load(f)
                graph_constraints = json_data["graph"]["constraints"]
                length = json_data["length"]
            constrains = [[], []]
            for constraint in graph_constraints:
                constrains[1 if constraint["axis"] == "y" else 0].append(
                    [constraint["left"], constraint["right"], constraint["gap"]]
                )
            _v = []
            for i in range(2):
                _v.extend(
                    violation_constraints(position, constraints=constrains[i], axis=i)
                )
            # print(node_n, i, sum(_violations), _violations)
            violations.append(_v)

            with open(f"{vilation_dir}/fullsgd_{node_n}.json", "w") as f:
                json.dump(
                    violations,
                    f,
                    indent=2,
                )


def webcola():
    d_today = datetime.date.today()
    t_now = datetime.datetime.now().time()
    vilation_dir = "src/data/align/violation"
    os.makedirs(vilation_dir, exist_ok=True)

    basedir = "src/data/align/cola"
    # position_dir = "src/data/json/2024-10-21/random_tree/03:20:28.536389"
    graph_dir = "src/data/json/random_tree/2024-10-27/07:07:06.283826"
    "100/node_n=100_0.json"

    for node_n in range(100, 2001, 100):
        position_dir = f"{basedir}/{node_n}"
        files = [file for file in glob.glob(f"{position_dir}/*.json")]
        files.sort()
        positions = []
        for file in files:
            with open(file) as f:
                json_data = json.load(f)
                nodes = json_data["nodes"]
                position = {node["index"]: [node["x"], node["y"]] for node in nodes}
                position = [position[i] for i in range(len(position))]
                positions.append(position)
        # print(files)
        violations = []
        for i, position in enumerate(positions):
            with open(f"{graph_dir}/{node_n}/node_n={node_n}_{i}.json") as f:
                json_data = json.load(f)
                graph_constraints = json_data["graph"]["constraints"]
                length = json_data["length"]
            constrains = [[], []]
            for constraint in graph_constraints:
                constrains[0 if constraint["axis"] == "y" else 1].append(
                    [constraint["left"], constraint["right"], length]
                )
            _violations = violation_constraints(
                position, constraints=constrains[1], axis=1
            )
            # print(node_n, i, sum(_violations), _violations)
            violations.append(_violations)

            with open(f"{vilation_dir}/webcola_{node_n}.json", "w") as f:
                json.dump(
                    violations,
                    f,
                    indent=2,
                )


if __name__ == "__main__":
    # sgd()
    webcola()
