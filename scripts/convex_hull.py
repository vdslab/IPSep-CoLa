import argparse
import csv
import json
import os
from pathlib import Path

from scipy.spatial import ConvexHull


class Arg(argparse.Namespace):
    drawing_file: str
    out_csv: str
    create: bool


header = ["method", "node_count", "xrange", "yrange", "area", "filepath"]


def file_create(filepath, header):
    if os.path.exists(filepath):
        return

    with open(filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerow(header)


def append(filepath, line):
    with open(filepath, "a") as f:
        writer = csv.writer(f)
        writer.writerow(line)


def record_convexhull_volume(points, method, filepath):
    hull = ConvexHull(points)
    hull.volume


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("drawing_file")
    parser.add_argument("out_csv")
    parser.add_argument("--create", action=argparse.BooleanOptionalAction)
    args: Arg = parser.parse_args()

    pos: dict[str, list[float]] = json.load(open(args.drawing_file))
    points = list(pos.values())

    if args.create:
        file_create(args.out_csv, header)

    drawing_file = Path(args.drawing_file)
    node_count = drawing_file.parent.name
    parts = drawing_file.parts
    method = parts[parts.index("drawing") + 2]
    hull = ConvexHull(points)
    hull.volume
    xs, ys = zip(*points)
    xrange = max(xs) - min(xs)
    yrange = max(ys) - min(ys)
    # print(max(xs), min(xs), max(ys), min(ys))
    record = [method, node_count, xrange, yrange, hull.volume, str(drawing_file)]
    append(args.out_csv, record)


if __name__ == "__main__":
    main()
