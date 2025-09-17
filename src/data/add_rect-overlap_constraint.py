import argparse
import json
import os


class Arg(argparse.Namespace):
    output: str
    input: str


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--input", required=True)
    args: Arg = parser.parse_args()
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    data = json.load(open(args.input))
    print(data["nodes"])
    for i in range(len(data["nodes"])):
        data["nodes"][i] = {
            "shape": {"type": "rect", "width": 0.375, "height": 0.375},
            "id": data["nodes"][i]["id"],
        }

    json.dump(data, open(f"{args.output}", "w"))


if __name__ == "__main__":
    main()
