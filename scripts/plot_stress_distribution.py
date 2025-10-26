import argparse
import csv

import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(
        description="Plot stress value distribution from CSV files"
    )
    parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="Paths to input CSV files containing stress values",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        required=True,
        help="Labels for each input file (e.g., method names)",
    )
    parser.add_argument("--output", required=True, help="Path to output image file")
    parser.add_argument(
        "--bins",
        type=int,
        default=50,
        help="Number of bins for histogram (default: 50)",
    )
    parser.add_argument(
        "--log-scale", action="store_true", help="Use logarithmic scale for y-axis"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.6,
        help="Transparency of histograms (default: 0.6)",
    )
    args = parser.parse_args()

    if len(args.inputs) != len(args.labels):
        parser.error("Number of input files must match number of labels")

    # Read stress values from each CSV file
    all_stress_values = []
    ss = []
    for input_file, label in zip(args.inputs, args.labels):
        stress_values = []
        with open(input_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                stress_values.append(float(row["stress_value"]))
                ss.append((float(row["stress_value"]), label))
        all_stress_values.append((label, stress_values))
        print(f"{label}: {len(stress_values)} node pairs")

    # Calculate the maximum stress value across all datasets
    max_stress = max(max(values) for _, values in all_stress_values)
    print(f"Maximum stress value across all datasets: {max_stress:.4f}")
    ss.sort(key=lambda x: x[0])
    print(ss[-10:])
    # Create histogram with consistent bin range
    plt.figure(figsize=(12, 6))

    # all_stress_values.sort(key=lambda x: sum(x[1]) / len(x[1]))  # Sort by average stress value
    # Extract just the stress values for grouped histogram
    stress_data = [values for _, values in all_stress_values]
    labels = [label for label, _ in all_stress_values]

    # Create grouped histogram
    plt.hist(
        stress_data,
        bins=args.bins,
        range=(0, max_stress),
        alpha=args.alpha,
        label=labels,
        edgecolor="black",
        linewidth=0.5,
    )

    plt.xlabel("Stress Value", fontsize=12)

    if args.log_scale:
        plt.ylabel("Frequency (log scale)", fontsize=12)
        plt.yscale("log")
    else:
        plt.ylabel("Frequency", fontsize=12)

    plt.title("Distribution of Stress Values per Node Pair", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)

    # Set more detailed x-axis ticks
    ax = plt.gca()
    ax.xaxis.set_major_locator(plt.MaxNLocator(nbins=20))
    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()
    plt.savefig(args.output, dpi=300, bbox_inches="tight")
    print(f"Plot saved to {args.output}")


if __name__ == "__main__":
    main()
